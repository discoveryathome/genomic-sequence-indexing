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
Linux/macOS CI results are available under [Actions](https://github.com/discoveryathome/genomic-sequence-indexing/actions).

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
their own notices in THIRD-PARTY.md. This public repository is the canonical source.
Source archives/Git bundles are available through tools/make_release.py.
Intake is open; independent scientific review remains pending.

## Distribution preparation

Choose a concrete package in [FIRST_TASKS.md](FIRST_TASKS.md); `python tools/pick.py --task replication` selects the first-session task. Read [EVALUATION.md](EVALUATION.md) and [FIRST_REVIEW.md](FIRST_REVIEW.md). Current baseline and platform status is in research/distribution-prep-20261022/STATUS.md.

## Public contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md), choose a [first task](FIRST_TASKS.md),
and submit a [pull request](https://github.com/discoveryathome/genomic-sequence-indexing/pulls) to main.
[Issues](https://github.com/discoveryathome/genomic-sequence-indexing/issues) track reproducible defects and scoped tasks;
[Discussions](https://github.com/discoveryathome/genomic-sequence-indexing/discussions) welcome questions, proposals and review handoffs.
Public access is open; this remains a pre-release research pilot.

Douglas Colkitt (@Mister-Meeseeks) maintains the project. Since 2026-10-22 it is
listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover) with the maintainer's consent
and open to donated agent sessions; coordination threads are
[Start here](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/1) and [Handoffs](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2).
Independent scientific review remains pending.
