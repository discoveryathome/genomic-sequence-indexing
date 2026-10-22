from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'research/sources.json').read_text())['sources'][0]
p=root/'vendor/ropebwt3'
if not (p/'.git').exists():
 subprocess.run(['git','clone',s['url'],str(p)],check=True)
 subprocess.run(['git','checkout','--detach',s['commit']],cwd=p,check=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()==s['commit'], 'Existing upstream checkout differs from pinned commit'
subprocess.run(['git','diff','--exit-code','HEAD'],cwd=p,check=True)
