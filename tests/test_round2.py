import json
import itertools
import subprocess
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trial import ROOT, oracle, encode
from round2_index import libraries, create_cache, validate_cache, build_sa, load, evaluate, close

@pytest.fixture()
def fixture(tmp_path):
    seqs=['AAAACGTNAC','GTAAAAC','NNACGTACGT'];fa=tmp_path/'test.fa';index=tmp_path/'test.fmd'
    fa.write_text(''.join(f'>s{i}\n{s}\n' for i,s in enumerate(seqs)))
    subprocess.run([str(ROOT/'vendor/ropebwt3/ropebwt3'),'build','-t1','-d','-o',str(index),str(fa)],check=True,capture_output=True)
    libs=libraries();table=tmp_path/'table.cache';sa=tmp_path/'test.sa'
    create_cache(index,table,libs);build_sa(seqs,sa,libs)
    return seqs,index,table,sa,libs

def test_all_short_strings_and_long_boundaries(fixture):
    seqs,index,table,sa,libs=fixture
    qs=[''.join(q) for n in range(1,5) for q in itertools.product('ACGTN',repeat=n)]
    qs+=['AAAACGTNAC','ACGTNACGTAAAAC','ACGTACGT','ACGTACGTA','C'*20]
    expected=[oracle(seqs,q) for q in qs]
    for method in ['rank2a','rebuilt8','persisted8','suffix_array']:
        p=load(method,index,table,sa,libs)
        try:assert evaluate(method,p,encode(qs),libs)[0].tolist()==expected
        finally:close(method,p,libs)

def test_cache_wrong_hash_and_index(fixture):
    _,index,table,sa,libs=fixture
    raw=table.read_bytes();changed=bytearray(raw);changed[-1]^=1;table.write_bytes(changed)
    with pytest.raises(ValueError,match='hash'):validate_cache(index,table)
    table.write_bytes(raw)
    other=index.with_name('other.fmd');other.write_bytes(index.read_bytes()+b'x')
    with pytest.raises(ValueError,match='hash'):validate_cache(other,table)
    table.write_bytes(raw[:-1])
    with pytest.raises(ValueError,match='length'):validate_cache(index,table)
    assert not libs[0].load_cached(str(index).encode(),str(table).encode(),8)

def test_cache_abi_and_invalid_queries(fixture):
    _,index,table,sa,libs=fixture
    meta=table.with_suffix('.json');data=json.loads(meta.read_text());data['byteorder']='unsupported';meta.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='ABI'):validate_cache(index,table)
    for method in ['rank2a','suffix_array']:
        p=load(method,index,table,sa,libs)
        try:assert evaluate(method,p,encode(['']),libs)[0].tolist()==[2**64-1]
        finally:close(method,p,libs)

def test_separate_certificate_checker(tmp_path,monkeypatch):
    sys.path.insert(0,str(ROOT/'tools'))
    import verify_count
    import hashlib
    monkeypatch.setattr(verify_count,'ROOT',tmp_path)
    (tmp_path/'data').mkdir();fa=tmp_path/'data/tiny.fa';fa.write_text('>a\nAAAN\n>b\nCGT\n')
    cert={'dataset':'data/tiny.fa','dataset_sha256':hashlib.sha256(fa.read_bytes()).hexdigest(),
          'queries':[{'sequence':'AA','count':2},{'sequence':'N','count':2},{'sequence':'NCG','count':0}]}
    cp=tmp_path/'cert.json';cp.write_text(json.dumps(cert));assert verify_count.check(cp)['passed']
    cert['queries'][0]['count']=3;cp.write_text(json.dumps(cert))
    with pytest.raises(ValueError,match='Count mismatch'):verify_count.check(cp)
    cert['dataset_sha256']='0'*64;cp.write_text(json.dumps(cert))
    with pytest.raises(ValueError,match='identity'):verify_count.check(cp)
