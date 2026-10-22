from pathlib import Path
import argparse,json,random
p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=42);a=p.parse_args()
root=Path(__file__).resolve().parents[1];catalog=json.loads((root/'discover/catalog.json').read_text());r=random.Random(a.seed)
t=r.choices(catalog['tracks'],weights=[t['weight'] for t in catalog['tracks']])[0]
print(json.dumps({'intake':'open','track':t['id'],'task':r.choice(t['tasks'])},indent=2))
