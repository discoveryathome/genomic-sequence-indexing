# Round 2 protocol — fixed before measurement

Scope: computational sequence indexing only. Exact literal substring counts on public reference DNA; measure software correctness, time and memory. No wet-lab work, organism modification, sequence design, experimental protocols or biological-effect predictions.

Question: does the prior conventional eight-base suffix cache provide useful total-cost savings, and can persisting it reduce initialization overhead? No novelty claim. Original results remain frozen.

Compare Ropebwt3 rank2a, duplicate rank2a A/A, rebuilt suffix8/rank2a, persisted suffix8/rank2a, and a conventional full suffix-array binary-search count index constructed with pinned bundled libsais. The SA is an uncompressed architectural control, not a modern compressed-index leaderboard or optimized production count implementation.

Development: original E. coli corpus, newly generated queries. Evaluation: fresh public accessions AE006468.2, AE004091.2, AE000511.1 and AL123456.3, individually and pooled where useful; retain source hashes and headers, all contigs. Existing synthetic repetitive panel is an exposed stress control. Keep acquisition failures; do not silently substitute data based on performance. Freeze suffix length 8 before new evaluation, no tuning on held-out results.

Query groups: sampled exact substrings at lengths 20/31/75/150, synthetic absent strings, short strings at lengths 1/4/7/8/9, and literal N/palindrome/contig-boundary controls. These are controlled traces, not actual sequencing-read workloads. Check all queries against direct per-contig both-strand overlapping string counts.

Warm throughput: seven randomized rounds with identical native batching, >=2000 count operations per timed sample, separate short/long groups, and duplicated rank2a control. Report all samples, medians and paired ratios, no significance claim. Fresh-process end-to-end: batch sizes 100, 10000, 100000, three repetitions/method in randomized order; include index loading and cache validation, separately report Python/import/input overhead and wall time. OS page cache is not flushed; call these fresh-process, filesystem-warm measurements, not disk-cold. Measure peak RSS in separate processes and construction time/index bytes for each representation. Record system load throughout; this shared machine is not isolated.

Cache artifacts must bind index and table hashes, format, word size and endianness; fail closed on mismatch/truncation. Test invalid cache, wrong index, N fallback, short queries and contig boundaries. A persisted cache inherits the builder's correctness; a checksum is not a proof. Check rebuilt and persisted tables against oracle.

Promotion gate: every oracle matches; persisted variant saves end-to-end time on at least two fresh corpora for a declared batch size; paired rank2a A/A drift reported and timing claim qualified if drift >10%. Otherwise keep it an experimental option, retain null results. Fresh participant smoke run and distributable source bundle required; no independent review inferred.

Data-domain amendment before performance measurement: AE000511.1 contains 34 non-ACGTN ambiguity symbols and fails the declared literal alphabet. Preserve the original reference and error; exclude it from measured cases and the pool rather than silently normalizing. Three fresh reference corpora plus their 15.5 Mb pool remain. Dataset exclusion was solely alphabet-based, with no candidate performance observed. Prepared case artifacts are reused unchanged.
