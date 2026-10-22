# Current distribution status — computational sequence indexing

Open for limited exact-string software trials and expert review. FIRST_TASKS.md
has replication, compressed-baseline, break-even and workload-definition tasks.
EVALUATION.md and FIRST_REVIEW.md provide evaluation and independent-review packets.

## Second compressed-index family

SDSL 2.1.1 now supplies a genuine compressed FM-index comparator using a Huffman
wavelet tree and RRR(63) bitvectors, SA/ISA sampling 32/64. The configuration was
fixed before testing. This is an established alternative, not a claim that it is
the fastest contemporary compressed index. Build compatibility fixes are recorded;
upstream algorithm parameters were not tuned. Source and linked binaries stay
in ignored build directories; dependencies retain their terms.

All 107 corpus queries and eight tiny multi-contig semantic controls matched the
separate direct-string oracle. Both strands count separately, including palindromes;
N is literal, matches overlap and queries cannot cross boundaries. There is no
wet-lab work, sequence design or biological-effect inference.

On the exposed AL123456.3 corpus, serialized sizes were 3,448,577 bytes for SDSL,
5,436,432 for rank2a and 6,485,032 for rank2a plus persisted8. SDSL construction
was about 2.13 seconds. Warm medians were 51.68, 19.34 and 15.05 microseconds/query,
respectively. Thus the new control exposes a meaningful space/time tradeoff rather
than an unconditional win. The duplicated rank2a median was 19.45 microseconds.
Seven randomized timing rounds are retained. These are author-run measurements
under shared load, not portable performance guarantees.

## Actual batch-cost follow-up

A separately declared follow-up ran 36 fresh processes: four batch sizes, three
methods and three repeats. All counts verified. Median external wall time, seconds:

| Queries | rank2a | rank2a A/A | persisted8 |
| ---: | ---: | ---: | ---: |
| 1 | 0.3724 | 0.3110 | 0.4500 |
| 100 | 0.3143 | 0.3708 | 0.3144 |
| 10,000 | 0.6853 | 0.6472 | 0.7290 |
| 100,000 | 9.9722 | 24.5543 | 7.6246 |

Startup/import/input encoding are included. OS caches were not flushed. A/A
variation is severe: at 100,000 queries the duplicated baseline medians differ
by about 2.46x. This pass cannot establish a reliable process-level speedup or
break-even point, even where the cached method has a better median. The earlier
component model estimated a roughly 1,459-query cache break-even, but that estimate
is not an empirically established process-level crossover. The measured curve
must be reported alongside it. Queries are generated probes on one exposed corpus,
not a real application trace. Independent workload provenance remains a useful task.

## Optional comparator reproduction

```sh
uv pip install --python .venv/bin/python cmake==4.4.4
python tools/build_sdsl.py
python tools/compare_sdsl.py --out research/my-sdsl-comparison
python tools/verify_count.py research/my-sdsl-comparison/candidate.json
```

For the frozen batch follow-up: `python tools/cache_break_even.py --out research/my-batches`.
It deliberately uses the archived exposed comparison panel. Use a separate protocol
and generator to make a genuinely new evaluation. Its full source, raw process logs,
RSS and per-stage timings are in batch-comparison/.

Linux execution and independent outside review remain pending; see MIGRATION.md.
A quiet-machine replication, real query trace, larger/repetitive corpus comparison
and specialized baseline review are still valuable before broad performance claims.
