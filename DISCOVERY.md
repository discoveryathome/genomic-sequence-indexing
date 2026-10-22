# Genomic sequence indexing: contributor workflow

Intake is open for local contributions and expert-agent assistants. Start with
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
