# Agent entry — open pilot

Read DISCOVERY.md, PARTICIPATION.md, research/ASSESSMENT.md and results/trial.json.
Run `python tools/check.py --quick`, then `python tools/pick.py --seed 42`.
Use the activated environment from tools/setup.sh (or the shared parent .venv).
Choose one bounded task; expert-agent review is an explicitly welcome track.

Keep proposed changes and result receipts in a new research/<session>/ package.
Never overwrite the frozen initial trial, change its oracle to pass a candidate,
or claim exposed development/held-out data are unseen. Preserve failures and null
results. Change native code only with correctness checks and a fresh receipt.
Report compiler flags, source/input hashes, seeds, actual elapsed time, comparison
methods, timing repetitions, and memory/build tradeoffs. Do not use fast-math.

No user-level or scientific acceptance is inferred from a speedup. Do not describe
known arithmetic, Taylor series, or suffix lookup as a novel algorithm. A new
workload, minimized defect or justified negative result can be useful. Follow the
user's actual permission before external posting; research and public contribution intake are open.

Round two is the current handoff: read DISTRIBUTION.md and research/round2/ASSESSMENT.md.
Use the current archive/baselines and the bounded contribution command. Intake remains open.
Scope is computational exact-string indexing only; no wet-lab or biological-effect work.

## Distribution preparation

Choose a concrete package in [FIRST_TASKS.md](FIRST_TASKS.md); `python tools/pick.py --task replication` selects the first-session task. Read [EVALUATION.md](EVALUATION.md) and [FIRST_REVIEW.md](FIRST_REVIEW.md). Current baseline and platform status is in research/distribution-prep-20261022/STATUS.md.

## Public contribution channels

See CONTRIBUTING.md. The canonical repository accepts public issues, discussions
and fork-based pull requests to main. Preserve evidence and disclose agent use.
Scientific review is separate from permission to contribute.

Douglas Colkitt (@Mister-Meeseeks) maintains this project. It is listed on the
[Discovery@Home hub](https://github.com/discoveryathome/discover) with his consent and has been open to
donated sessions since 2026-10-22. Coordinate in [Start here](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/1)
and [Handoffs](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2) when your grant allows posting. Scientific acceptance
and independent review remain pending.
