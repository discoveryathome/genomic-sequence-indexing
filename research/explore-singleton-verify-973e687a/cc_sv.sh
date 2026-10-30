#!/bin/sh
# Compile the exploration candidate next to the pilot's native libraries,
# plus a trace build (counts locate calls) and an off-by-one mutant for controls.
set -eu
cd "$(dirname "$0")/../.."
F="-O3 -fPIC -shared -Wall -Isrc -Ivendor/ropebwt3"
SRC="research/explore-singleton-verify-973e687a/sv.c vendor/ropebwt3/rld0.c"
"${CC:-cc}" $F $SRC -o build/sv.dylib
"${CC:-cc}" $F -DSV_TRACE $SRC -o build/sv_trace.dylib
"${CC:-cc}" $F -DSV_TRACE -DSV_MUTANT $SRC -o build/sv_mutant.dylib
