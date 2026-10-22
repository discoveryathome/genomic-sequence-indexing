"""Reconstruct ignored native artifacts without rewriting frozen research evidence."""
from pathlib import Path
import argparse, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from trial import read_fasta
from round2_index import libraries, create_cache, build_sa, digest

def rebuild(case, with_sa=False):
    data=ROOT/case['dataset'];index=ROOT/case['index'];table=ROOT/case['table'];sa=ROOT/case['suffix_array']
    assert digest(data)==case['dataset_sha256'],'Source mismatch'
    index.parent.mkdir(exist_ok=True,parents=True)
    if not index.exists():
        subprocess.run([str(ROOT/'vendor/ropebwt3/ropebwt3'),'build','-t1','-d','-o',str(index),str(data)],check=True,capture_output=True)
    libs=libraries()
    if not table.exists():create_cache(index,table,libs)
    if with_sa and not sa.exists():build_sa(read_fasta(data),sa,libs)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case');p.add_argument('--with-sa',action='store_true');a=p.parse_args()
    paths=[a.case] if a.case else json.loads((ROOT/'research/round2/cases.json').read_text())
    for path in paths:
        case=json.loads((ROOT/path).read_text());rebuild(case,a.with_sa);print(case['name'],'rebuilt',flush=True)
