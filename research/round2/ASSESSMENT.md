# Computational sequence indexing: round-two assessment

**Ready for limited pre-release contributor distribution as an exact-string
software indexing and benchmarking pilot.** The persisted cache makes the earlier
lookup optimization easier to reuse. Confirmation supports a modest measured
throughput benefit, with explicit startup/memory tradeoffs. No novel algorithm,
production-workload advantage or biological result is established.

Scope is computational exact substring counting on public reference sequences.
There is no wet-lab work, organism modification, sequence design, experimental
protocol or biological-effect inference. This is a software data-structure task.

## What was added and tested

The native Ropebwt3 rank2a baseline now has a duplicated A/A control. The prior
eight-base lookup table is compared both rebuilt at startup and persisted with
index/table SHA-256 binding, format checks and endian checks. Checksums establish
artifact identity, not whole-domain algorithm correctness. A second architectural
control uses a full uncompressed suffix array built with pinned libsais and
pilot-owned conventional binary search. It is not an optimized production count
implementation or a second competitive compressed-index system.

Three fresh public reference corpora and their 15,533,386-base pool extend the
original E. coli and synthetic repetitive panel. One downloaded accession contains
34 symbols outside literal A/C/G/T/N and was excluded on alphabet grounds before
performance measurement; its raw record and failure are retained. The pool repeats
the three references, and the synthetic panel remains exposed material: these
are six test panels, not six independent biological samples.

Generated long queries, short queries around the lookup threshold, literal N,
palindromes, absent strings and contig-boundary controls supplied 1,973 queries.
All **9,865 method/query comparisons matched** the direct-count oracle. Exhaustive
short-string tests and a separate regex-based witness checker strengthen coverage.
There are **216 fresh-process measurements**, plus 24 in a single fixed confirmation
pass. All failures and the initial negative results remain in the package.

## Results and their limits

The initial round ran under substantial shared-machine load; duplicated-baseline
median drift reached 27.5%. A fixed confirmation, with no candidate retuning, reused
the exposed queries after load fell. Its warm A/A median drift was at most 4.0%.
Long-query throughput improved 19.5–23.5% in confirmation; that does not translate
one-for-one into whole-process savings.

Observed **100,000-query whole-process time reduction** for persisted8 versus
rank2a (positive is faster; negative is a regression):

| Corpus | Main round | Fixed confirmation |
|---|---:|---:|
| AE006468.2 | 10.9% | 13.7% |
| AE004091.2 | -14.1% | 2.7% |
| AL123456.3 | 16.0% | 9.0% |
| pooled | 14.7% | 10.8% |

These are medians of three fresh processes per method. They include startup and
input preparation; the OS filesystem cache was not flushed. Confirmation is
repeatability on exposed data under lower shared load, not a quiet-machine study
or a newly independent holdout. The modest 2.7% case should especially not be
treated as a portable established speedup. The old E. coli panel regressed 4.7%
on whole-process large-batch time in the main round and was not in confirmation.
Short 100-query batches had mixed outcomes, including regressions.

Persisting the table removes repeated table construction: observed load/validation
time was about 2–21 ms, versus roughly 0.21–1.25 s rebuilding the table. Plain
rank2a loaded in about 0.2–2.8 ms. The persisted file is 1,048,600 bytes (1 MiB of
intervals plus a 24-byte header), with separate metadata. Index hashing is included
in persisted startup timings. Creation cost is still paid once and is recorded.

The pooled compressed index is 19.26 MB plus the 1.05 MB table; the full suffix
array is 155.33 MB. The suffix-array control was faster in the main count tests
but materially larger. The repetitive panel makes the tradeoff sharper: 0.85 MB
compressed index, 1.05 MB table, versus 20.01 MB suffix array. A cache is not
unconditionally a good memory choice.

Pooled 100,000-query median peak RSS was about 99.7 MiB for rank2a, 101.7 MiB for
persisted8 and 200.2 MiB for the suffix array. These are **whole-process peaks**,
including Python input preparation and native queries; that overhead can mask
index-memory differences on smaller panels. They are not steady-state native
index allocation measurements. Construction times, all warm samples, fresh-process
rows, load averages and index sizes are preserved.

## Contribution workflow and next stage

The project has an idempotent setup, one-command bounded replication, a source-bound
count certificate, cache-corruption/identity controls, current task cards, and
source/Git-bundle distribution tooling. Input generation and benchmarks are software
work; contributors need no laboratory access. Read [DISTRIBUTION.md](../../DISTRIBUTION.md).
Original evidence remains frozen, and every existing panel is now exposed.

Next useful contributions: independent replication on a quiet second machine;
real exact-count query traces and application batch sizes; a strong second
compressed-index implementation; larger/repetitive collections; memory-mapped or
adaptive cache sizes; and steady-state native-memory measurement. Start from
rank2a plus the persisted cache and retain the uncompressed control; comparing only
to rank21 would repeat a known inadequate baseline. A counterexample, justified
negative result or workload characterization is an acceptable contribution.

A sequence-indexing software maintainer should assess competitive baselines and
upstream usefulness. No independent external reviewer or fresh donor is claimed;
a clean-checkout author smoke is operational testing. Intake is open for trials
and expert-agent review, while scientific acceptance remains pending.

Evidence: [protocol](PROTOCOL.md), [main summary](summary.json),
[confirmation](confirmation/results.json), [data provenance](data-sources.json),
[original assessment](round1-assessment.md). Sources: [Ropebwt3](https://github.com/lh3/ropebwt3),
[libsais](https://github.com/IlyaGrebnov/libsais),
[ENA/INSDC reuse policy](https://ena-browser-docs.readthedocs.io/en/latest/about/policies.html).
