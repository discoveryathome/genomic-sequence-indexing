from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from jsonschema import Draft202012Validator,FormatChecker
root=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--quick',action='store_true');args=a.parse_args()
for name,path in [('manifest','discover.json'),('catalog','discover/catalog.json'),('frontier','discover/frontier.json')]:
 schema=json.loads((root/f'spec/{name}.schema.json').read_text());Draft202012Validator(schema,format_checker=FormatChecker()).validate(json.loads((root/path).read_text()))
for p,h in json.loads((root/'research/manifest.json').read_text())['sha256'].items():
 assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h, f'Changed frozen artifact: {p}'
assert json.loads((root/'discover.json').read_text())['review']['paused'] is False
for item in json.loads((root/'discover/frontier.json').read_text())['artifacts']:
 assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256'], 'Frontier binding mismatch'
if 'commit' in json.loads((root/'research/sources.json').read_text())['sources'][0]:
 assert (root/'vendor/ropebwt3/.git').exists(), 'Run tools/setup.sh to fetch pinned upstream'
 src=json.loads((root/'research/sources.json').read_text())['sources'][0]
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root/'vendor/ropebwt3',text=True).strip()==src['commit']
 subprocess.run(['git','diff','--exit-code','HEAD'],cwd=root/'vendor/ropebwt3',check=True,capture_output=True)
if not args.quick:subprocess.run([sys.executable,'-m','pytest','-q','tests'],cwd=root,check=True)
print('PASS: schemas and frozen artifacts; intake open; scientific review pending')

# Preserve prior package identities across explicit onboarding/frontier migrations.
import sys
root=Path(__file__).resolve().parents[1]
prior=root/'research/distribution-prep-20261022'
for path,h in json.loads((prior/'prior-manifest.json').read_text())['sha256'].items():
 assert any(f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==h for f in [root/path,prior/'prior-files'/path]),('historical',path)
