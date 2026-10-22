"""Replay a bounded, ordered canonical-query fixture; no throughput claim."""
from collections import Counter
from itertools import islice
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def reverse_complement(word):
    return word.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def windows(records, k):
    """Yield (record, start, canonical word), including repeated occurrences."""
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    for record, sequence in enumerate(records):
        sequence = sequence.upper()
        run = 0
        for end, base in enumerate(sequence):
            run = run + 1 if base in "ACGT" else 0
            if run >= k:
                start = end - k + 1
                word = sequence[start:end + 1]
                yield record, start, min(word, reverse_complement(word))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory for generated evidence")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]
    from trial import read_fasta, oracle, encode
    from round2_index import digest, libraries, load, evaluate, close
    from verify_count import check

    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    case = json.loads((ROOT / "research/round2/ecoli-case.json").read_text())
    reference = ROOT / protocol["reference"]["path"]
    if digest(reference) != protocol["reference"]["sha256"]:
        raise ValueError("Reference identity mismatch")
    records = read_fasta(reference)
    accession = ROOT / "data/U00096.3.fasta"
    if records != read_fasta(accession):
        raise ValueError("Fixture differs from the accession sequence records")
    k = protocol["stream"]["k"]
    if k % 2 != 1:
        raise ValueError("Both-strand compatibility requires odd k for this adapter")
    prefix = list(islice(windows(records, k),
                         protocol["stream"]["fixture_prefix_queries"]))
    frequency = Counter(word for _, _, word in prefix)
    stream_hash = hashlib.sha256()
    for _, _, word in prefix:
        stream_hash.update((word + "\n").encode("ascii"))
    rng = random.Random(int(protocol["seed_hex"], 16))
    positions = sorted(rng.sample(range(len(prefix)),
                                  protocol["stream"]["oracle_sample_queries"]))
    sample = [{"ordinal": i, "record": prefix[i][0], "start": prefix[i][1],
               "sequence": prefix[i][2]} for i in positions]
    qs = [item["sequence"] for item in sample]
    # Independently count canonical windows in forward records. The project's
    # oracle instead searches each original record and its reverse complement.
    canonical_counts = dict.fromkeys(frequency, 0)
    full_windows = 0
    for _, _, word in windows(records, k):
        full_windows += 1
        if word in canonical_counts:
            canonical_counts[word] += 1
    expected = [oracle(records, q) for q in qs]
    if expected != [canonical_counts[q] for q in qs]:
        raise ValueError("Canonical and both-strand semantics disagree")
    generation_and_oracle_seconds = time.perf_counter() - started
    libs = libraries()
    all_qs = [word for _, _, word in prefix]
    full_expected = [canonical_counts[q] for q in all_qs]
    encoded = encode(all_qs)
    repeated_key = next(word for _, _, word in prefix if frequency[word] > 1)
    repeated_ordinals = [i for i, (_, _, q) in enumerate(prefix) if q == repeated_key]
    repeated_native = {}
    native = {}
    full_native = {}
    for method in ("rank2a", "persisted8", "suffix_array"):
        pointer = load(method, ROOT / case["index"], ROOT / case["table"],
                       ROOT / case["suffix_array"], libs)
        try:
            counts, _ = evaluate(method, pointer, encoded, libs)
            values = counts.tolist()
            native[method] = [values[i] for i in positions]
            repeated_native[method] = [values[i] for i in repeated_ordinals]
        finally:
            close(method, pointer, libs)
        mismatches = sum(a != b for a, b in zip(values, full_expected))
        if mismatches or len(values) != len(full_expected):
            raise ValueError(f"{method} disagrees with canonical-window tally")
        full_native[method] = {
            "queries": len(values), "mismatches": mismatches,
            "ordered_lf_counts_sha256": hashlib.sha256(
                "".join(f"{n}\n" for n in values).encode("ascii")).hexdigest()}
        if native[method] != expected:
            raise ValueError(f"{method} sample disagrees with the direct oracle")
    for item, count in zip(sample, native["persisted8"]):
        item["count"] = count
    certificate = {"dataset": str(reference.relative_to(ROOT)),
                   "dataset_sha256": digest(reference), "queries": sample}
    cert_path = args.output / "certificate.json"
    cert_path.write_text(json.dumps(certificate, indent=2) + "\n")
    verified = check(cert_path)
    repeated_count = oracle(records, repeated_key)
    if repeated_count != canonical_counts[repeated_key]:
        raise ValueError("Repeated-key oracle mismatch")
    repeated_certificate = {
        "dataset": certificate["dataset"], "dataset_sha256": digest(reference),
        "queries": [{"sequence": repeated_key, "count": count,
                     "ordinal": i} for i, count in
                    zip(repeated_ordinals, repeated_native["persisted8"])]}
    repeated_path = args.output / "repeated-certificate.json"
    repeated_path.write_text(json.dumps(repeated_certificate, indent=2) + "\n")
    repeated_verified = check(repeated_path)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_bytes = peak if sys.platform == "darwin" else peak * 1024
    budget = protocol["resources"]["proposed_process_memory_budget_bytes"]
    results = {
        "evidence_level": "author-checked deterministic fixture, not a production trace",
        "k": k, "records": len(records), "bases": sum(map(len, records)),
        "accession_file_sha256": digest(accession),
        "fixture_file_sha256": digest(reference),
        "same_sequence_records_as_accession": True,
        "full_valid_windows": full_windows,
        "prefix": {"queries": len(prefix), "unique_keys": len(frequency),
                   "repeated_occurrences_after_first": len(prefix) - len(frequency),
                   "keys_repeated": sum(n > 1 for n in frequency.values()),
                   "max_key_frequency": max(frequency.values()),
                   "ordered_lf_query_sha256": stream_hash.hexdigest(),
                   "first_location": list(prefix[0][:2]),
                   "last_location": list(prefix[-1][:2])},
        "sample_queries": len(sample), "sample_unique_keys": len(set(qs)),
        "canonical_forward_window_counts": [canonical_counts[q] for q in qs],
        "direct_both_strand_counts": expected, "native_counts": native,
        "certificate_check": verified,
        "full_prefix_native_check": full_native,
        "full_prefix_expected_count_distribution": dict(sorted(Counter(full_expected).items())),
        "repeated_key_control": {"sequence": repeated_key,
                                 "prefix_ordinals": repeated_ordinals,
                                 "full_reference_count": repeated_count,
                                 "native_counts": repeated_native,
                                 "certificate_check": repeated_verified},
        "native_artifact_sha256": {key: digest(ROOT / case[key])
                                   for key in ("index", "table", "suffix_array")},
        "resources": {"generation_and_oracle_seconds": generation_and_oracle_seconds,
                      "total_seconds": time.perf_counter() - started,
                      "process_peak_rss_bytes": peak_bytes,
                      "proposed_budget_bytes": budget,
                      "within_proposed_budget": peak_bytes <= budget,
                      "scope": "Replay Python process including native index loads; excludes native build, shell and other processes; no hard memory cap imposed"},
        "environment": {"python": sys.version, "platform": platform.platform()},
    }
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"queries": len(prefix), "checked": len(sample),
                      "native_methods": list(native), "peak_rss_bytes": peak_bytes,
                      "within_proposed_budget": peak_bytes <= budget}))
    if peak_bytes > budget:
        raise SystemExit("Replay exceeds the proposed process-memory budget")


if __name__ == "__main__":
    main()
