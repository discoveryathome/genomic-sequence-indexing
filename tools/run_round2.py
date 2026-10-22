"""Frozen round-two exact-string workloads and total-cost measurements."""
from pathlib import Path
import argparse, json, math, os, platform, random, statistics, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from trial import read_fasta, revcomp, oracle, encode
from round2_index import libraries, create_cache, build_sa, load, close, evaluate, digest
DEST=ROOT/'research/round2'
METHODS=['rank2a','rank2a_AA','rebuilt8','persisted8','suffix_array']
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def workload(seqs,seed):
    rng=random.Random(seed);out=[]
    for i in range(240):
        length=[20,31,75,150][i%4]
        text=rng.choice(seqs);pos=rng.randrange(len(text)-length+1)
        q=text[pos:pos+length]
        if i%3==0:q=''.join(rng.choices('ACGT',k=length))
        elif i%3==1:q=revcomp(q)
        out.append({'sequence':q,'group':'long'})
    for i in range(80):
        length=[1,4,7,8,9][i%5];text=rng.choice(seqs);pos=rng.randrange(len(text)-length+1)
        out.append({'sequence':text[pos:pos+length],'group':'short'})
    for q in ['N','NN','NACGT','ACGT','ATAT','A'*20,'C'*31]+[a[-10:]+b[:10] for a,b in zip(seqs,seqs[1:])]:
        out.append({'sequence':q,'group':'controls'})
    texts=[strand for s in seqs for strand in (s,revcomp(s))]
    for q in out:
        needle=q['sequence'];total=0
        for text in texts:
            if len(needle)==1:
                total+=text.count(needle)
                continue
            pos=0
            while True:
                pos=text.find(needle,pos)
                if pos<0:break
                total+=1;pos+=1
        q['count']=total
    return out

def prepare():
    libs=libraries();build=ROOT/'build/round2';build.mkdir(exist_ok=True)
    sources=json.loads((DEST/'data-sources.json').read_text())
    configs=[('ecoli','data/development_ecoli.fasta','development')]
    eligible=[];excluded=[]
    for source in sources:
        if source['status']!='downloaded':continue
        try:read_fasta(ROOT/source['path'])
        except AssertionError:
            excluded.append({'accession':source['accession'],'source_sha256':source['sha256'],
                             'reason':'Outside declared literal A/C/G/T/N alphabet; retained raw, not silently normalized'})
        else:eligible.append(source)
    save(DEST/'excluded-inputs.json',excluded)
    configs += [(s['accession'],s['path'],'fresh-corpus') for s in eligible]
    configs += [('repetitive','data/heldout_derived_panel.fasta','exposed-stress')]
    # A pooled set extends the original 2–5 Mb tests to ~17 Mb of independent references.
    pooled=ROOT/'data/round2/pooled-supported.fasta'
    pooled.write_bytes(b''.join((ROOT/s['path']).read_bytes()+b'\n' for s in eligible))
    configs += [('pooled','data/round2/pooled-supported.fasta','fresh-corpora-pooled')]
    records=[]
    for i,(name,data,split) in enumerate(configs):
        print('prepare',name,flush=True)
        existing=DEST/(name+'-case.json')
        if existing.exists():
            record=json.loads(existing.read_text())
            assert digest(ROOT/data)==record['dataset_sha256']
            records.append(record)
            continue
        seqs=read_fasta(ROOT/data);index=build/(name+'.fmd');table=build/(name+'.cache');sa=build/(name+'.sa')
        start=time.perf_counter()
        cmd=[str(ROOT/'vendor/ropebwt3/ropebwt3'),'build','-t1','-d','-o',str(index),str(ROOT/data)]
        result=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (DEST/(name+'-build.log')).write_text(result.stdout+result.stderr)
        index_seconds=time.perf_counter()-start
        start=time.perf_counter();meta=create_cache(index,table,libs);cache_seconds=time.perf_counter()-start
        start=time.perf_counter();build_sa(seqs,sa,libs);sa_seconds=time.perf_counter()-start
        record={'name':name,'split':split,'dataset':data,'dataset_sha256':digest(ROOT/data),
                'bases':sum(map(len,seqs)),'contigs':len(seqs),'query_seed':2026102300+i,
                'index':str(index.relative_to(ROOT)),'table':str(table.relative_to(ROOT)),
                'suffix_array':str(sa.relative_to(ROOT)),
                'construction':{'ropebwt_seconds':index_seconds,'table_seconds':cache_seconds,'suffix_array_seconds':sa_seconds},
                'bytes':{'ropebwt':index.stat().st_size,'table':table.stat().st_size,'suffix_array':sa.stat().st_size},
                'cache_metadata':meta,'queries':workload(seqs,2026102300+i)}
        save(DEST/(name+'-case.json'),record);records.append(record)
    save(DEST/'cases.json',[str((DEST/(r['name']+'-case.json')).relative_to(ROOT)) for r in records])

