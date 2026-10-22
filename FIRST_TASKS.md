# First contribution packages

Intake is open. Choose one task and return a complete handoff, including failures.
See EVALUATION.md for exposure rules and FIRST_REVIEW.md for independent review.
Budgets are defaults for trial sessions, not a reason to refuse explicitly authorized
larger work. Record extensions and actual resources.

## replication: Produce one verified exact-count handoff

Budget: 30 minutes; built-in 96-query panel and five timing rounds.

```sh
python tools/contribute.py --case AL123456.3 --seed 419 --out research/my-first-trial
```

Deliverable: candidate.json and handoff.json; run tools/verify_count.py. Equal counts with no speed improvement complete the task.

## compressed-baseline: Audit the SDSL FM-index comparison

Budget: 60 minutes; one corpus, fixed configuration and query panel.

After the optional build in research/distribution-prep-20261022/STATUS.md, use `python tools/compare_sdsl.py --out research/my-sdsl-comparison`.

```sh
python tools/check.py --quick
```

Deliverable: Compare two-strand, overlapping, literal-N and contig-boundary semantics; report index bytes, construction/load time and all query mismatches. The standalone runner has separate dependency terms.

## break-even: Find the persisted cache break-even batch size

Budget: 60 minutes; fixed batches 1, 100, 10000 and 100000; three randomized paired processes.

Use `python tools/cache_break_even.py --out research/my-batches` for exact replication of the exposed panel.

```sh
python tools/check.py --quick
```

Deliverable: Report warm count time, startup including hashing, peak RSS and byte counts. A regression at every batch size is a complete outcome. Generated queries remain workload probes, not real application traces.

## workload: Specify a real exact-count use case

Budget: 30 minutes; one sourced workload definition.

```sh
python tools/pick.py --task workload
```

Deliverable: Document query lengths, batch sizes, repeats, literal-N policy, memory budget and permitted trace provenance. No biological-effect inference; external contact needs explicit instruction.
