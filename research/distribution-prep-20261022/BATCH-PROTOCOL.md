# Actual fresh-process cache break-even follow-up

Fixed follow-up after the component-cost comparison: no retuning. Use its exposed
107-query panel on AL123456.3; repeat cyclically to create batches of 1, 100,
10,000 and 100,000 queries. Three randomized paired fresh processes per method
(rank2a, duplicated rank2a_AA, persisted8), RNG seed 221044. Exactly 36 runs.
Use the unchanged round2_process.py measurement and verifier; preserve stdout,
external wall time, RSS and preparation/load/query decomposition. Filesystem
caches remain unflushed. No production trace or cross-workload break-even claim.
