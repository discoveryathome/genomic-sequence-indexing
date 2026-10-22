# Genomic sequence indexing

Exact DNA count queries on a compressed index; throughput versus extra memory. **Open for local pre-release trials and expert-agent reviews.**

Read [the assessment](research/ASSESSMENT.md) and [the contribution guide](DISCOVERY.md).
The initial author-run trial is complete in `results/trial.json`. It establishes
only the specific measurements recorded there, not novelty or external signoff.

## Start

Requires macOS/Apple Clang, Python 3.12 and `uv`; other platforms need a native
library suffix/build adjustment and fresh validation. From this directory:

```sh
sh tools/setup.sh
source .venv/bin/activate
python tools/check.py
python tools/pick.py --seed 42
```

The original local run used the shared environment at `../.venv`. Every trial is
replayable with `python src/trial.py`; run in a copy or new worktree, because replay
writes new results and timings. The integrity check intentionally detects altered
frozen trial artifacts. Save new proposals in separate research packages.

`discover.json` uses this local repository's `file:` URI and an empty hub list.
No GitHub repository or public listing was created. Before publishing, assign the
real canonical remote and review source/data notices.

- [Participation](PARTICIPATION.md)
- [Protocol](research/PROTOCOL.md)
- [Sources](research/sources.json)
- [Review record](research/review.json)
- [Handoff template](research/HANDOFF_TEMPLATE.md)

Pilot-owned code is MIT; third-party code/data retain the terms in THIRD-PARTY.md.

Verify an individual handoff without rerunning the search:

```sh
python tools/verify_candidate.py results/example-candidate.json
```

The JSON examples specify the certificate shape. Passing certifies only the supplied inputs and outputs, not novelty or whole-domain correctness.
