"""Second compressed-index calibration with identical exact-string semantics."""
from pathlib import Path
import argparse,ctypes as C,hashlib,json,os,platform,random,statistics,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from trial import read_fasta,revcomp,oracle,queries,encode
from round2_index import libraries,load,close,evaluate
from rebuild_round2 import rebuild

def libload():
    lib=C.CDLL(str(ROOT/'build/sdsl.dylib'))
    lib.fm_build.argtypes=[C.c_void_p,C.c_size_t,C.c_char_p];lib.fm_build.restype=C.c_int
    lib.fm_load.argtypes=[C.c_char_p];lib.fm_load.restype=C.c_void_p
    lib.fm_close.argtypes=[C.c_void_p]
    lib.fm_batch.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t,C.c_int,C.c_void_p];lib.fm_batch.restype=C.c_uint64
    return lib

def build(lib,seqs,path):
    chars={'A':1,'C':2,'G':3,'T':4,'N':5}
    text=bytearray()
    for seq in seqs:
        for strand in (seq,revcomp(seq)):
            text.extend(chars[c] for c in strand);text.append(6)
    a=np.frombuffer(text,dtype=np.uint8);t=time.perf_counter()
    if lib.fm_build(a.ctypes.data,len(a),str(path).encode()):raise ValueError('SDSL construction failed')
    return {'construct_seconds':time.perf_counter()-t,'index_bytes':path.stat().st_size,'text_sha256':hashlib.sha256(text).hexdigest()}

def query(lib,ptr,enc,reps=1):
    data,offsets,lengths=enc;out=np.empty(len(lengths),dtype=np.uint64);t=time.perf_counter()
    lib.fm_batch(ptr,data.ctypes.data,offsets.ctypes.data,lengths.ctypes.data,len(lengths),reps,out.ctypes.data)
    return out,(time.perf_counter()-t)/(len(lengths)*reps)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();dest=(ROOT/a.out).resolve()
    if dest.exists() or not dest.is_relative_to(ROOT/'research'):p.error('Choose a new research directory')
    dest.mkdir(parents=True);lib=libload();tiny=['AAC','GTT','AANNA','AAAA']
    control=['A','AA','N','NN','CG','ACGT','ATAT','C'*31]
    index=ROOT/'build/distribution-control.fm';build(lib,tiny,index);ptr=lib.fm_load(str(index).encode());assert ptr
    try:
        actual,_=query(lib,ptr,encode(control));expected=[oracle(tiny,q) for q in control];assert actual.tolist()==expected
    finally:lib.fm_close(ptr)
    case=json.loads((ROOT/'research/round2/AL123456.3-case.json').read_text());rebuild(case);seqs=read_fasta(ROOT/case['dataset'])
    qs=queries(seqs,221043,n=96)+[seqs[0][:n] for n in (1,4,7,8,9)]
    expected=[oracle(seqs,q) for q in qs];enc=encode(qs)
    certificate={'dataset':case['dataset'],'dataset_sha256':case['dataset_sha256'],
                 'queries':[{'sequence':q,'count':c} for q,c in zip(qs,expected)]}
    (dest/'candidate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    index=ROOT/'build/distribution-AL123456.fm';construction=build(lib,seqs,index);libs=libraries()
    names=['rank2a','rank2a_AA','persisted8','sdsl'];ptrs={};loads={n:[] for n in names};samples={n:[] for n in names};rng=random.Random(221043)
    def get(n):return lib.fm_load(str(index).encode()) if n=='sdsl' else load(n,ROOT/case['index'],ROOT/case['table'],ROOT/case['suffix_array'],libs)
    def free(n,ptr):return lib.fm_close(ptr) if n=='sdsl' else close(n,ptr,libs)
    # Repeated warm-process loads include persisted cache identity hashing.
    for _ in range(7):
        order=names[:];rng.shuffle(order)
        for n in order:
            t=time.perf_counter();ptr=get(n);assert ptr;loads[n].append(time.perf_counter()-t);free(n,ptr)
    try:
        ptrs={n:get(n) for n in names};assert all(ptrs.values())
        for _ in range(7):
            order=names[:];rng.shuffle(order)
            for n in order:
                out,t=query(lib,ptrs[n],enc,100) if n=='sdsl' else evaluate(n,ptrs[n],enc,libs,reps=100)
                assert out.tolist()==expected,(n,out.tolist(),expected);samples[n].append(t)
    finally:
        for n,ptr in ptrs.items():free(n,ptr)
    sizes={'rank2a':(ROOT/case['index']).stat().st_size,'persisted8':(ROOT/case['index']).stat().st_size+(ROOT/case['table']).stat().st_size,'sdsl':index.stat().st_size}
    delta_load=statistics.median(loads['persisted8'])-statistics.median(loads['rank2a'])
    delta_query=statistics.median(samples['rank2a'])-statistics.median(samples['persisted8'])
    report={'kind':'exposed author-run compressed-index calibration','platform':platform.platform(),'load_average':os.getloadavg(),
            'configuration':'SDSL 2.1.1 csa_wt<wt_huff<rrr_vector<63>>,32,64>','construction':construction,
            'semantic_controls':dict(zip(control,expected[:0])) if False else {'queries':control,'counts':[oracle(tiny,q) for q in control]},
            'corpus':case['dataset'],'corpus_sha256':case['dataset_sha256'],'queries':len(qs),'all_counts_match':True,
            'query_seconds':samples,'warm_load_seconds':loads,'serialized_bytes':sizes,
            'estimated_persisted_break_even_queries':max(0,delta_load/delta_query) if delta_query>0 else None,
            'estimated_batch_seconds':{n:{str(batch):statistics.median(loads[n])+batch*statistics.median(samples[n]) for batch in [1,100,10000,100000]} for n in names},
            'limitations':['One exposed corpus, fixed untuned SDSL configuration','Generated probes, not real application query traces','Batch costs are component estimates, not fresh-process measurements','SDSL loaded-index checksum validation not charged; persisted8 checksum validation charged','No independent review or quiet-machine performance claim'],
            'sources_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['tools/compare_sdsl.py','tools/build_sdsl.py','research/distribution-prep-20261022/sdsl_adapter.cpp']}}
    (dest/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
