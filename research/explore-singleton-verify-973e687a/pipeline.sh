#!/bin/sh
# Development timing, mechanical selection/freeze, then evaluation (protocol.json).
set -eu
cd "$(dirname "$0")/../.."
P=research/explore-singleton-verify-973e687a
H="python $P/sv_run.py"
$H time AL123456.3 2051343105 960 5 $P/dev-timing.json 16:2 16:4 32:2 32:4
$H select $P/dev-timing.json $P/freeze.json
SEL=$(python -c "import json;m=json.load(open('$P/freeze.json'))['selected'];print(m[2:].replace('_d',':') if m else '')")
[ -n "$SEL" ] || { echo "no eligible config; stopping per protocol"; exit 3; }
$H time AL123456.3 2537449594 96 7 $P/eval-panel-timing.json "$SEL"
$H time AL123456.3 2537449594 960 5 $P/eval-groups-timing.json "$SEL"
$H cert AL123456.3 2537449594 "$SEL" $P/certificate
