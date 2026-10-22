# Agent entry — open local pilot

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
user's actual permission before external posting; local research is open.
