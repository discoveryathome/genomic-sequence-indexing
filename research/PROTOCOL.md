# Three local pilot trials

Scope: author-run feasibility and contribution trials. These are not independent
donor sessions or external scientific reviews. All three accept local trial and
expert-agent work. No repository is being published or submitted to the hub.

The user confirmed these three starting points on 2026-10-22. This round tests
the following representative questions:

1. **Computational geometry:** can a bounded-integer specialization improve a
   robust 2-D orientation predicate without wrong signs or unacceptable regressions
   on fractional coordinates? Compare with pinned Shewchuk adaptive predicates,
   and with a direct exact integer implementation where its domain permits it.
2. **Numerical computation:** can bounded polynomial/branch tuning improve the
   accuracy/cost tradeoff of scalar phi functions used in exponential integration?
   Compare with stable series/expm1 baselines, not just cancellation-prone formulas.
3. **Genomic sequence indexing:** can a suffix-interval table improve exact DNA
   count-query throughput over pinned Ropebwt3 rank primitives at a stated memory
   cost? Validate strand semantics, overlapping matches, absent queries and contig
   boundaries against a separate direct-string oracle on public bacterial DNA.

Each trial has a finite candidate grid, fixed development and held-out seeds,
separate selection and evaluation, source hashes, retained negative results,
candidate verification, and a local handoff. Timing trials run sequentially.
Timing evidence is machine-specific, warm-process data; system activity is not
controlled. Repeated timings and A/A variation must accompany speed claims.

Selection rules are fixed in code before the first measurement. A held-out failure
is retained; it is not repaired and relabeled as an unseen success. Future donor
tests need new unseen cases because this entire package becomes exposed material.

Success tiers: (a) workflow and verification work; (b) reproducible improvement
over a substantive starting baseline; (c) improvement over current published or
production methods on representative workloads. Tier (b) alone does not establish
tier (c), novelty, generality, or real application benefit. Known algorithmic
techniques are credited as such. A null result is an acceptable trial outcome.

Outside help should identify a concrete useful workload, audit the verifier and
baseline, and assess remaining headroom. Missing signoff does not block local work.
