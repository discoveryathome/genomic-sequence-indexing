"""Computational string-index adapters. No biological-effect inference."""
from pathlib import Path
import ctypes as C
import hashlib
import json
import sys
import time
import numpy as np
from trial import ROOT, encode, revcomp


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def libraries():
    lib = C.CDLL(str(ROOT/'build/cache.dylib'))
    lib.load_index.argtypes = [C.c_char_p, C.c_int]
    lib.load_index.restype = C.c_void_p
    lib.load_cached.argtypes = [C.c_char_p, C.c_char_p, C.c_int]
    lib.load_cached.restype = C.c_void_p
    lib.save_table.argtypes = [C.c_void_p, C.c_char_p]
    lib.save_table.restype = C.c_int
    lib.close_index.argtypes = [C.c_void_p]
    lib.count_batch.argtypes = [C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t,C.c_int,C.c_int,C.c_void_p]
    lib.count_batch.restype = C.c_uint64
    sa = C.CDLL(str(ROOT/'build/suffix_array.dylib'))
    sa.sa_build.argtypes = [C.c_void_p,C.c_int32,C.c_char_p]
    sa.sa_build.restype = C.c_int
    sa.sa_load.argtypes = [C.c_char_p]
    sa.sa_load.restype = C.c_void_p
    sa.sa_close.argtypes = [C.c_void_p]
    sa.sa_batch.argtypes = [C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_size_t,C.c_int,C.c_void_p]
    sa.sa_batch.restype = C.c_uint64
    return lib, sa


def create_cache(index, table, libs, seed=8):
    lib = libs[0]
    table = Path(table)
    p = lib.load_index(str(index).encode(), seed)
    if not p:
        raise ValueError('Cannot build index cache')
    try:
        if lib.save_table(p, str(table).encode()):
            raise ValueError('Cannot save index cache')
    finally:
        lib.close_index(p)
    meta = {'format':'dah-suffix-cache-v1','seed':seed,'byteorder':sys.byteorder,
            'uint64_bytes':8,'index_sha256':digest(index),'table_sha256':digest(table),
            'table_bytes':table.stat().st_size}
    table.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta


def validate_cache(index, table):
    table = Path(table)
    meta = json.loads(table.with_suffix('.json').read_text())
    if meta['format'] != 'dah-suffix-cache-v1' or meta['byteorder'] != sys.byteorder or meta['uint64_bytes'] != 8:
        raise ValueError('Cache format/ABI mismatch')
    if type(meta['seed']) is not int or not 1 <= meta['seed'] <= 8:
        raise ValueError('Invalid suffix length')
    if table.stat().st_size != 24+16*(4**meta['seed']) or table.stat().st_size != meta['table_bytes']:
        raise ValueError('Cache length mismatch')
    if digest(index) != meta['index_sha256'] or digest(table) != meta['table_sha256']:
        raise ValueError('Cache/index hash mismatch')
    return meta


def load(method, index, table, sapath, libs):
    if method not in ('rank2a','rank2a_AA','rebuilt8','persisted8','suffix_array'):
        raise ValueError('Unknown index method')
    lib, sa = libs
    if method == 'suffix_array':
        p = sa.sa_load(str(sapath).encode())
    elif method == 'persisted8':
        meta = validate_cache(index, table)
        p = lib.load_cached(str(index).encode(), str(table).encode(), meta['seed'])
    else:
        p = lib.load_index(str(index).encode(), 8 if method == 'rebuilt8' else 0)
    if not p:
        raise ValueError('Native index load failed')
    return p


def close(method, pointer, libs):
    (libs[1].sa_close if method == 'suffix_array' else libs[0].close_index)(pointer)


def evaluate(method, pointer, enc, libs, reps=1):
    data, offsets, lens = enc
    out = np.empty(len(lens),dtype=np.uint64)
    start = time.perf_counter()
    common = (pointer,data.ctypes.data,offsets.ctypes.data,lens.ctypes.data,len(lens))
    if method == 'suffix_array':
        libs[1].sa_batch(*common,reps,out.ctypes.data)
    else:
        libs[0].count_batch(*common,0,reps,out.ctypes.data)
    return out,(time.perf_counter()-start)/(len(lens)*reps)


def build_sa(seqs, path, libs):
    # 0 is a boundary symbol; A/C/G/T/N are 1..5, so queries cannot cross it.
    text = bytearray()
    mapping = str.maketrans({'A':chr(1),'C':chr(2),'G':chr(3),'T':chr(4),'N':chr(5)})
    for s in seqs:
        for strand in (s,revcomp(s)):
            text.extend(strand.translate(mapping).encode('ascii'))
            text.append(0)
    if len(text) >= 2**31:
        raise ValueError('32-bit suffix-array control limit exceeded')
    a = np.frombuffer(text,dtype=np.uint8)
    if libs[1].sa_build(a.ctypes.data,len(a),str(path).encode()):
        raise ValueError('Suffix-array construction failed')
