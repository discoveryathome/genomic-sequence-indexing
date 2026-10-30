"""Post-evaluation diagnostic (not part of the frozen selection/evaluation):
is the absent/short-query regression real, or timing noise? Adds the missing
persisted8 A/A control. Fresh queries, seed int(hub_seed[16:24], 16).

  python research/explore-singleton-verify-973e687a/diag.py OUT.json [LIB ...]
"""
from pathlib import Path
import json, os, random, statistics, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sv_run import ROOT, case_of, svlib, sv_open, sv_eval, read_fasta, encode, libraries, load, close, evaluate, rebuild, revcomp, digest

SEED = int('973e687a7a4503011501a460be45a9ea'[16:24], 16)

def main(out, libnames):
    case = case_of('AL123456.3'); rebuild(case); libs = libraries()
    seqs = read_fasta(ROOT / case['dataset']); rng = random.Random(SEED)
    groups = {}
    for L in (20, 31, 75, 150):
        groups[f'absent{L}'] = [''.join(rng.choices('ACGT', k=L)) for _ in range(400)]
    t = seqs[0]
    groups['present20'] = [t[p:p + 20] for p in (rng.randrange(len(t) - 20) for _ in range(400))]
    groups['present21rc'] = [revcomp(t[p:p + 21]) for p in (rng.randrange(len(t) - 21) for _ in range(400))]
    ptr = {'persisted8': load('persisted8', ROOT / case['index'], ROOT / case['table'], None, libs),
           'persisted8_AA': load('persisted8', ROOT / case['index'], ROOT / case['table'], None, libs)}
    svl = {}
    for name in libnames:
        os.environ['SV_LIB'] = name; lib = svlib(); key = 'sv16_d4' + ('' if name == 'sv.dylib' else '@' + name)
        ptr[key], _ = sv_open(lib, case, 16, 4); svl[key] = lib
    encs = {g: encode(q) for g, q in groups.items()}
    def run(m, e, reps):
        return sv_eval(svl[m], ptr[m], e, reps) if m in svl else evaluate('persisted8', ptr[m], e, libs, reps)
    ref = {g: run('persisted8', e, 1)[0] for g, e in encs.items()}
    mism = {m: sum(int((run(m, e, 1)[0] != ref[g]).sum()) for g, e in encs.items()) for m in ptr}
    present = {g: int((ref[g] > 0).sum()) for g in encs}
    samples = {m: {g: [] for g in encs} for m in ptr}
    try:
        for _ in range(15):
            for g, e in encs.items():
                order = list(ptr); rng.shuffle(order)
                for m in order:
                    samples[m][g].append(run(m, e, 50)[1])
    finally:
        for m, p in ptr.items():
            svl[m].sv_close(p) if m in svl else close('persisted8', p, libs)
    res = {'kind': 'post-evaluation diagnostic, not selection or evaluation evidence', 'seed': SEED,
           'libraries': {n: digest(ROOT / 'build' / n) for n in libnames}, 'rounds': 15, 'reps': 50,
           'queries_per_group': 400, 'present_counts': present, 'mismatches_vs_persisted8': mism,
           'median_us': {m: {g: statistics.median(v) * 1e6 for g, v in x.items()} for m, x in samples.items()},
           'median_paired_ratio_vs_persisted8': {m: {g: statistics.median(a / b for a, b in zip(samples[m][g], samples['persisted8'][g])) for g in encs} for m in ptr},
           'load_average': list(os.getloadavg())}
    Path(out).write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: res[k] for k in ('mismatches_vs_persisted8', 'present_counts', 'median_paired_ratio_vs_persisted8', 'load_average')}, indent=1))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or ['sv.dylib'])
