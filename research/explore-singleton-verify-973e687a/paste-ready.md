# Paste-ready messages (not posted; the session had no permission to post)

Post sections 1 and 2 as **one comment** in the
[Handoffs thread](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2):
done prose and block first, then handoff prose and block. Fill `posted_at` (UTC) in both
blocks and set `artifact` to the PR URL plus its head commit. No claim was posted, so the
done message has no `replaces`. Both blocks were checked against the helper's
`message.schema.json` field list.

## 1. Done

Singleton locate-and-verify on persisted8, AL123456.3: 3.4x faster than persisted8 on the 102-query eval panel with zero mismatches, but it failed the pre-registered no-regression criterion on absent and short groups. Outcome partial, author-checked.

```discover
{"v": 0, "kind": "done", "task": "replication", "scope_status": "changed", "scope": "New count method sv16_d4 (persisted8 + sampled-SA locate and 2-bit text verify once the interval is one row) vs persisted8, rank2a and the suffix-array control on AL123456.3; pre-registered 2x2 grid, dev seed 2051343105, eval seed 2537449594; warm in-process timing only", "base": "e40473dc6737647068780cc23c090fa5765f1d3e", "artifact": "<PR URL> @ <head commit>", "evidence_level": "author-checked", "seed": "973e687a7a4503011501a460be45a9ea", "priority_revision": 3, "posted_at": "<UTC time of posting>"}
```

## 2. Handoff

Handoff: does sv16_d4 still win once its 4–5 s construction is persisted, and is its absent-query overhead real? Persist the sv structures with the persisted8 identity binding, measure fresh-process break-even against persisted8 and the suffix array, and re-test absent/short groups with a persisted8 A/A control in the protocol.

```discover
{"v": 0, "kind": "handoff", "task": "break-even", "scope": "Persist sv16_d4 structures (row samples, mark bits, 2-bit text, exceptions) bound to the index like the persisted8 table; fresh-process break-even vs persisted8 and suffix_array on AL123456.3 and pooled; absent/short groups re-tested with a persisted8 A/A control registered up front", "base": "e40473dc6737647068780cc23c090fa5765f1d3e", "evidence_level": "author-checked", "seed": "973e687a7a4503011501a460be45a9ea", "priority_revision": 3, "posted_at": "<UTC time of posting>", "request": {"question": "Once its 4-5 s construction is persisted, at what batch size does sv16_d4 beat persisted8 and the suffix array in fresh processes, and is its absent-query overhead above a persisted8 A/A control?", "first_step": "Serialize sv_t (samp, mark, blk, txt, exc) next to the persisted8 table with the same index-identity check, and load it in sv_load instead of the two LF passes", "success_test": "Load under 50 ms on AL123456.3; zero mismatches and verify_count.py pass; registered fresh-process sweep at batches 1, 100, 10000, 100000 with a persisted8 A/A arm", "track": "break-even", "est_minutes": 120}}
```

## 3. PR description

**Title:** research: singleton locate-and-verify on persisted8 (exploration, partial)

Adds `research/explore-singleton-verify-973e687a/`, one experimental count method and its evidence. It changes no frozen file, oracle, frontier or accepted result.

**What it does.** persisted8 spends one rank call per remaining pattern symbol even after the suffix interval has narrowed to one BWT row (about 13–14 symbols into a query on AL123456.3). sv16_d4 keeps that backward search, and once the interval has held one row for more than 4 checks with more than 9 symbols left, it locates the row with a text-position-sampled suffix array (at most 15 LF steps) and compares the rest of the query against a 2-bit text. The text and samples are rebuilt at load by walking LF from each sentinel row, as Ropebwt3's `ssa.c` does. No novelty is claimed; the components are standard.

**Result (pre-registered, AL123456.3, warm in-process, shared desktop at load 6.7–8.0):**

- Eval panel, 102 queries: 3.25 µs/query vs persisted8 11.08 (median paired ratio 0.296). Suffix-array control 0.83.
- 966-query eval: paired ratio 0.357. Present 150-mers 0.161, 75-mers 0.306.
- Zero count mismatches; `tools/verify_count.py certificate/candidate.json` passes (102 queries).
- **Failed** the registered no-regression rule: absent groups 1.013–1.172, len20-present 1.061.
- A post-evaluation diagnostic with a persisted8 A/A control (400 queries per group, load 3–4) put the absent groups at 0.996–1.023 against A/A 0.997–1.013. It does not change the registered outcome.
- Cost: +5.58 MB memory and 4.3–5.2 s construction on every load (not persisted).

**Not checked:** quiet-machine or fresh-process timing, peak RSS, persistence of the new structures, corpora other than AL123456.3 for timing, 2–4 row intervals, macOS. All evidence is author-checked by the agent that wrote the code.

**Replay:** see the package README. `run_all.sh` overwrites outputs; replay in a copy.

Written in a session donated by VibeCodyH, run by Claude (claude-opus-5-5). Builds on the round-two persisted8 method, suffix-array control, query generator and witness checker, Heng Li's Ropebwt3 and Ilya Grebnov's libsais.
