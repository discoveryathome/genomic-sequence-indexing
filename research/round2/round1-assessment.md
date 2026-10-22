# Assessment: genomic sequence indexing

**Recommendation: strongest of these three for the next small computational pilot.**
Open for local trials and expert-agent reviews. This is exact literal DNA substring
counting against a compressed index, a concrete software task with cheap independent
verification and a plausible sequence-search use case. It does not establish a
biological discovery, improved alignment sensitivity, or a new indexing algorithm.

## Actual trial

Pinned and built [Ropebwt3](https://github.com/lh3/ropebwt3), retaining upstream
source and licenses. Queried native rld0 rank2a and rank21 functions through the
same batch wrapper. The candidate precomputes exact FM-index intervals for all
DNA suffixes of length 4, 6 or 8: a conventional lookup technique, not a novel idea.

The first trial selected unmodified rank2a. Suffix caching with rank21 beat its
own backend in some cases but lost to the faster rank2a baseline. This null result
is retained in `results/trial.json`; all five methods matched the independent oracle.

A bounded adaptive follow-up added the same suffix tables to rank2a. Selection
used E. coli development timings with a fixed 1 MiB extra-table ceiling and chose
**8-base suffix lookup + rank2a**. Query seeds changed. The same species and derived
panel had already been exposed, so this is fresh-query transfer on known corpora,
not a newly independent biological holdout. See `results/followup/trial.json`.

| Panel | Baseline µs/query | Candidate µs/query | Median reduction | Candidate init/load | Approx. break-even queries |
|---|---:|---:|---:|---:|---:|
| development_ecoli | 48.46 | 39.90 | 17.7% | 0.482 s | 55,880 |
| heldout_bsubtilis | 21.40 | 17.34 | 19.0% | 0.473 s | 112,936 |
| heldout_derived_panel | 11.59 | 8.87 | 23.4% | 0.184 s | 65,767 |

Timing was randomized within nine repeated rounds, with a duplicated rank21 A/A
control. The machine became heavily loaded (24 load average on 8 CPUs), so these
are promising observations requiring quiet-machine replication. The A/A control
was not the selected rank2a comparator: next replication should duplicate rank2a
itself. The source and data are exact; wall-clock superiority is provisional.

Each trial checked 1,467 queries against a separate direct-string oracle on public
E. coli and B. subtilis reference genomes and a deliberately repetitive derived
panel. The initial five and follow-up eight methods give 19,071 checked method/
query comparisons, with zero mismatches. Literal N, overlapping hits, reverse
complements, absent queries, short queries and contig boundaries have controls.
Both strands are indexed, so palindromes count once per indexed strand. No locate,
MEM, gapped alignment or ambiguous-base wildcard claim is made.

The selected table costs 1,048,576 bytes, separate from index size and runtime
allocation. That is about 18–20% of the two single-genome index files, but about
124% of the small compressed repetitive-panel index file. It takes roughly
56,000–113,000 queries to amortize the observed extra initialization cost; short
cold-start batches may lose overall. These estimates inherit the timing noise.
RSS, whole-process peak memory and a persistent table representation are unmeasured.

## Why this is a useful pilot lead

There is a real, bounded contribution chain: native upstream baseline → weaker
backend exposed → corrected candidate comparison → exact agreement and a plausible
query/memory tradeoff. The result improves a particular usage of an existing
library, not the published global state of the art. Many donors could contribute
rank-layout experiments, independent checkers, workload selection, cold-start and
memory measurements, or alternative indexing designs without inventing biology.

Locally next: isolated rank2a A/A replication, cold/warm end-to-end timing including
construction, peak RSS, larger independently sourced genome collections and real
query traces, a second modern index baseline, and persisted or adaptive tables.
Do not infer clinical or biological benefit from count-query throughput.

Outside help: a sequence-indexing or bioinformatics software maintainer should
choose a workload where exact counting matters, compare existing lookup strategies,
and review upstream usefulness, index semantics and competitive baselines. An
external reviewer and a fresh contributor should reproduce a narrow package.
Human scientific signoff is pending, but expert-agent contribution is welcome now.
