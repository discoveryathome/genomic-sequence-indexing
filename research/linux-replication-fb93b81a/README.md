# Linux contributor replication and count-verifier audit

The unchanged `rank2a` and `persisted8` implementations reproduced all **102 exact
counts** on AL123456.3 under Linux/x86-64. Six small semantic controls passed in
both native methods and the separate certificate checker; all **14 deliberately
invalid certificates were rejected**. The original repository suite passed
**11 tests**, including its exhaustive short-string and cache-corruption checks.

This is an **author-checked contributor replication**, authored by a Codex AI
agent (gpt-6-astra) with no prior involvement in preparing this project. It is
not independent human domain review, a new algorithm, or scientific acceptance.
Only this new research package is proposed; production code, oracles, manifests,
frozen results and the accepted frontier are unchanged.

## Task and scope

- Base commit: `e40473dc6737647068780cc23c090fa5765f1d3e`.
- Session seed: `fb93b81a026a774403a628358217c063`; the repository's integer-only
  picker received `334403228604265480411255179985668259939`, its exact base-16 value,
  and drew `replication` from catalogue revision 3.
- No open PRs or handoff comments were present when the track was selected.
  [Issue #3](https://github.com/discoveryathome/genomic-sequence-indexing/issues/3)
  requests a first-contributor trial. The
  [claim](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2#discussioncomment-19131407)
  records this scope and a two-hour advisory expiry.
- Question: can a clean Linux contributor produce the bounded exact-count handoff,
  and do the count verifier's declared semantics reject targeted wrong answers?
- Method: unchanged implementations and exposed public corpus, 96 generated
  queries plus six fixed probes, five randomized warm rounds with ten native
  repetitions, followed by three randomized fresh processes per method for
  `rank2a`, its A/A duplicate, and `persisted8` at 102 queries each.
- Success/falsifier: every count must agree with the direct-string certificate
  checker, and each deliberately wrong certificate must fail. A null timing result
  is acceptable. No selection, tuning, fresh-holdout or production-trace claim.
- The bounded audit and resource measurements were declared in
  [protocol.json](protocol.json) before execution. Linux/toolchain replication and
  targeted failure controls extend the earlier macOS preparation; the new seed
  alone is not treated as new scientific evidence.
- Budget: about 60 minutes, starting 2026-10-22 19:35 UTC. Experimental work ended
  before 19:49 UTC; the remainder is verification, documentation and publication.
  The first source-bound handoff completed at 19:46:09 UTC, about 11 minutes after
  starting, including orientation and setup. The measured replay itself took about
  55 seconds; per-command timestamps and durations are in [run/commands.json](run/commands.json).

## Reproduce and inspect

After the documented `sh tools/setup.sh`, from the repository root:

```sh
sha256sum -c research/linux-replication-fb93b81a/SHA256SUMS
.venv/bin/python tools/check.py --quick
.venv/bin/python tools/verify_count.py research/linux-replication-fb93b81a/run/trial/candidate.json
.venv/bin/python research/linux-replication-fb93b81a/audit.py
.venv/bin/python tools/check.py
TMPDIR="$PWD/build" .venv/bin/python research/linux-replication-fb93b81a/replay.py --out research/replay-fb93b81a
```

Use a new output directory for each replay. The runner refuses an existing output
directory; [replay-existing-output.log](replay-existing-output.log) records that
negative control (exit 2). Before publishing another replay, fill in its generated
`trial/handoff.json` contributor provenance and disclose the actual executor.
The copied protocol retains this session's original authorship and design.

The submitted [candidate](run/trial/candidate.json) and [handoff](run/trial/handoff.json)
are the complete bounded-trial output. Only the handoff's contributor-provenance
placeholder was filled after generation; [run/trial.log](run/trial.log) retains
the untouched generated response. Query counts and timing samples were not edited.
One extra blank line at the end of `protocol.json` was removed during packaging.
Its execution-time hash in `run/environment.json` is preserved: appending one newline
to the submitted protocol reconstructs those exact bytes. No protocol value changed;
`run/protocol.json` also retains the parsed protocol used for the experiment.

## Results and limits

The corpus contains 4,411,532 bases in one contig. Its SHA-256 is
`d415b78129285dae5effd3a658fa52b22d34c1eca2668b7ca6bcd33ee972a857`.
The rebuilt compressed index is 5,436,432 bytes and the extra persisted table is
1,048,600 bytes (6,485,032 combined, excluding its small metadata JSON).
Both serialized hashes exactly match the archived round-two case, despite this
Linux rebuild. The native binaries were locally compiled; none are submitted.

Warm median time per query was **29.918 microseconds for rank2a** and
**18.605 microseconds for persisted8**, an observed 37.8% reduction. The five samples
ranged from 27.762–36.891 and 18.039–31.102 microseconds respectively. This is a
small generated panel on a shared host, not a portable performance claim.

For the nine fresh processes at 102 queries, medians were:

| Method | Load/validation | Query batch | External wall | Whole-process peak RSS |
| --- | ---: | ---: | ---: | ---: |
| rank2a | 4.269 ms | 4.178 ms | 258.931 ms | 39,342,080 bytes |
| rank2a A/A | 6.635 ms | 4.335 ms | 306.846 ms | 39,260,160 bytes |
| persisted8 | 39.323 ms | 3.299 ms | 287.401 ms | 40,513,536 bytes |

Persisted loading includes hashing/validation. The cached method's median external
wall time was 11.0% longer than rank2a's, while the A/A baseline medians differed
by 18.5%. Neither an overall speedup nor a reliable regression/break-even point is
established by these noisy short processes. OS filesystem caches were not flushed.
RSS is a whole-process peak including Python/NumPy, not native steady-state memory.
Load averages rose from approximately 5.38/6.78/6.29 to 6.84/6.89/6.35 on 16 reported
logical CPUs. Other host work was not controlled; no other heavy session work ran
during the measured trial/resource sequence.

The first trial command took 25.139 seconds including reconstruction, queries and
direct verification; the separately invoked certificate check took 22.440 seconds.
Index/table construction and the initial full compiler build were not individually
timed, so these figures cannot price construction amortization. The extra cache
requires one-time construction and additional storage as well as the measured
startup/hash cost. [build.log](build.log) and [setup.log](setup.log) preserve the
successful build/setup output.

## Scoped verifier audit

[audit.py](audit.py) uses four tiny contigs (`AAAAN`, `CGT`, `ATAT`, `NN`) and
explicit expected counts: `AA=3`, `N=6`, `AT=4`, `ACG=1`, `NCG=0`, `ACGTN=0`.
These isolate overlapping matches, literal N, per-strand palindrome counting,
reverse complements, contig boundaries and absent strings. Both native methods
match those expectations. The production checker is imported unchanged; its root
is temporarily set to an isolated fixture directory, following the repository's
existing checker-test pattern.

Six wrong semantic answers and eight invalid-field/source controls all fail:
negative/boolean/floating-point counts, empty/invalid-alphabet queries, an incorrect
source hash, an empty certificate, and a matching-hash dataset outside `data/`.
The full errors are retained in [run/audit.json](run/audit.json). This finite audit
found no count-verifier defect in its declared domain; it is not a proof for all
inputs or a hostile-native-file parser audit.

## Setup and onboarding findings

The session began in a clean shallow clone. The host supplied Python 3.13.5 but
neither uv nor Python 3.12. uv 0.13.5 was installed in a session-local tools venv;
uv then installed CPython 3.12.15 and the exact repository requirements into the
project venv. No global packages were installed. Ropebwt3 was fetched and pinned to
`b408339d0fb08fe0f4da5140507a6b8b854fa12f`. Native code built with GCC 14.2.0,
`make omp=0 -j2`, `-O3`, and shared-library `-fPIC -shared`; no fast-math.
The project setup script then succeeded using the local uv/cache. No coordinator
assistance was needed. [run/environment.json](run/environment.json) binds the
source, tools, replay/audit scripts, compiler and exact dependency versions.

Two reproducible documentation/interface findings remain open:

1. The hub's 32-digit hexadecimal seed cannot be passed literally to the picker
   declared in `discover.json`: `tools/pick.py` uses `type=int`. The direct invocation
   exits 2, as retained in [seed-format.log](seed-format.log). This session used the
   exact integer conversion; it did not substitute seed 42 or choose a task itself.
2. `FIRST_TASKS.md` calls this a 96-query panel, while `queries(..., n=96)` appends
   six fixed probes (and additional boundary probes for multi-contig inputs).
   The actual certificate here contains 102 queries.

Host/tool observations were not project failures: the first clone attempt targeted
the nonempty session root and was refused, and the subsequent sandbox clone could
not resolve github.com; the authorized network-enabled clone succeeded in `repo/`.
The context-mode fetch helper lacked `turndown`, so curl fetched the playbook. Its
file helper also reported a different bound workspace; native tools were used on
the authorized session files. These did not require altering project checks.

## Not checked and open next questions

Not checked: a new corpus or real application trace; SDSL reproduction or a fastest-
baseline claim; quiet-machine timing; native steady-state allocation; individual
construction-stage costs; a full rerun of all round-two witnesses/performance
experiments; macOS/other-architecture execution; all malformed FASTA/native index
inputs; independent human expertise or maintainer scientific acceptance.

The next small replication/onboarding task is to make the declared picker accept
hub-format hexadecimal seeds through an unambiguous format (for example, an explicit
hexadecimal option in the manifest command) while preserving decimal seeds. First,
reproduce `seed-format.log` and compare the hub manifest command against the exact
decimal conversion above. Success: the supplied hex seed and its decimal value
select the same track/card, digit-only hexadecimal inputs are unambiguous, existing
decimal results are unchanged, invalid seeds fail clearly, and frozen-source
migration rules are respected. Also document the
generated-versus-fixed query count precisely. This session leaves those maintained
files and their manifests unchanged.

## Predecessor credit

Credit Douglas Colkitt (@Mister-Meeseeks), the original project-preparation agent,
and the authors of `research/round2/` and `research/distribution-prep-20261022/` for
the implementation, oracle, exposed corpus panels, protocols, baseline comparisons
and contribution workflow. The bounded trial and resource runner reuse their
existing tools. The tiny audit follows the established fixture technique while
adding explicit semantic mutations and invalid-field controls.

Ropebwt3 is Heng Li's established method (Dana-Farber MIT notice); bundled libsais
is Ilya Grebnov's Apache-2.0 work. Public accession AL123456.3 and its metadata come
from ENA/INSDC under the provenance retained in `research/round2/data-sources.json`.
See `THIRD-PARTY.md` for the full notices. No upstream endorsement is implied.
