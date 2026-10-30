"""Exploration harness for the sv8 candidate: correctness controls, paired
timing against all round-two baselines, and a certificate for verify_count.py.
Computational exact-string counting only; no biological inference.

  python research/explore-singleton-verify-973e687a/sv_run.py check CASE
  python research/explore-singleton-verify-973e687a/sv_run.py time CASE SEED N ROUNDS OUT.json s:d [s:d ...]
  python research/explore-singleton-verify-973e687a/sv_run.py cert CASE SEED s:d OUTDIR
"""
from pathlib import Path
import ctypes as C, json, platform, random, statistics, sys, time
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'tools'))
from trial import read_fasta, encode, queries, revcomp, oracle
from round2_index import libraries, load, close, evaluate, digest
from rebuild_round2 import rebuild
from verify_count import check as witness

def case_of(name):
    for q in json.loads((ROOT / 'research/round2/cases.json').read_text()):
        c = json.loads((ROOT / q).read_text())
        if c['name'] == name:
            return c
    raise SystemExit('unknown case')

def svlib():
    lib = C.CDLL(str(ROOT / 'build' / __import__('os').environ.get('SV_LIB', 'sv.dylib')))
    lib.sv_load.argtypes = [C.c_char_p, C.c_char_p, C.c_int, C.c_int]; lib.sv_load.restype = C.c_void_p
    lib.sv_close.argtypes = [C.c_void_p]
    lib.sv_bytes.argtypes = [C.c_void_p]; lib.sv_bytes.restype = C.c_uint64
    lib.sv_sym.argtypes = [C.c_void_p, C.c_uint64]; lib.sv_sym.restype = C.c_int
    lib.sv_locate.argtypes = [C.c_void_p, C.c_uint64]; lib.sv_locate.restype = C.c_int64
    lib.sv_batch.argtypes = [C.c_void_p] * 4 + [C.c_size_t, C.c_int, C.c_void_p]; lib.sv_batch.restype = C.c_uint64
    return lib

def sv_open(lib, case, s, d):
    shift = {8: 3, 16: 4, 32: 5, 64: 6}[s]
    t = time.perf_counter()
    p = lib.sv_load(str(ROOT / case['index']).encode(), str(ROOT / case['table']).encode(), shift, d)
    if not p:
        raise ValueError('sv_load failed')
    return p, time.perf_counter() - t

def sv_eval(lib, p, enc, reps=1):
    data, off, lens = enc; out = np.empty(len(lens), dtype=np.uint64); t = time.perf_counter()
    lib.sv_batch(p, data.ctypes.data, off.ctypes.data, lens.ctypes.data, len(lens), reps, out.ctypes.data)
    return out, (time.perf_counter() - t) / (len(lens) * reps)

