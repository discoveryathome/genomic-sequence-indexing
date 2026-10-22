"""Exact count-query trial against native Ropebwt3 rank functions."""
from pathlib import Path
import argparse,ctypes as C,hashlib,json,platform,random,statistics,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
CONFIGS=[{'name':'rank2a','seed':0,'mode':0},{'name':'rank21','seed':0,'mode':1}]+[{'name':f'suffix{k}','seed':k,'mode':1} for k in [4,6,8]]

def read_fasta(p):
    seqs=[];parts=[]
    for line in p.read_text().splitlines():
        if line.startswith('>'):
            if parts:seqs.append(''.join(parts).upper());parts=[]
        else:parts.append(line.strip())
    if parts:seqs.append(''.join(parts).upper())
    assert seqs and all(set(s)<=set('ACGTN') for s in seqs);return seqs

def revcomp(s):return s.translate(str.maketrans('ACGTN','TGCAN'))[::-1]

def oracle(seqs,q):
    # Literal N; overlapping hits; forward and reverse-complement indexed separately.
    count=0
    for s in seqs:
        for text in [s,revcomp(s)]:
            start=0
            while True:
                i=text.find(q,start)
                if i<0:break
                count+=1;start=i+1
    return count

def queries(seqs,seed,n=480):
    r=random.Random(seed);out=[]
    for i in range(n):
        size=[20,31,75,150][i%4];s=r.choice(seqs);pos=r.randrange(len(s)-size+1);q=s[pos:pos+size]
        if i%3==0:q=''.join(r.choices('ACGT',k=size))
        elif i%3==1:q=revcomp(q)
        out.append(q)
    out+=['N','NN','NACGT','A'*20,'C'*31,'ACGT'*8]
    out += [a[-10:]+b[:10] for a,b in zip(seqs,seqs[1:])]
    return out

def libload():
    lib=C.CDLL(str(ROOT/'build/count.dylib'))
    lib.load_index.argtypes=[C.c_char_p,C.c_int];lib.load_index.restype=C.c_void_p
    lib.close_index.argtypes=[C.c_void_p]
    lib.count_batch.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t,C.c_int,C.c_int,C.c_void_p];lib.count_batch.restype=C.c_uint64
    return lib

def encode(qs):
    lens=np.array(list(map(len,qs)),dtype=np.int32);off=np.r_[0,np.cumsum(lens)[:-1]].astype(np.int32)
    data=np.array([{'A':1,'C':2,'G':3,'T':4,'N':5}[c] for q in qs for c in q],dtype=np.uint8)
    return data,off,lens

def evaluate(lib,p,encoded,mode,reps=1):
    data,off,lens=encoded;out=np.empty(len(lens),dtype=np.uint64);t=time.perf_counter()
    lib.count_batch(p,data.ctypes.data,off.ctypes.data,lens.ctypes.data,len(lens),mode,reps,out.ctypes.data)
    return out,(time.perf_counter()-t)/(len(lens)*reps)*1e6

def prep():
    a=read_fasta(ROOT/'data/U00096.3.fasta')[0];b=read_fasta(ROOT/'data/AL009126.3.fasta')[0]
    r=random.Random(2026102223);panel=[]
    for k in range(8):
        seq=list(a[100000:350000])
        for i in r.sample(range(len(seq)),1250):seq[i]=r.choice([x for x in 'ACGT' if x!=seq[i]])
        panel.append(''.join(seq))
    panel+=['A'*300+'N'*20+'ACGT'*100,'G'*40+'ACAT'*100]
    datasets={'development_ecoli':[a],'heldout_bsubtilis':[b],'heldout_derived_panel':panel}
    for name,seqs in datasets.items():
        path=ROOT/f'data/{name}.fasta';path.write_text(''.join(f'>contig{i}\n{s}\n' for i,s in enumerate(seqs)))
    return datasets

