# Source and data provenance

Pilot-owned wrapper, tests and docs are MIT. Ropebwt3 is pinned in
research/sources.json and fetched into an ignored vendor checkout. Its root license
is MIT (Dana-Farber Cancer Institute); bundled libsais is Apache-2.0 and individual
file notices must be retained. We link its rld0 code without modifying it. No
upstream endorsement is implied. The suffix-interval lookup technique is known.

Public bacterial sequences U00096.3 (E. coli K-12 MG1655) and AL009126.3
(B. subtilis 168) were fetched from the European Nucleotide Archive; source URLs,
accessions, headers and byte hashes are in data/source.json and
holdout-source.json. ENA/INSDC states a policy of free and unrestricted access to
records. These are accessioned bacterial reference sequences, not human subjects
or restricted-access patient data. Source metadata are retained, not relicensed
as pilot-owned MIT code.

The derived panel contains eight synthetic mutated copies of a 250 kb E. coli
segment (0.5% substitutions) and two artificial low-complexity/N controls. It is
not eight independent sampled genomes and cannot support population claims.
Queries are locally generated synthetic exact strings, not real sequencing reads.
Both strands are indexed; palindromic hits are counted once per indexed strand.

## Round-two computational indexing data and control

Additional public accession records and exact response hashes are listed in
research/round2/data-sources.json. Headers and original files are retained, under
the ENA/INSDC reuse policy linked above. AE000511.1 is retained as an excluded
input because it contains symbols beyond the declared literal A/C/G/T/N alphabet.
The supported pool concatenates the three eligible records with contig boundaries
preserved; it is not an independent biological cohort.

The second architectural control is pilot-owned conventional suffix-array binary
search using the existing pinned Ropebwt3 copy of libsais for construction. Libsais
is Apache-2.0 (Ilya Grebnov); no vendor source or native library is bundled in our
source distribution. This is an uncompressed index control, not a claim to beat
optimized production compressed indexes.

All round-two queries are generated count-query workloads, not experimental
protocols, engineered sequences for biological use or biological-effect predictions.
