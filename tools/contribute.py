"""Bounded software-index trial with a source-bound certificate and all timings."""
from pathlib import Path
import argparse, json, random, statistics, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from trial import read_fasta, encode, queries
from round2_index import libraries, load, close, evaluate
from rebuild_round2 import rebuild
from verify_count import check

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',default='AL123456.3');p.add_argument('--seed',type=int,required=True)
    p.add_argument('--out',required=True);a=p.parse_args()
    dest=(ROOT/a.out).resolve()
    if not dest.is_relative_to(ROOT/'research') or dest.exists():raise SystemExit('Choose a new research/<session> directory')
    cases=[json.loads((ROOT/q).read_text()) for q in json.loads((ROOT/'research/round2/cases.json').read_text())]
    case=next((c for c in cases if c['name']==a.case),None)
    if case is None:raise SystemExit('Unknown case')
    start=time.perf_counter();rebuild(case);libs=libraries()
    qs=queries(read_fasta(ROOT/case['dataset']),a.seed,n=96);enc=encode(qs);methods=['rank2a','persisted8']
    ptrs={};values={};samples={m:[] for m in methods};rng=random.Random(a.seed)
    try:
        for m in methods:ptrs[m]=load(m,ROOT/case['index'],ROOT/case['table'],ROOT/case['suffix_array'],libs)
        for _ in range(5):
            order=methods[:];rng.shuffle(order)
            for m in order:
                out,t=evaluate(m,ptrs[m],enc,libs,reps=10);values[m]=out.tolist();samples[m].append(t)
    finally:
        for m,v in ptrs.items():close(m,v,libs)
    assert values['rank2a']==values['persisted8']
    dest.mkdir()
    cert={'dataset':case['dataset'],'dataset_sha256':case['dataset_sha256'],
          'queries':[{'sequence':q,'count':int(n)} for q,n in zip(qs,values['persisted8'])]}
    cp=dest/'candidate.json';cp.write_text(json.dumps(cert,indent=2)+'\n');verified=check(cp)
    handoff={'kind':'bounded author/contributor software-index replication','case':a.case,'seed':a.seed,
             'samples_seconds_per_query':samples,'median_seconds_per_query':{m:statistics.median(s) for m,s in samples.items()},
             'verified':verified,'elapsed_seconds':time.perf_counter()-start,'novelty_claim':False,
             'workload_limit':'Fresh generated queries on an exposed public corpus; warm throughput only',
             'contributor_provenance':'Fill in identity/model and prior involvement before review','scientific_review':'pending'}
    (dest/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n');print(json.dumps(handoff))
if __name__=='__main__':main()