def benchmark():
    if (DEST/'trial.json').exists():raise SystemExit('Frozen result exists; use a fresh checkout/package')
    rng=random.Random(20261023);libs=libraries();records=[]
    for cp in json.loads((DEST/'cases.json').read_text()):
        case=json.loads((ROOT/cp).read_text());name=case['name'];print('measure',name,flush=True)
        warm={};ptrs={}
        try:
            for method in METHODS:
                ptrs[method]=load(method,ROOT/case['index'],ROOT/case['table'],ROOT/case['suffix_array'],libs)
            for group in ['long','short','controls']:
                qs=[q for q in case['queries'] if q['group']==group]
                enc=encode([q['sequence'] for q in qs]);expected=[q['count'] for q in qs]
                samples={m:[] for m in METHODS};reps=max(1,math.ceil(2000/len(qs)))
                for _ in range(7):
                    order=METHODS[:];rng.shuffle(order)
                    for method in order:
                        out,elapsed=evaluate(method,ptrs[method],enc,libs,reps)
                        assert out.tolist()==expected,(name,method,group)
                        samples[method].append(elapsed*1e6)
                warm[group]={'queries':len(qs),'reps_per_sample':reps,'samples_us':samples,
                             'median_us':{m:statistics.median(s) for m,s in samples.items()},
                             'paired_persisted_over_baseline':[a/b for a,b in zip(samples['persisted8'],samples['rank2a'])],
                             'paired_AA_over_baseline':[a/b for a,b in zip(samples['rank2a_AA'],samples['rank2a'])]}
        finally:
            for m,p in ptrs.items():close(m,p,libs)
        fresh=[]
        for count in [100,10000,100000]:
            for repeat in range(3):
                order=['rank2a','rebuilt8','persisted8','suffix_array'];rng.shuffle(order)
                for method in order:
                    start=time.perf_counter()
                    result=subprocess.run([sys.executable,'tools/round2_process.py',cp,method,str(count)],cwd=ROOT,capture_output=True,text=True)
                    if result.returncode:
                        (DEST/'process-failure.log').write_text(result.stdout+result.stderr)
                        raise RuntimeError('Fresh-process benchmark failed; see process-failure.log')
                    row=json.loads(result.stdout);row['external_wall_seconds']=time.perf_counter()-start;row['repeat']=repeat
                    fresh.append(row)
        record={'name':name,'case':cp,'warm':warm,'fresh_process':fresh,'load_average':os.getloadavg()}
        records.append(record);save(DEST/'measurements-progress.json',records)
        print('done',name,flush=True)
    result={'scope':'computational exact substring counting only','author_run':True,'external_review':False,
            'machine':platform.platform(),'cpu_count':os.cpu_count(),'datasets':records,
            'timing_limit':'Shared machine; unflushed OS filesystem cache; no production-workload claim'}
    save(DEST/'trial.json',result)
    print('round two complete',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--measure',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    if a.measure:benchmark()
