"""Bounded semantic and rejection controls; leaves the production checker unchanged."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "src")]
import verify_count
from trial import encode
from round2_index import close, create_cache, evaluate, libraries, load


def audit():
    # Explicit expected counts avoid sharing the production oracle's algorithm.
    controls = [
        ("overlap", "AA", 3, 2),
        ("literal-N", "N", 6, 28),
        ("palindrome-both-strands", "AT", 4, 2),
        ("reverse-complement", "ACG", 1, 0),
        ("contig-boundary", "NCG", 0, 1),
        ("absent", "ACGTN", 0, 1),
    ]
    raw = b">a\nAAAAN\n>b\nCGT\n>c\nATAT\n>d\nNN\n"
    report = {"fixture_sha256": hashlib.sha256(raw).hexdigest(),
              "controls": [{"name": n, "query": q, "expected": c}
                           for n, q, c, _ in controls],
              "rejections": [], "native_methods": {}}
    with tempfile.TemporaryDirectory(prefix="replication-audit-", dir=ROOT / "build") as tmp:
        work = Path(tmp)
        (work / "data").mkdir()
        fasta = work / "data/tiny.fa"
        fasta.write_bytes(raw)
        cert = {"dataset": "data/tiny.fa", "dataset_sha256": report["fixture_sha256"],
                "queries": [{"sequence": q, "count": c} for _, q, c, _ in controls]}
        certificate = work / "candidate.json"
        original_root = verify_count.ROOT
        verify_count.ROOT = work
        try:
            certificate.write_text(json.dumps(cert))
            report["positive_certificate"] = verify_count.check(certificate)
            mutations = []
            for i, (name, _, _, wrong) in enumerate(controls):
                bad = deepcopy(cert)
                bad["queries"][i]["count"] = wrong
                mutations.append(("semantic-" + name, bad))
            for name, field, value in [
                ("negative-count", "count", -1),
                ("boolean-count", "count", True),
                ("nonintegral-count", "count", 3.0),
                ("empty-query", "sequence", ""),
                ("invalid-alphabet", "sequence", "A."),
            ]:
                bad = deepcopy(cert)
                bad["queries"][0][field] = value
                mutations.append((name, bad))
            for name, field, value in [
                ("wrong-hash", "dataset_sha256", "0" * 64),
                ("empty-certificate", "queries", []),
                ("outside-data-path", "dataset", "outside.fa"),
            ]:
                bad = deepcopy(cert)
                bad[field] = value
                mutations.append((name, bad))
            (work / "outside.fa").write_bytes(raw)
            for name, bad in mutations:
                certificate.write_text(json.dumps(bad))
                try:
                    verify_count.check(certificate)
                except ValueError as error:
                    report["rejections"].append({"name": name, "error": str(error)})
                else:
                    raise AssertionError("Invalid certificate accepted: " + name)
        finally:
            verify_count.ROOT = original_root

        index, table = work / "tiny.fmd", work / "tiny.cache"
        subprocess.run([str(ROOT / "vendor/ropebwt3/ropebwt3"), "build", "-t1", "-d",
                        "-o", str(index), str(fasta)], check=True, capture_output=True)
        libs = libraries()
        create_cache(index, table, libs)
        queries = [q for _, q, _, _ in controls]
        expected = [c for _, _, c, _ in controls]
        for method in ("rank2a", "persisted8"):
            pointer = load(method, index, table, work / "unused.sa", libs)
            try:
                actual = evaluate(method, pointer, encode(queries), libs)[0].tolist()
            finally:
                close(method, pointer, libs)
            assert actual == expected, (method, actual, expected)
            report["native_methods"][method] = actual
    report["passed"] = True
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
