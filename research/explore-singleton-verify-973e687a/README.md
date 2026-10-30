# Singleton locate-and-verify on top of persisted8 (exploration, author-checked)

Computational exact literal substring counting only. No wet-lab work, sequence design or
biological-effect inference. This package adds one experimental count method and its
evidence. It changes no frozen file, oracle, frontier or accepted result.

**Outcome: partial.** On generated long-query mixes from the exposed AL123456.3 corpus, the
frozen configuration (s=16, d=4) counted 3.4x faster than persisted8 on the 102-query
evaluation panel and 2.5x faster on a 966-query panel, with zero count mismatches, at
+5.58 MB of memory and 4.3–5.2 s of unpersisted construction. It **failed the third
pre-registered criterion**: absent and short query groups ran 6–17% slower than persisted8
in median paired ratio during evaluation. The protocol had no persisted8 A/A control. A
post-evaluation diagnostic with that control, 400 fresh queries per group and lower load
put the four absent groups and 20-mers at 0.996–1.023 against an A/A spread of 0.997–1.013, so most of the
evaluation regression did not reproduce. It does not change the registered outcome. The gain comes entirely from present 31/75/150-mers. It is
not a new algorithm: the components (sampled-suffix-array locate, direct text comparison)
are standard.

## Idea

persisted8 spends one rank2a call per remaining pattern symbol even after the suffix
interval has narrowed to one BWT row. On a 4.4 Mbp genome indexed on both strands
(8.8 M rows) that happens after about 13–14 symbols, so a present 150-mer spends about 128
of its 142 rank calls checking a single candidate. sv8 keeps persisted8's backward search
unchanged, and once the interval has been one row for more than `d` checks with more than
`s/2+1` symbols left, it

1. locates the row with a text-position-sampled suffix array: at most `s-1` LF steps
   (`rld_rank1a`), then one sample read;
2. compares the remaining prefix against the stored 2-bit text, with separators and N held
   in a sorted exception list, and returns 1 or 0.

The text and samples are rebuilt at load time by walking LF from every sentinel row, the
way Ropebwt3's `ssa.c` builds its sample array. They therefore use the multi-string BWT's
own row and string order, with no libsais or sentinel-order assumption. Upstream `rb3_ssa`
samples by row index, so its locate walk has no fixed bound. This package samples by
string-local text offset (offset 0 is always sampled), so the walk has a hard bound.

Probation `d` exists because the first best-case model showed that locating at the first
singleton slows down random absent queries: they reach a single row and then fail one or
two symbols later, so a locate there is wasted.

## Pre-registration, selection and evaluation

`protocol.json` was written before any candidate code. It records the task draw (hub
seed → decimal → `replication` card), the scope change (a new method under focus
`explore`), the seeds (dev 2051343105, eval 2537449594, both derived from the hub seed),
the 2x2 grid, the selection rule, the pass threshold and the stopping rule.
`freeze.json` records the mechanically selected configuration and the source, library and
harness hashes before any evaluation output existed.

| | development (966 q) | eval panel (102 q) | eval groups (966 q) |
|---|---:|---:|---:|
| rank2a µs/query | 14.94 | 14.02 | 16.35 |
| rank2a A/A µs/query | 14.86 | 14.44 | 15.44 |
| persisted8 µs/query | 11.68 | 11.08 | 12.32 |
| **sv16_d4 µs/query** | **4.06** | **3.25** | **4.86** |
| suffix_array (uncompressed) µs/query | 1.83 | 0.83 | 1.91 |
| sv16_d4 / persisted8, median paired ratio | 0.345 | 0.296 | 0.357 |

These are warm, in-process native `count_batch` medians: reps=10, randomized method order,
5 or 7 rounds, all methods loaded in one process. Load average was 6.7–8.0 throughout on a
shared desktop (Ryzen 5 3600, Linux, two capped cores). They are not quiet-machine or
whole-process measurements.

Per-group median paired ratios against persisted8 (evaluation, 966 queries):

| group | sv16_d4 | rank2a copy B / copy A |
|---|---:|---:|
| len150 present | 0.161 | 0.984 |
| len75 present | 0.306 | 0.959 |
| len31 present | 0.959 | 0.977 |
| len20 present | 1.061 | 0.994 |
| absent (20/31/75/150) | 1.065 / 1.018 / 1.172 / 1.013 | 1.001 / 1.025 / 1.009 / 0.985 |
| fixed probes | 1.063 | 1.012 |

The last column divides the two identical rank2a loads' paired ratios. It is the only A/A
signal the registered protocol produced, and it shows ±4% between identical code in the
same run. Absent groups held 80 queries, present groups 160, probes 6.

The selection rule picked the only eligible configuration, sv16_d4. sv16_d2 was fastest on
development (3.67 µs) but regressed len31-absent by 1.39x.

### Post-evaluation diagnostic (not selection or evaluation evidence)

`diag.py` was written after the evaluation, to test whether the absent and short-query
regression is real. It adds a second persisted8 load as an A/A control and uses fresh
queries (seed `int(hub_seed[16:24], 16)`), 400 per group, 15 rounds, reps=50, randomized
order, with the frozen library (sha256 `351977684b…b71a`). Load average was 3.2–4.0.
Output: `diag-absent.json`.

