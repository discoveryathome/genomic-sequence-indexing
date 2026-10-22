# Canonical sequence-query workload, seed 5eda2181

This package specifies a real software operation: Jellyfish `query -s` against
an exact canonical k-mer database. It supplies an ordered, repeat-preserving
21-mer replay fixture and checks the subset that matches this project's
both-strand exact-count semantics. **The fixture is extracted from an already
exposed public reference; it is not a captured application or production trace.**

The contribution is confined to this directory. Base:
`e40473dc6737647068780cc23c090fa5765f1d3e`; catalogue revision 3; drawn track
`workload`. OS-generated seed `5eda2181903384ad1a017421b2132463`, passed to the
current integer-only picker as `126080031903520692497811457829816706147`.
There was no matching open workload handoff.
[Claim](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2#discussioncomment-19132161).

## Sourced workload contract

Jellyfish is pinned to `43b1ab27abdb8c9399c386cc998bb9fd33648412`.
[source-hashes.json](source-hashes.json) binds the inspected primary-source files.
The following distinguishes documented behavior from choices made for this replay.

| Dimension | Documented operation | This fixture |
| --- | --- | --- |
| Query lengths | `query` reads k from the database header. The official guide demonstrates canonical k=21. | Fixed k=21, step 1. This is a chosen documented example, not a universal application default. |
| Batch size | `-s` visits all valid windows of the supplied sequence files. Its parser's 4096 buffer parameter is not an application query-batch measurement. | First 100,000 emitted windows of one reference record. The complete file has 4,641,632 valid windows. Neither number is measured production traffic. |
| Repeats/order | The sequence iterator emits each window; the query loop performs one lookup per emission without deduplication. | FASTA record order, then increasing zero-based start; preserve every repeated canonical key. |
| Canonicalization | Database canonical flag chooses the lexicographically smaller word/reverse complement. | ACGT-only canonical keys; counts refer to the entire reference, not only the query prefix. |
| Ambiguity/boundaries | Invalid bases reset the iterator. The parser inserts an invalid separator between records. | Skip every non-ACGT-containing window, never bridge an ambiguity or record boundary. Literal-N queries are outside this adapter's domain. |
| Memory | Sequence querying maps the database and normally requests preloading. The documented hash size is an entry count, not a byte ceiling. No production RAM budget was established. | Proposed 256 MiB replay-process target; measured peak RSS, no hard cap. Not a Jellyfish or application memory requirement. |
| Provenance/permission | Source inspection establishes a software workflow, not permission to publish someone else's trace. | Existing public U00096.3 reference, already in this repository; no external user data or contact. No production trace obtained. |

Primary evidence: [guide's 21-mer example](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/doc/UserGuide.lyx#L119),
[query loop and exact binary/Bloom branches](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/sub_commands/query_main.cc#L46),
[sequence CLI option](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/sub_commands/query_main_cmdline.yaggo#L4),
[canonical iterator and reset](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/include/jellyfish/mer_iterator.hpp#L54),
[base decoding](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/include/jellyfish/mer_dna.hpp#L31), and
[record separator](https://github.com/gmarcais/Jellyfish/blob/43b1ab27abdb8c9399c386cc998bb9fd33648412/include/jellyfish/mer_overlap_sequence_parser.hpp#L172).
The exact binary-database branch is the intended comparator; the Bloom-counter
branch is excluded. Jellyfish itself was not built or executed in this session.

A delegated source check also identified KAT `sect` as an application-level
example of per-position canonical count lookups. Its documented default is 27,
and its implementation batches 1,024 **sequence records**, not 1,024 queries.
Invalid windows receive zero output without a lookup. We retained the original
21-mer Jellyfish protocol; KAT was not run or used as the fixture generator.
[KAT documentation](https://kat.readthedocs.io/en/latest/using.html#sect),
[pinned record-batch constant](https://github.com/TGAC/KAT/blob/ee8473fb438b7a17005d19c2e91067043208870a/src/sect.hpp#L66),
[pinned positional loop](https://github.com/TGAC/KAT/blob/ee8473fb438b7a17005d19c2e91067043208870a/src/sect.cc#L525).

## Semantic boundary

Let F(q) be the overlapping count in the original, separate reference records.
The project returns F(q) + F(reverse-complement(q)). For a non-palindromic key,
this equals the canonical-window count in the original records. An odd-length
ACGT word cannot be its own reverse complement: its middle base would have to
complement itself. Thus the proposed 21-mer subset is compatible.

This does not extend unchanged to even-length palindromes: the record `AT` has
one canonical 2-mer occurrence, while the project's two-strand count of `AT`
is two. Nor does it extend to literal-N queries: the adapter emits no 3-mer
for `NAN`, whereas the project counts the literal query `NAN` once there.
The maintained oracle and native index semantics remain unchanged.

## Evidence and limits

[protocol.json](protocol.json) was recorded before execution. The initial
64-position sample is preserved under [evidence/initial](evidence/initial), with
its source in commit `7fca0c0`. Every sampled count was one. Before expanding
the check, [supplement.json](supplement.json) declared a full-prefix comparison
and a fixed repeated-key control; the seed and original sample were retained.

The prefix contains 99,875 distinct canonical keys, 125 repeated occurrences
after the first, and 86 repeated keys; maximum prefix frequency is three.
Its ordered query hash is
`d825e2d8264520d2a5448a1e49a363fc5593287cdf97e5b126457806e0d1fa6b`
(ASCII query plus LF per emitted window, no headers or deduplication).

All 100,000 positions match a forward canonical-window tally in `rank2a`,
`persisted8`, and the uncompressed `suffix_array` control. This tally shares
the extraction iterator, so it is **not an independent oracle**. The unchanged
direct-string oracle and separate certificate checker additionally cover the
fixed 64 sampled keys and the first repeated key. That repeated key occurs at
prefix ordinals 5,563, 66,622 and 66,707, and has count five in the full reference.
Prefix query frequency and reference occurrence count are different quantities.
Full-prefix reference counts range from one to 81; 2,462 positions have counts
greater than one. No absent-query corpus panel is claimed.

Ten small tests cover ordered overlap/repeats, lowercase normalization,
ambiguity resets, short records and boundaries, invalid k, the even-palindrome
negative control, and exhaustive ACGT queries at k=1,3,5 against the unchanged
oracle (including absent words). The original repository's eleven tests pass.
Corpus native boundary/N behavior is not newly certified here: the corpus is
one ACGT record, and the added boundary/N controls are small Python tests.

The [final full-prefix author run](evidence/final/results.json) took about 31
seconds and peaked near 114 MiB RSS,
below the proposed 256 MiB process target. Exact values, hashes and machine
details are in the result receipt. RSS includes Python, extraction/tally data
and sequential native loads; it excludes build processes, other processes and
system page cache. This is one execution-cost observation, not a steady-state
memory benchmark or throughput comparison. No speedup, break-even point,
production representativeness, independent scientific acceptance, or new
algorithm is claimed. Construction time/RSS and Jellyfish/KAT behavior were not
measured. There was no tuning or randomized timing experiment.

The first full-prefix run is retained in `evidence/full-before-review`; a small
receipt-provenance change then made the repeated-key certificate take its counts
directly from the `persisted8` result vector. The final run exercises that code.
Both full runs give identical deterministic counts and query hashes. Resource
observations are retained separately, not selected or averaged as a benchmark.
See [execution environment and input hashes](evidence/environment.json),
[build output](evidence/build.log), and [21-test output](evidence/final-tests.log).

## Replay

Use the repository's setup environment, or the documented shared parent venv.
From the repository root (each output directory must be new):

```sh
sh tools/build_round2.sh
python tools/rebuild_round2.py --case research/round2/ecoli-case.json --with-sa
python research/canonical-workload-5eda2181/workload.py --output build/workload-replay
python tools/verify_count.py build/workload-replay/certificate.json
python tools/verify_count.py build/workload-replay/repeated-certificate.json
python -m pytest -q research/canonical-workload-5eda2181/test_workload.py
python tools/check.py
```

For comparison with the archived receipt, deterministic fields and hashes must
match; elapsed time, platform and RSS may differ. The 64 positional sample is
generated using CPython 3.12.15 `random.Random` with the exact seed above.
The full-prefix vectors are hashed as ASCII decimal count plus LF per position.
Build uses the repository scripts: Ropebwt3 `make omp=0 -j2`; adapters use
`-O3 -fPIC -shared`, no fast-math. Author compiler: Debian GCC 14.2.0-19.
Pinned Ropebwt3 commit: `b408339d0fb08fe0f4da5140507a6b8b854fa12f`.
Native index/table/suffix-array identities are recorded in results; the 46 MB
uncompressed suffix array is a verification control, not a proposed small index.

## Provenance and credit

The existing `data/development_ecoli.fasta` and original `data/U00096.3.fasta`
have different file encodings but identical parsed sequence records, checked by
the replay. Both file hashes are recorded. See the repository's
[source record](../../data/source.json), [ENA accession](https://www.ebi.ac.uk/ena/browser/view/U00096.3),
and [ENA/INSDC access and reuse policy](https://ena-browser-docs.readthedocs.io/en/latest/about/policies.html).
The query fixture is a deterministic transformation of that already public
reference, not a newly released biological sample. Existing dataset attribution
and [third-party notices](../../THIRD-PARTY.md) are retained.

Credit the original repository contributors and maintainer Douglas Colkitt for
the trial, wrappers, oracle, certificates and frozen evidence; Heng Li and
Ropebwt3 contributors for the index; libsais contributors for the suffix-array
control; and Guillaume Marçais, Carl Kingsford and Jellyfish contributors for
canonical k-mer counting and its documented query operation. KAT contributors
supplied the related application example. This work applies those established
ideas and adds a bounded workload specification and author checks.

The parent coding agent authored [PR #5](https://github.com/discoveryathome/genomic-sequence-indexing/pull/5)
in the preceding session and had seen these references and the project status.
This branch starts directly from upstream main, not from that PR. Delegated
source research and review are part of this same author session; they do not
constitute independent human review or scientific acceptance.

Next useful work on the workload track: run the pinned Jellyfish executable on
a tiny separately generated exact canonical database and compare its emitted
ordered stream/counts with this adapter, including N and multiple records.
A later application-supplied trace still needs explicit publication permission,
observed batch/repeat statistics and a justified application memory budget.
