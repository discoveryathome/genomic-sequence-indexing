"""Fixed fresh-process batch comparison; no stopping on wins or candidate tuning."""
from pathlib import Path
import argparse,hashlib,json,os,random,statistics,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();dest=(ROOT/a.out).resolve()
if dest.exists() or not dest.is_relative_to(ROOT/'research'):p.error('Choose a new research directory')
dest.mkdir(parents=True);rng=random.Random(221044)
case=json.loads((ROOT/'research/round2/AL123456.3-case.json').read_text())
panel=ROOT/'research/distribution-prep-20261022/sdsl-comparison/candidate.json'
case['queries']=json.loads(panel.read_text())['queries'];cp=dest/'case.json';cp.write_text(json.dumps(case,indent=2)+'\n')
rows=[]
for count in [1,100,10000,100000]:
    for repeat in range(3):
        methods=['rank2a','rank2a_AA','persisted8'];rng.shuffle(methods)
        for method in methods:
            start=time.perf_counter()
            result=subprocess.run([sys.executable,'tools/round2_process.py',str(cp),method,str(count)],cwd=ROOT,capture_output=True,text=True,timeout=120)
            (dest/f'{count}-{repeat}-{method}.log').write_text(result.stdout+result.stderr)
            if result.returncode:row={'status':'failed','returncode':result.returncode,'method':method,'count':count}
            else:row={'status':'verified',**json.loads(result.stdout)}
            row.update(repeat=repeat,external_wall_seconds=time.perf_counter()-start);rows.append(row)
    print(count,'complete',flush=True)
    report={'seed':221044,'panel_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'rows':rows,
            'load_average':os.getloadavg(),'claim':'Fresh processes with unflushed filesystem cache on one exposed generated workload; not a production trace.'}
    (dest/'results.json').write_text(json.dumps(report,indent=2)+'\n')
