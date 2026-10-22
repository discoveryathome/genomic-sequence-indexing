"""Fresh-process measurement; OS filesystem cache is deliberately not flushed."""
import time
START = time.perf_counter()
from pathlib import Path
import argparse, json, resource, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from trial import encode
from round2_index import libraries, load, close, evaluate
p=argparse.ArgumentParser()
p.add_argument('case');p.add_argument('method');p.add_argument('count',type=int)
a=p.parse_args()
case=json.loads(Path(a.case).read_text())
qs=[q['sequence'] for q in case['queries']]
qs=(qs*((a.count+len(qs)-1)//len(qs)))[:a.count]
enc=encode(qs);libs=libraries();prepared=time.perf_counter()
ptr=load(a.method,ROOT/case['index'],ROOT/case['table'],ROOT/case['suffix_array'],libs)
loaded=time.perf_counter()
out,per_query=evaluate(a.method,ptr,enc,libs)
finished=time.perf_counter()
expected=[q['count'] for q in case['queries']]
expected=(expected*((a.count+len(expected)-1)//len(expected)))[:a.count]
assert out.tolist()==expected
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
close(a.method,ptr,libs)
print(json.dumps({'method':a.method,'count':a.count,'load_seconds':loaded-prepared,
 'query_seconds':per_query*a.count,'load_plus_query_seconds':finished-prepared,
 'input_import_seconds':prepared-START,'total_instrumented_seconds':finished-START,
 'peak_rss_bytes':int(rss if sys.platform=='darwin' else rss*1024),
 'mismatches':0,'filesystem_cache':'unflushed; fresh process only'}))
