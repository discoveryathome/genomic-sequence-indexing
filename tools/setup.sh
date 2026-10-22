#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python tools/fetch_upstream.py
sh tools/build.sh
printf "Setup complete. Activate with: source .venv/bin/activate\n"
