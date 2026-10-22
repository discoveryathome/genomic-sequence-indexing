#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sh tools/build.sh
cc="${CC:-cc}"
"$cc" -O3 -fPIC -shared -Ivendor/ropebwt3 src/cache.c vendor/ropebwt3/rld0.c -o build/cache.dylib
"$cc" -O3 -fPIC -shared -Ivendor/ropebwt3 src/suffix_array.c vendor/ropebwt3/libsais.c -o build/suffix_array.dylib
