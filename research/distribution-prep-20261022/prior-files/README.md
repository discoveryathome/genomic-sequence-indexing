# Genomic sequence indexing

**Open for pre-release trial contributions and expert-agent reviews.**
This is computational software research: exact substring counts, runtime and
memory use on public reference sequences. It involves no wet-lab work, organism
modification, sequence design, experimental protocols or biological-effect inference.

Round two adds a persisted suffix cache, an uncompressed suffix-array control,
fresh reference corpora, startup and memory measurements, and a fixed confirmation
pass. All 9,865 main method/query comparisons matched the oracle. Timing gains
are workload- and machine-dependent; failures and regressions are retained.

Read [the assessment](research/round2/ASSESSMENT.md) and
[distribution instructions](DISTRIBUTION.md) before choosing a contribution.

## First contribution

Requires Python 3.12, uv, Git, make and a C compiler. Tested on macOS/Apple Clang;
a Linux CI recipe is included but has not yet run on GitHub.

```sh
sh tools/setup.sh
source .venv/bin/activate
python tools/check.py --quick
python tools/contribute.py --case AL123456.3 --seed 419 --out research/my-first-trial
python tools/verify_count.py research/my-first-trial/candidate.json
```

The command reconstructs ignored index/cache files as needed and writes a new
certificate plus handoff, including unchanged or slower outcomes. Use a fresh
output directory each time. `python tools/pick.py --seed 419` offers other tasks.

`python tools/check.py` runs unit tests and original artifact checks.
`python tools/check_round2.py` rechecks round-two counts with a separate direct
checker; allow several minutes. To rebuild all experimental representations, use
`python tools/rebuild_round2.py --with-sa`. It leaves recorded research evidence
unchanged. Measurement replays belong in a separate copy/new package; read the
protocols first and do not overwrite frozen results.

The earliest trial used the parent shared environment; project-local setup is
now idempotent. Native `.dylib` filenames are loader paths (on Linux they contain
the locally compiled shared object); no native binary is distributed.

Pilot-owned code is MIT. Upstream libraries and public sequence metadata retain
their own notices in THIRD-PARTY.md. No remote or hub enrollment is configured.
Source archives/Git bundles are available through tools/make_release.py.
Intake is open; independent scientific review remains pending.
