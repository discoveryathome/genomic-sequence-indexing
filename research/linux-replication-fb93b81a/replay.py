"""Replay this fixed Linux replication into a new research directory."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    dest = (ROOT / args.out).resolve()
    if dest.exists() or not dest.is_relative_to(ROOT / "research"):
        parser.error("Choose a new directory under research/")
    dest.mkdir(parents=True)
    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    (dest / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    seed = int(protocol["seed_decimal"])
    commands = []

    def run(label, command):
        started = time.perf_counter()
        stamp = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=300)
        elapsed = time.perf_counter() - started
        (dest / (label + ".log")).write_text(result.stdout + result.stderr)
        commands.append({"label": label, "argv": command, "started_at": stamp,
                         "elapsed_seconds": elapsed, "returncode": result.returncode})
        (dest / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if result.returncode:
            raise RuntimeError(f"{label} failed; see {dest / (label + '.log')}")
        return result.stdout, elapsed

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    sources = [ROOT / p for p in ("tools/contribute.py", "tools/verify_count.py",
               "tools/round2_process.py", "tools/rebuild_round2.py", "tools/build.sh",
               "tools/build_round2.sh", "src/trial.py", "src/round2_index.py",
               "src/cache.c", "src/count.c", "src/suffix_array.c", "research/sources.json")]
    sources += [PACKAGE / p for p in ("protocol.json", "audit.py", "replay.py")]
    environment = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "cpu_count": os.cpu_count(), "load_average_start": os.getloadavg(),
        "compiler": subprocess.check_output(["cc", "--version"], text=True).splitlines()[0],
        "dependencies": {name: importlib.metadata.version(name)
                         for name in ("numpy", "mpmath", "pytest", "jsonschema")},
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
        "compiler_flags": {"ropebwt3": "make omp=0 -j2; -g -Wall -Wc++-compat -O3",
                           "wrappers": "-O3 -fPIC -shared -Ivendor/ropebwt3; no fast-math"},
        "authorship": protocol["authorship"], "exposure": protocol["exposure"],
    }
    (dest / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    run("quick", [sys.executable, "tools/check.py", "--quick"])
    run("picker", [sys.executable, "tools/pick.py", "--seed", str(seed)])
    run("trial", [sys.executable, "tools/contribute.py", "--case", protocol["case"],
                  "--seed", str(seed), "--out", str((dest / "trial").relative_to(ROOT))])
    run("certificate", [sys.executable, "tools/verify_count.py", str(dest / "trial/candidate.json")])
    audit, _ = run("audit", [sys.executable, str(PACKAGE / "audit.py")])
    (dest / "audit.json").write_text(audit)
    archived = json.loads((ROOT / "research/round2/AL123456.3-case.json").read_text())
    case = {key: archived[key] for key in ("name", "dataset", "dataset_sha256", "index",
                                          "table", "suffix_array")}
    certificate = json.loads((dest / "trial/candidate.json").read_text())
    case["queries"] = certificate["queries"]
    case_path = dest / "measurement-case.json"
    case_path.write_text(json.dumps(case, indent=2) + "\n")
    rng = random.Random(seed)
    rows = []
    for repeat in range(3):
        methods = ["rank2a", "rank2a_AA", "persisted8"]
        rng.shuffle(methods)
        for method in methods:
            output, elapsed = run(f"resource-{repeat}-{method}",
                [sys.executable, "tools/round2_process.py", str(case_path), method, "102"])
            rows.append({**json.loads(output), "repeat": repeat, "external_wall_seconds": elapsed})
    artifacts = [ROOT / case[key] for key in ("index", "table")]
    artifacts += list((ROOT / "build").glob("*.dylib"))
    resources = {"rows": rows, "load_average_end": os.getloadavg(),
                 "artifacts": {str(p.relative_to(ROOT)): {"bytes": p.stat().st_size, "sha256": digest(p)}
                               for p in artifacts},
                 "limit": "Fresh processes, unflushed filesystem cache, shared host; whole-process RSS is not native allocation size."}
    (dest / "resources.json").write_text(json.dumps(resources, indent=2) + "\n")
    run("full-check", [sys.executable, "tools/check.py"])
    print(json.dumps({"output": str(dest.relative_to(ROOT)), "commands": len(commands), "passed": True}))


if __name__ == "__main__":
    main()
