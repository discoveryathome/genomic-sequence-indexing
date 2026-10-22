#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
make -C vendor/ropebwt3 omp=0 -j2
mkdir -p build
"${CC:-cc}" -O3 -fPIC -shared -Ivendor/ropebwt3 src/count.c vendor/ropebwt3/rld0.c -o build/count.dylib