def stress(seqs, rng):
    """Queries aimed at the locate path, string ends, N runs and boundaries."""
    qs = []; texts = [t for s in seqs for t in (s, revcomp(s))]
    for t in texts:
        for L in (20, 31, 40, 75, 150):
            if len(t) < L + 2:
                continue
            for pos in [0, 1, 2, 15, 16, 17, 31, 32, 33, len(t) - L, len(t) - L - 1, len(t) - L - 16] + [rng.randrange(len(t) - L + 1) for _ in range(3)]:
                q = t[pos:pos + L]; qs.append(q)
                j = rng.randrange(min(6, L)); alt = rng.choice([x for x in 'ACGT' if x != q[j]])
                qs.append(q[:j] + alt + q[j + 1:])            # mismatch near the start (verified prefix)
                qs.append(q[:-1] + rng.choice('ACGT'))        # mismatch at the end (table region)
    for t in texts:                                           # windows overlapping literal N runs
        i = t.find('N')
        while i >= 0 and len(qs) < 20000:
            for L in (20, 40, 75):
                for start in (i - L + 1, i - L // 2, i - 3, i):
                    if 0 <= start and start + L <= len(t):
                        qs.append(t[start:start + L])
            i = t.find('N', i + 25)
    for a, b in zip(seqs, seqs[1:]):                          # contig-boundary crossers (expected 0)
        for k in (10, 20, 40, 70):
            qs += [a[-k:] + b[:k], revcomp(a[-k:] + b[:k])]
    return list(dict.fromkeys(q for q in qs if q))

def cmd_check(name):
    case = case_of(name); rebuild(case); libs = libraries(); lib = svlib()
    seqs = read_fasta(ROOT / case['dataset']); rng = random.Random(97368)
    report = {'case': name, 'configs': {}}
    base = load('persisted8', ROOT / case['index'], ROOT / case['table'], None, libs)
    try:
        qs = stress(seqs, rng) + queries(seqs, 2051343105, n=480); enc = encode(qs)
        ref, _ = evaluate('persisted8', base, enc, libs)
        sample = rng.sample(range(len(qs)), min(400, len(qs)))
        direct = {i: oracle(seqs, qs[i]) for i in sample}
        bad_ref = [i for i in sample if direct[i] != int(ref[i])]
        for s, d in [(8, 0), (16, 2), (16, 4), (32, 2), (32, 4), (64, 0)]:
            p, build_s = sv_open(lib, case, s, d)
            try:
                if 'text_reconstruction_ok' not in report:  # same text for every s, d
                    # Reconstructed strings must be exactly the indexed strands.
                    n = sum(2 * (len(x) + 1) for x in seqs); txt = []; cur = []
                    for x in range(n):
                        c = lib.sv_sym(p, x)
                        if c == 0:
                            txt.append(''.join(cur)); cur = []
                        else:
                            cur.append('?ACGTN'[c])
                    report['text_reconstruction_ok'] = sorted(txt) == sorted(t for x in seqs for t in (x, revcomp(x)))
                traced = hasattr(lib, 'sv_located')
                if traced:
                    C.c_uint64.in_dll(lib, 'sv_located').value = 0
                got, _ = sv_eval(lib, p, enc)
                mism = [(qs[i], int(ref[i]), int(got[i])) for i in np.flatnonzero(got != ref)[:10]]
                if traced:
                    report['configs'].setdefault('locate_calls', {})[f'{s}:{d}'] = C.c_uint64.in_dll(lib, 'sv_located').value
                report['configs'][f'{s}:{d}'] = {'queries': len(qs),
                                                 'mismatches_vs_persisted8': int((got != ref).sum()), 'examples': mism,
                                                 'construction_seconds': build_s, 'added_bytes': lib.sv_bytes(p)}
            finally:
                lib.sv_close(p)
        report['direct_oracle_sample'] = {'checked': len(sample), 'persisted8_disagreements': len(bad_ref)}
        report['present_queries'] = int((ref > 0).sum()); report['invalid'] = int((ref == np.uint64(2**64 - 1)).sum())
    finally:
        close('persisted8', base, libs)
    print(json.dumps(report, indent=1))

def cmd_time(name, seed, n, rounds, out, specs):
    case = case_of(name); rebuild(case, with_sa=True); libs = libraries(); lib = svlib()
    seqs = read_fasta(ROOT / case['dataset']); qs = queries(seqs, seed, n=n); rng = random.Random(seed)
    ptr = {}; loads = {}
    for m in ['rank2a', 'rank2a_AA', 'persisted8', 'suffix_array']:
        t = time.perf_counter(); ptr[m] = load(m, ROOT / case['index'], ROOT / case['table'], ROOT / case['suffix_array'], libs); loads[m] = time.perf_counter() - t
    added = {}
    for spec in specs:
        s, d = map(int, spec.split(':')); ptr[f'sv{s}_d{d}'], loads[f'sv{s}_d{d}'] = sv_open(lib, case, s, d); added[f'sv{s}_d{d}'] = lib.sv_bytes(ptr[f'sv{s}_d{d}'])
    methods = list(ptr); enc = encode(qs); ref, _ = evaluate('persisted8', ptr['persisted8'], enc, libs)
    grp = {}
    for i, q in enumerate(qs):
        key = (f'len{len(q)}' if i < n else 'probe') + ('-present' if 0 < ref[i] < 2**63 else '-absent')
        grp.setdefault(key, []).append(i)
    encs = {'all': enc, **{k: encode([qs[i] for i in v]) for k, v in grp.items()}}
    samples = {m: {g: [] for g in encs} for m in methods}; mism = {m: 0 for m in methods}
    def run(m, e, reps):
        if m.startswith('sv'):
            return sv_eval(lib, ptr[m], e, reps)
        return evaluate(m, ptr[m], e, libs, reps)
    try:
        for m in methods:
            got, _ = run(m, enc, 1); mism[m] = int((got != ref).sum())
        for _ in range(rounds):
            for g, e in encs.items():
                order = methods[:]; rng.shuffle(order)
                for m in order:
                    samples[m][g].append(run(m, e, 10)[1])
    finally:
        for m, p in ptr.items():
            lib.sv_close(p) if m.startswith('sv') else close(m, p, libs)
    med = {m: {g: statistics.median(v) for g, v in gs.items()} for m, gs in samples.items()}
    paired = {m: {g: statistics.median(a / b for a, b in zip(samples[m][g], samples['persisted8'][g])) for g in encs} for m in methods}
    res = {'case': name, 'seed': seed, 'n': n, 'rounds': rounds, 'reps': 10, 'queries': len(qs),
           'group_sizes': {g: len(v) for g, v in grp.items()}, 'mismatches_vs_persisted8': mism,
           'load_or_construction_seconds': loads, 'sv_added_bytes': added,
           'index_bytes': {'ropebwt': (ROOT / case['index']).stat().st_size, 'table': (ROOT / case['table']).stat().st_size,
                           'suffix_array': (ROOT / case['suffix_array']).stat().st_size},
           'median_us_per_query': {m: {g: v * 1e6 for g, v in x.items()} for m, x in med.items()},
           'median_paired_ratio_vs_persisted8': paired, 'samples_seconds_per_query': samples,
           'machine': platform.platform(), 'load_average': list(__import__('os').getloadavg()),
           'note': 'Warm in-process native count_batch timings under shared desktop load; not a quiet-machine or whole-process measurement.'}
    Path(out).write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({'mismatches': mism, 'all_us': {m: round(med[m]['all'] * 1e6, 3) for m in methods},
                      'paired_all': {m: round(paired[m]['all'], 3) for m in methods}}, indent=1))