def build_index(name):
    t=time.perf_counter();p=subprocess.run([str(ROOT/'vendor/ropebwt3/ropebwt3'),'build','-t1','-d','-o',str(ROOT/f'build/{name}.fmd'),str(ROOT/f'data/{name}.fasta')],capture_output=True,text=True,check=True)
    (ROOT/f'results/{name}-build.log').write_text(p.stderr)
    return {'wall_seconds':time.perf_counter()-t,'index_bytes':(ROOT/f'build/{name}.fmd').stat().st_size}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');args=ap.parse_args();start=time.time()
    subprocess.run(['sh','tools/build.sh'],cwd=ROOT,check=True,capture_output=True)
    lib=libload();sets=prep();rows={};selected=None;strong=None;rng=random.Random(122)
    for d,(name,seqs) in enumerate(sets.items()):
        print('dataset',name,flush=True)
        build=build_index(name);qs=queries(seqs,2026102220+d);enc=encode(qs)
        (ROOT/f'data/{name}-queries.json').write_text(json.dumps(qs)+'\n')
        # Independent direct-string oracle, all cases, all strands, contig boundaries.
        expected=np.array([oracle(seqs,q) for q in qs],dtype=np.uint64)
        (ROOT/f'data/{name}-expected.json').write_text(json.dumps(expected.tolist())+'\n')
        pointers={};stats=[]
        try:
            for cfg in CONFIGS:
                t=time.perf_counter();p=lib.load_index(str(ROOT/f'build/{name}.fmd').encode(),cfg['seed']);init=time.perf_counter()-t
                assert p;pointers[cfg['name']]=p
                got,_=evaluate(lib,p,enc,cfg['mode']);bad=np.flatnonzero(got!=expected)
                assert len(bad)==0,(name,cfg,[(qs[i],int(expected[i]),int(got[i])) for i in bad[:5]])
                stats.append({**cfg,'mismatches':int(len(bad)),'queries':len(qs),'init_seconds':init,'suffix_table_bytes':16*(4**cfg['seed']) if cfg['seed'] else 0,'samples_us':[]})
            # Invalid queries are rejected, no empty-query convention silently inferred.
            invalid=(np.array([0],dtype=np.uint8),np.array([0],dtype=np.int32),np.array([1],dtype=np.int32))
            assert evaluate(lib,pointers['rank2a'],invalid,0)[0][0]==2**64-1
            if not args.verify_only:
                aa=[]
                for _ in range(9):
                    order=stats.copy()+[None];rng.shuffle(order)
                    for row in order:
                        if row is None:aa.append(evaluate(lib,pointers['rank21'],enc,1,10)[1])
                        else:row['samples_us'].append(evaluate(lib,pointers[row['name']],enc,row['mode'],10)[1])
                for row in stats:row['median_us']=statistics.median(row['samples_us'])
                if d==0:
                    strong=min(stats[:2],key=lambda x:x['median_us'])['name']
                    # Fixed memory ceiling 1 MiB; amortized throughput is selection objective.
                    selected=min(stats,key=lambda x:x['median_us'])['name']
                    (ROOT/'results/selection.json').write_text(json.dumps({'selected':selected,'strong_baseline':strong,'rule':'fastest development median; <=1 MiB suffix table; every query exact'},indent=2)+'\n')
            else:aa=[]
            rows[name]={'bases':sum(map(len,seqs)),'contigs':len(seqs),'both_strands':True,'build':build,'methods':stats,'rank21_AA_samples_us':aa}
        finally:
            for p in pointers.values():lib.close_index(p)
    if args.verify_only:
        print(json.dumps({'all_native_methods_match_direct_oracle':True,'queries':sum(r['methods'][0]['queries'] for r in rows.values())}));return
    result={'kind':'author-run bounded native-index trial','machine':platform.platform(),'elapsed_seconds':time.time()-start,'selected':selected,'strong_baseline':strong,'datasets':rows,'interpretation':'Known suffix-interval lookup, exact count only, no novelty or end-to-end read alignment claims; synthetic relatives are derived from one genome, not independent biological samples; index bytes exclude runtime allocations and suffix table is reported separately.'}
    (ROOT/'results/trial.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'selected':selected,'strong_baseline':strong,'elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