| group | persisted8 µs/query | persisted8 A/A | sv16_d4 |
|---|---:|---:|---:|
| absent20 | 1.17 | 1.000 | 0.996 |
| absent31 | 1.13 | 1.013 | 1.021 |
| absent75 | 1.14 | 1.003 | 1.023 |
| absent150 | 1.15 | 0.997 | 1.008 |
| present20 | 3.26 | 0.997 | 1.001 |
| present21 (revcomp) | 3.52 | 1.008 | 0.999 |

Ratios are median paired ratios against persisted8. Zero mismatches for all three methods.
The 17% len75-absent figure did not reproduce. A residual overhead of up to about 2% on
absent 31- and 75-mers sits just above the A/A spread. That fits the one extra comparison
sv16_d4 makes per backward-search step, but this run cannot separate it from noise. Why the
evaluation showed 6–17% is unexplained. Small groups at load 7–8 are the likely cause, but
that is a guess.

## Memory, construction and startup

| AL123456.3 | bytes |
|---|---:|
| Ropebwt3 rank2a index | 5,436,432 |
| persisted 8-mer table | 1,048,600 |
| sv additions, s=16 (2-bit text, mark bits, rank directory, samples, exceptions) | 5,583,376 |
| sv additions, s=32 | 4,480,496 |
| uncompressed suffix array control | 44,115,346 |

sv16 totals about 12.1 MB, against 6.5 MB for persisted8 and 44.1 MB for the suffix array.
Construction (two LF passes over 8.8 M rows plus sorting) took 4.3–5.2 s and is **not
persisted**: every load pays it, against 9 ms for persisted8. That rules out short batches
unless the structures are serialized. That is the first open question below.

## Correctness evidence (author-checked)

- Zero mismatches against persisted8 on every development and evaluation query (all
  methods, including rank2a, its A/A copy and the suffix array).
- `tools/verify_count.py certificate/candidate.json`: passed, 102 queries.
- Stress set (`sv_run.py check`) on the 10-contig repetitive panel (literal N runs,
  boundaries) and on AL123456.3: present substrings at both string ends and on both
  strands, one-mismatch variants inside the verified prefix and in the table region,
  windows overlapping N runs, and contig-boundary crossers. Six configurations
  (s 8–64, d 0–4), zero mismatches. A trace build shows the locate path ran 340–1,013
  times per configuration, so the agreement is not vacuous.
- The reconstructed text equals the multiset of indexed strands exactly, on both corpora.
- Negative control: an off-by-one mutant (`-DSV_MUTANT`, located position + 1) produced
  211–416 mismatches per configuration.
- persisted8 agreed with the direct string oracle on 400 sampled stress queries per corpus.

## Not checked

- Quiet-machine timing; whole-process and fresh-process timing; peak RSS.
- Serialization of the sv structures (startup cost stays 4–5 s).
- Corpora other than AL123456.3 for timing; real application traces; batch-size
  break-even.
- Intervals of 2–τ rows (only singletons are verified directly); macOS/Apple Clang.
- Independent human or domain review. All evidence here is author-checked by the agent
  that wrote the code. A separate model instance read `sv.c` and found no defect on valid
  indexes; that is not independent review.

Known limits of `sv.c` (found in that read, left unchanged because the candidate was frozen):

- An index holding only one empty string (n = m = 1) returns the error value `UINT64_MAX`
  where persisted8 returns 0.
- A failed locate returns `UINT64_MAX` instead of falling back to backward search. It
  never happened in any run here, but a fallback would be safer.
- A corrupt index whose LF walk cycles would loop forever in the first load pass, which has
  no step guard. Valid indexes cannot do this.

## Open next questions

1. Persist the sv structures (row-order samples, mark bits, 2-bit text, exceptions) with the
   same identity binding as the persisted8 table, then measure fresh-process break-even
   against persisted8 and the suffix array.
2. Settle the absent-query regression with a persisted8 A/A control in the protocol itself.
3. Repeat on the pooled corpus, whose 19 MB index does not fit one L3 slice, and on a quiet
   machine.
4. Verify small intervals (2–4 rows) the same way; most present 20/31-mers end above one
   row.

## Replay

```sh
sh research/explore-singleton-verify-973e687a/cc_sv.sh   # build/sv.dylib (+ trace and mutant builds)
sh research/explore-singleton-verify-973e687a/run_all.sh # controls, dev timing, freeze, evaluation, certificate
python tools/verify_count.py research/explore-singleton-verify-973e687a/certificate/candidate.json
```

`run_all.sh` overwrites this package's outputs. Replay in a copy. Timings will differ by
machine and load.

## Provenance and credit

Written in a session donated by VibeCodyH (GitHub) and run by Claude
(Anthropic, claude-opus-5-5). No prior involvement in this project. Builds on the project's
round-two persisted8 method, its suffix-array control, its query generator and its witness
checker (Douglas Colkitt / @Mister-Meeseeks and the project's preparation agent); Heng Li's
Ropebwt3 (rld0 rank functions; the sentinel LF walk follows `ssa.c`); Ilya Grebnov's
libsais (suffix-array control); the FM-index and sampled-suffix-array locate of Ferragina
and Manzini (2000); and the ENA/INSDC accession records. PR #5 reported the picker's
hex-seed rejection that this session reproduced.
