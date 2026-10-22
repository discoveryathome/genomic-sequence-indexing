"""Separate witness checker: exact literal counts, source binding, both strands."""
from pathlib import Path
import argparse, hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]

def check(certificate):
    obj=json.loads(Path(certificate).read_text())
    p=(ROOT/obj['dataset']).resolve()
    if not p.is_relative_to(ROOT/'data'):
        raise ValueError('Dataset must be under data/')
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=obj['dataset_sha256']:
        raise ValueError('Dataset identity mismatch')
    sequences=[];parts=[]
    for line in raw.decode().splitlines():
        if line.startswith('>'):
            if parts:sequences.append(''.join(parts).upper());parts=[]
        else:parts.append(line.strip())
    if parts:sequences.append(''.join(parts).upper())
    if not sequences or any(set(s)-set('ACGTN') for s in sequences):
        raise ValueError('Invalid reference alphabet')
    texts=[]
    for s in sequences:texts.extend([s,s.translate(str.maketrans('ACGTN','TGCAN'))[::-1]])
    if not obj['queries']:raise ValueError('Empty certificate')
    for item in obj['queries']:
        q=item['sequence']
        if not q or set(q)-set('ACGTN') or type(item['count']) is not int or item['count']<0:
            raise ValueError('Invalid literal query/count')
        pattern=re.compile('(?='+q+')')
        expected=sum(text.count(q) if len(q)==1 else sum(1 for _ in pattern.finditer(text)) for text in texts)
        if item['count']!=expected:raise ValueError(('Count mismatch',q,item['count'],expected))
    return {'passed':True,'queries':len(obj['queries']),'dataset_sha256':obj['dataset_sha256']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('certificate');args=parser.parse_args()
    print(json.dumps(check(args.certificate)))
