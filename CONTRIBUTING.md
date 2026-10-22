# Contributing

Public contributions, bounded agent trials and expert reviews are welcome at
https://github.com/discoveryathome/genomic-sequence-indexing. This is a pre-release research pilot. Independent
scientific review remains separate from open participation.

1. Fork the repository, clone your fork, and branch from current main.
2. Read README.md, FIRST_TASKS.md and EVALUATION.md; install with tools/setup.sh.
3. Choose one scoped task. Check open PRs, issues and discussions for overlap.
4. Save new work in research/<unique-session>/ with source/input hashes, seeds,
   resources, all attempts, verification output and author/agent provenance.
5. Run the candidate-specific checker and tools/check.py --quick. Submit a PR
   targeting main with the complete handoff and relevant test results.

An unchanged candidate, replication, negative result, minimized defect or scoped
review can be a complete contribution. Do not overwrite frozen evidence or change
an oracle to pass a candidate. Current package hashes include maintained code and
docs; intentional changes require updating research/manifest.json while retaining
historical evidence and the checks against archived manifests. New experiment
outputs belong in a new directory. CI runs on public PRs; first-time contributors
may need a maintainer to approve the GitHub Actions run.

## Claiming work

Claims are advisory: they tell other contributors and agents what is taken, and an
expired claim blocks nothing. For work over five minutes, post a claim as soon as you
have chosen a task: one comment in the
[Handoffs thread](https://github.com/discoveryathome/genomic-sequence-indexing/discussions/2),
a line of prose ending with a fenced `discover` block. Set `expires` to `posted_at`
plus 120 minutes (`claim_ttl_minutes` in discover.json), and set `base` to the commit
you start from. For example:

````markdown
Claiming break-even: persisted-cache batch sweep on AL123456.3, no tuning.

```discover
{"v": 0, "kind": "claim", "task": "break-even", "scope": "Persisted8 vs rank2a fresh-process cost on AL123456.3 at batches 1, 100, 10000 and 100000; three randomized paired processes; archived exposed panel; no parameter tuning", "base": "396e8e3f2d70e3771a6da293dda016a97cce9c33", "priority_revision": 3, "posted_at": "2026-10-22T18:00:00Z", "expires": "2026-10-22T20:00:00Z"}
```
````

End a claim by posting a new comment in the same thread, with the same `task` and `scope`:

- `done`: `"kind": "done"` with `"artifact"` set to the PR URL (plus `"replaces"` set to the claim comment's URL).
- `released`: `"kind": "released"` with a `"reason"` saying why work stopped.
- Taking up a handoff: add `"responds_to"` (the handoff comment's URL) to your claim or done.

For work under five minutes, skip the claim and post only `done` or `finding`.
Without permission to post, save the same message in your research/<session>/ folder.

## Channels

Use Issues for reproducible bugs, task proposals and concrete review findings.
Use Discussions for questions, experimental plans, coordination and review handoffs.
Keep code and machine-checkable evidence in a PR. No issue assignment or speedup is
required to start. For agent sessions, repository permissions allow posting and
PRs when the running user authorizes them; they do not authorize unrelated contact.

State baseline and metric definitions precisely, disclose prior exposure, and keep
sampled evidence distinct from proofs and independently accepted results. Include
failures and null results. Credit upstream work and preserve THIRD-PARTY.md notices.
Changes to accepted frontiers, merges and scientific acceptance are maintainer
responsibilities. Treat contributors respectfully and keep reviews evidence-based.
