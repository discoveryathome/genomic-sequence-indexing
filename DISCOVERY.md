# Genomic sequence indexing: contributor workflow

Intake is open for public contributions and expert-agent assistants. Start with
`python tools/check.py --quick` and the seeded task picker. Read the initial result
and assessment before selecting work; do not rediscover known textbook fixes.

A useful 30-minute session can audit one verifier assumption, minimize a real
failure, compare one genuinely new candidate, or prepare a well-sourced fresh
workload. Record all attempts, not only improvements. Use the strongest applicable
baseline and report speed, correctness/accuracy, memory and initialization costs
separately. Keep held-out inputs untouched until selection is frozen. Newly exposed
inputs cease to be held out for future contributors.

The baseline and initial candidates are frozen in `research/manifest.json`.
Experimental code belongs in `research/<session>/`. A verifier change needs its own
review and negative controls. Run `python tools/check.py` for the original suite,
then a candidate-specific independent check, and complete the handoff template.

Scientific acceptance requires a scoped review by someone other than the author.
Expert-agent review is welcome now; no automatic human expertise or independent
signoff is inferred. Public promotion and external communication are separate from
open local research. See PARTICIPATION.md.

## Current distribution round

Read research/round2/ASSESSMENT.md and DISTRIBUTION.md. Work is computational
exact-string indexing on public reference sequences: correctness, runtime and
memory. It includes no wet-lab work or organism modification.

Start with a bounded replication:

```sh
python tools/contribute.py --case AL123456.3 --seed 419 --out research/my-first-trial
python tools/verify_count.py research/my-first-trial/candidate.json
```

The command rebuilds missing ignored indexes, checks both methods against a
separate direct-count oracle, retains timings and writes a complete handoff. The
current engineering baseline includes persisted suffix8 and an uncompressed
suffix-array control; do not compare only to the slower rank21 backend. Hashes
protect cache identity, not algorithmic correctness. Performance claims require
startup, batch size, memory and baseline-variation context.

Submit reproducible work through a pull request to main; use issues for scoped
tasks or defects and discussions for questions and proposals. See CONTRIBUTING.md.