def cmd_cert(name, seed, spec, outdir):
    case = case_of(name); rebuild(case); libs = libraries(); lib = svlib(); s, d = map(int, spec.split(':'))
    dest = (ROOT / outdir).resolve()
    if not dest.is_relative_to(PKG) or dest.exists():
        raise SystemExit('choose a new directory inside the package')
    qs = queries(read_fasta(ROOT / case['dataset']), seed, n=96); enc = encode(qs)
    p, build_s = sv_open(lib, case, s, d); b = load('persisted8', ROOT / case['index'], ROOT / case['table'], None, libs)
    try:
        got, _ = sv_eval(lib, p, enc); ref, _ = evaluate('persisted8', b, enc, libs); added = lib.sv_bytes(p)
    finally:
        lib.sv_close(p); close('persisted8', b, libs)
    assert (got == ref).all(), 'sv disagrees with persisted8'
    dest.mkdir()
    cert = {'dataset': case['dataset'], 'dataset_sha256': case['dataset_sha256'], 'method': f'sv8 s={s} d={d}',
            'queries': [{'sequence': q, 'count': int(c)} for q, c in zip(qs, got)]}
    (dest / 'candidate.json').write_text(json.dumps(cert, indent=2) + '\n')
    print(json.dumps({'witness': witness(dest / 'candidate.json'), 'construction_seconds': build_s, 'added_bytes': added,
                      'sv_source_sha256': digest(PKG / 'sv.c'), 'library_sha256': digest(ROOT / 'build/sv.dylib')}))

def cmd_select(dev_json, out):
    """Pre-registered rule: fastest dev whole-panel median among sv configs whose
    median paired ratio vs persisted8 is <= 1.05 on every length x presence group
    (the six fixed probes are not a length group and are reported only)."""
    dev = json.loads(Path(dev_json).read_text()); rows = {}
    for m, gs in dev['median_paired_ratio_vs_persisted8'].items():
        if not m.startswith('sv'):
            continue
        worst = max(v for g, v in gs.items() if g.startswith('len'))
        rows[m] = {'all_median_us': dev['median_us_per_query'][m]['all'], 'worst_group_ratio': worst, 'eligible': worst <= 1.05}
    ok = [m for m in rows if rows[m]['eligible']]
    chosen = min(ok, key=lambda m: rows[m]['all_median_us']) if ok else None
    freeze = {'frozen_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'rule': cmd_select.__doc__.strip(),
              'candidates': rows, 'selected': chosen, 'sv_source_sha256': digest(PKG / 'sv.c'),
              'library_sha256': digest(ROOT / 'build/sv.dylib'), 'harness_sha256': digest(Path(__file__))}
    Path(out).write_text(json.dumps(freeze, indent=1) + '\n'); print(json.dumps(freeze, indent=1))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'check':
        cmd_check(a[1])
    elif a[0] == 'time':
        cmd_time(a[1], int(a[2]), int(a[3]), int(a[4]), a[5], a[6:])
    elif a[0] == 'select':
        cmd_select(a[1], a[2])
    elif a[0] == 'cert':
        cmd_cert(a[1], int(a[2]), a[3], a[4])
