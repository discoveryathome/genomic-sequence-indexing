from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def test_certificate_positive_and_negative(tmp_path):
 p=ROOT/'results/example-candidate.json'
 subprocess.run([sys.executable,'tools/verify_candidate.py',str(p)],cwd=ROOT,check=True,capture_output=True)
 r=json.loads(p.read_text())
 if 'queries' in r:r['queries'][0]['count']+=1
 elif 'order' in r:r['cases'][0]['y_hex']='0x1.0p+8'
 else:r['cases'][0]['sign']=-r['cases'][0]['sign']
 q=tmp_path/'bad.json';q.write_text(json.dumps(r))
 assert subprocess.run([sys.executable,'tools/verify_candidate.py',str(q)],cwd=ROOT,capture_output=True).returncode!=0
