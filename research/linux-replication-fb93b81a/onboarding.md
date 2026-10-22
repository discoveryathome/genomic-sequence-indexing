# Setup and command receipt

These are the material setup/execution commands, in order. Paths below are relative
to the session folder, with the repository at `repo/`; commands without a `repo/`
prefix are explicitly labelled when their working directory was the repository.
No global installs or committed binaries were used. The first checked handoff
completed at 2026-10-22 19:46:09 UTC, about 11 minutes after session start. Initial
setup stages were not individually instrumented; this is end-to-end onboarding
time including orientation, not an isolated installer benchmark.

1. `git clone https://github.com/discoveryathome/genomic-sequence-indexing.git .`
   was refused because the initial workspace was nonempty. A clone to
   `genomic-sequence-indexing` then failed to resolve github.com in the command
   sandbox. Neither produced experimental results.
2. The authorized network-enabled command
   `git clone --depth 1 https://github.com/discoveryathome/genomic-sequence-indexing.git repo`
   succeeded inside `session-fb93b81a/`, at
   `e40473dc6737647068780cc23c090fa5765f1d3e`.
3. `python3 -m venv tools-env`, then
   `tools-env/bin/python -m pip install --cache-dir pip-cache uv` succeeded.
   System Python was 3.13.5; uv resolved to 0.13.5. Python 3.12 and uv were initially absent.
4. `git clone https://github.com/lh3/ropebwt3.git repo/vendor/ropebwt3`, then
   `git -C repo/vendor/ropebwt3 checkout --detach b408339d0fb08fe0f4da5140507a6b8b854fa12f`
   supplied the pinned dependency. Repository and dependency build instructions
   were screened before executing them; no agent hooks/settings were loaded.
5. `python3 tools/check.py --quick` (cwd `repo/`) passed under the system interpreter;
   see `initial-quick.log`. All experimental results instead use the exact local
   Python 3.12 environment prepared next.
6. `UV_CACHE_DIR=uv-cache UV_PYTHON_INSTALL_DIR=python tools-env/bin/uv venv repo/.venv --python 3.12`
   installed CPython 3.12.15 inside the session and created the project venv.
7. `UV_CACHE_DIR=uv-cache tools-env/bin/uv pip install --python repo/.venv/bin/python -r repo/requirements.txt`
   succeeded with all four pinned versions unchanged. The full resolved environment
   is retained in `dependencies.txt`.
8. `sh tools/build_round2.sh` (cwd `repo/`) succeeded in the workspace sandbox;
   see `build.log`. No compile warnings/errors were emitted.
9. `PATH="../tools-env/bin:$PATH" UV_CACHE_DIR="../uv-cache" UV_PYTHON_INSTALL_DIR="../python" sh tools/setup.sh`
   (cwd `repo/`) succeeded with the installed local tools/cache; see `setup.log`.
   This was an idempotency check, not a fresh-build timing measurement.
10. `TMPDIR="<session>/tmp" .venv/bin/python research/linux-replication-fb93b81a/replay.py --out research/linux-replication-fb93b81a/run`
    (cwd `repo/`) passed. `run/commands.json` records all 15 subprocess argument
    vectors, timestamps, elapsed times and return codes. Logs retain every response.
11. `.venv/bin/python tools/pick.py --seed fb93b81a026a774403a628358217c063`
    (cwd `repo/`) returned the expected argparse error (exit 2); see `seed-format.log`.
12. Repeating the replay command with its existing output directory returned the
    expected refusal (exit 2); see `replay-existing-output.log`. It did not overwrite evidence.
13. The first `tools-env/bin/uv pip freeze --python repo/.venv/bin/python` export
    omitted the local cache setting and was refused by the sandbox's read-only
    home cache (exit 2); see `dependency-export-failure.log`. The retry with
    `UV_CACHE_DIR=uv-cache` succeeded. This was an artifact-export failure; no
    environment packages or measured results changed.

There were no failed experimental counts, failed native builds, dependency-version
substitutions or requests for coordinator help. The template's contributor
provenance was filled after generation; all other handoff fields match `run/trial.log`.
Author checks confirmed the 15 successful commands, 102 certificate entries, six
semantic controls, 14 rejected certificates, nine zero-mismatch resource processes,
and unchanged implementation/audit/replay source hashes. The protocol's trailing
blank line was normalized after execution as documented in README.md. Upstream `main` was refreshed before submission and
still matched the pinned base. No tuning followed the observations.
