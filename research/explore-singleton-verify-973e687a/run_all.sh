#!/bin/sh
# Correctness controls (trace build, off-by-one mutant), then pipeline.sh.
set -eu
cd "$(dirname "$0")/../.."
P=research/explore-singleton-verify-973e687a
SV_LIB=sv_trace.dylib python $P/sv_run.py check repetitive > $P/check-trace-repetitive.json
SV_LIB=sv_mutant.dylib python $P/sv_run.py check repetitive > $P/check-mutant-repetitive.json
SV_LIB=sv_trace.dylib python $P/sv_run.py check AL123456.3 > $P/check-trace-AL123456.3.json
sh $P/pipeline.sh
