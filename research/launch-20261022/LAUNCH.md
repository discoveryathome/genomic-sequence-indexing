# Hub launch, 2026-10-22

The maintainer, Douglas Colkitt (@Mister-Meeseeks), consented to listing on the
Discovery@Home hub (discoveryathome/discover). `discover.json` now records that consent
in `hubs` and declares review capacity as `surge`; `paused` stays false and the
owner's review note is kept. Entry and status documents gained launch facts only
(maintainer named, listed on the hub, coordination threads linked); the owner's
participation wording is unchanged. Scientific acceptance and independent review
remain pending. Priority weights are unchanged.

Every edited bound file is saved under prior-files/ at its pre-launch content
(base commit in base-commit.txt). `research/manifest.json` rebinds those paths to
their current hashes and keeps the pre-launch values under
`rebound.original_sha256`; `tools/check.py` verifies each saved copy against that
value. Dated receipts (round reports, logs, MIGRATION.md, research/PROTOCOL.md and
earlier prior-files/ snapshots) are unchanged; the distribution-preparation
snapshot gained a copy of discover/priority-log.md, which it had bound at its then
current content, following the precedent of the publication migration.

Follow-up the same day: CONTRIBUTING.md gained a "Claiming work" section (a
schema-valid claim example for the Handoffs thread) and AGENTS.md a pointer to it;
its pre-launch copy is saved and rebound the same way.

Third-party audit for the launch: no stored papers, PDFs or HTML snapshots. Stored
genomes are INSDC/ENA records (free and unrestricted access and redistribution);
derived panels and queries are pilot-generated; the SDSL compatibility patch is a
diff against GPLv3 sources and keeps that license. Nothing was removed.
