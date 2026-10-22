from pathlib import Path
import argparse,json,sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from trial import read_fasta,oracle
p=argparse.ArgumentParser();p.add_argument('candidate');a=p.parse_args();r=json.loads(Path(a.candidate).read_text())
assert r['dataset'] in ('development_ecoli','heldout_bsubtilis','heldout_derived_panel')
s=read_fasta(root/f'data/{r["dataset"]}.fasta');assert r['queries'],'Empty certificate'
for q in r['queries']:
 assert q['sequence'] and set(q['sequence'])<=set('ACGTN'),'Queries must be nonempty literal DNA'
 assert type(q['count']) is int and q['count']>=0
 expected=oracle(s,q['sequence']);assert q['count']==expected,('Wrong both-strand overlapping count',q,expected)
print(f'PASS: {len(r["queries"])} exact count witnesses; literal N, both indexed strands, no cross-contig matches')
