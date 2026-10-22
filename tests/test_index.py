import sys,subprocess
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import trial
@pytest.fixture(scope='module')
def fixture(tmp_path_factory):
    p=tmp_path_factory.mktemp('index');fa=p/'test.fa';idx=p/'test.fmd'
    seqs=['AAAAACGTNAC','GTAAAAC','NNACGTACGT'];fa.write_text(''.join(f'>s{i}\n{s}\n' for i,s in enumerate(seqs)))
    subprocess.run([str(trial.ROOT/'vendor/ropebwt3/ropebwt3'),'build','-t1','-d','-o',str(idx),str(fa)],capture_output=True,check=True)
    return trial.libload(),seqs,idx
@pytest.mark.parametrize('seed',[0,4,6,8])
def test_counts_strands_overlap_boundaries_and_absent(fixture,seed):
    lib,seqs,idx=fixture;p=lib.load_index(str(idx).encode(),seed);assert p
    qs=['A','AA','AAA','AAAA','AAAAA','ACGT','N','NN','NAC','ACGTACGT','ACGTAAAAC','C'*30,'GTAAAA']
    try:
        expected=[trial.oracle(seqs,q) for q in qs]
        for mode in [0,1]:assert trial.evaluate(lib,p,trial.encode(qs),mode)[0].tolist()==expected
    finally:lib.close_index(p)
def test_oracle_overlap():assert trial.oracle(['AAAA'],'AA')==3
def test_literal_n():assert trial.oracle(['ACNT'],'N')==2
