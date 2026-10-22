# Fixed confirmation before measurement

The main round showed A/A median drift up to 27.5%. Run exactly one additional
pass on the three fresh references and their pool, using the same exposed queries,
unchanged suffix8 candidate and fixed order seed 2026102341. No tuning.

Seven randomized warm rounds per short/long group, >=2000 operations each, compare
rank2a, duplicated rank2a and persisted8. Three randomized fresh-process repeats
per method on 100000 queries compare rank2a/persisted8. Keep all successes and
regressions. OS cache is unflushed; shared-machine load is recorded, not controlled.
This is repeatability evidence on exposed data, not a new holdout or quiet-machine
replication. Retain the original result regardless of this confirmation.
