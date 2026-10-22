"""One prespecified timing confirmation; no candidate tuning or stopping on wins."""
from pathlib import Path
import json, math, os, random, statistics, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from trial import encode
from round2_index import libraries, load, close, evaluate
DEST=ROOT/'research/round2/confirmation'
def main():
    if (DEST/'results.json').exists():raise SystemExit('Confirmation already completed')
    libs=libraries();rng=random.Random(2026102341);results=[]
    for name in ['AE006468.2','AE004091.2','AL123456.3','pooled']:
        cp='research/round2/'+name+'-case.json';case=json.loads((ROOT/cp).read_text());warm={};ptrs={}
        methods=['rank2a','rank2a_AA','persisted8'];load_before=os.getloadavg()
        try:
            for m in methods:ptrs[m]=load(m,ROOT/case['index'],ROOT/case['table'],ROOT/case['suffix_array'],libs)
            for group in ['long','short']:
                qs=[q for q in case['queries'] if q['group']==group];enc=encode([q['sequence'] for q in qs])
                samples={m:[] for m in methods};reps=math.ceil(2000/len(qs))
                for _ in range(7):
                    order=methods[:];rng.shuffle(order)
                    for m in order:
                        out,t=evaluate(m,ptrs[m],enc,libs,reps);assert out.tolist()==[q['count'] for q in qs]
                        samples[m].append(t*1e6)
                warm[group]={'samples_us':samples,'median_us':{m:statistics.median(v) for m,v in samples.items()}}
        finally:
            for m,v in ptrs.items():close(m,v,libs)
        fresh=[]
        for repeat in range(3):
            order=['rank2a','persisted8'];rng.shuffle(order)
            for m in order:
                start=time.perf_counter()
                p=subprocess.run([sys.executable,'tools/round2_process.py',cp,m,'100000'],cwd=ROOT,capture_output=True,text=True,check=True)
                row=json.loads(p.stdout);row['repeat']=repeat;row['external_wall_seconds']=time.perf_counter()-start;fresh.append(row)
        b=statistics.median(r['external_wall_seconds'] for r in fresh if r['method']=='rank2a')
        c=statistics.median(r['external_wall_seconds'] for r in fresh if r['method']=='persisted8')
        record={'name':name,'warm':warm,'fresh_process':fresh,'total_100k_reduction_percent':100*(1-c/b),
                'load_before':load_before,'load_after':os.getloadavg()}
        results.append(record);(DEST/'progress.json').write_text(json.dumps(results,indent=2)+'\n')
        print(name,record['total_100k_reduction_percent'],flush=True)
    (DEST/'results.json').write_text(json.dumps({'datasets':results,'author_run':True,'retuned':False,'new_holdout':False},indent=2)+'\n')
if __name__=='__main__':main()
