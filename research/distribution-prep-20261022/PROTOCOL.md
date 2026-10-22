# Distribution preparation compressed-baseline protocol

Author-run exact-string software calibration; no biological-effect inference.
Use SDSL 2.1.1 commit 0546faf0552142f06ff4b201b671a5769dd007ad with a Huffman
wavelet-tree FM-index, RRR(63) compressed bitvectors and SA/ISA sampling 32/64.
This is an established second compressed-index family, not a claim that this
configuration is today's fastest index. Only build compatibility fixes are allowed.

One exposed reference corpus AL123456.3 plus a tiny multi-contig semantic control.
Both strands are indexed separately, literal N and overlapping matches count,
and a distinct non-query separator prevents cross-contig matches. SDSL reserves
byte zero; encode bases as 1..5 and boundaries as 6. Compare every query with the
direct-string oracle and existing rank2a/persisted8 methods.

Freeze generated queries at seed 221043 before timing. Use 96 generated long
queries, inherited controls, and short length 1/4/7/8/9 probes. These are software
workload probes, not a real application's query trace or an independent holdout.
Report construction time, serialized index size, load time and warm timings.
Seven randomized paired timing rounds include rank2a A/A. Batch break-even estimates
must be labeled estimates; an actual process-cost trial remains separate.
No retuning the SDSL configuration or cache on this evaluation.

Keep library code/binaries in ignored build directories. GPLv3 and bundled
component terms apply to the locally linked SDSL comparator; pilot source release
contains only our adapter and reproducible build instructions.
