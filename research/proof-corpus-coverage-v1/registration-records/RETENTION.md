# Exact retention boundary

registration-derived.tar.gz retains 24 original files, 28,386,436 raw bytes,
including the byte-identical SEAL.json, full POPULATION.json, assignments, source
snapshots, policy, registration receipt and Git metadata spools. Its original
seal is 9d02378c93369da33ccd8940509474422d898bee899c42ce28e7bc6958362a2e.

supporting.tar.gz retains 31 files, 102,603 raw bytes: the outer process envelope,
58-test qualification/source snapshots, raw development logs, independent audit
and packaging recipe. Both archives use sorted regular members, uid/gid 0, mode
0644, mtime 0 and gzip without a filename and with mtime 0. No files are extracted
or executed by the guard. Per-archive maps bind every member's bytes and SHA256.

Exactly four files from the original 28-file registration tree are omitted:
inputs/CORPUS_SOURCE.json, inputs/GRAPH.json, inputs/SOLUTIONS.json and
inputs/WRAPPERS.json, totaling 401,351,933 bytes. OMITTED.json binds their exact
original and sealed-copy paths, hashes, sizes and prior archive members.
The existing external prior archive is 61,338,019 bytes with SHA256
c1177f5a3725b21d91f74a52faf6c98839800052ababa254cc173bff154d27fb.
The full original registration remains intact at the manifest's original_root.

Packaging rehashed all original/sealed-copy bytes and the prior archive's four
matching members. The portable guard checks the omission descriptors and stored
derived records; it does not fetch, parse or independently revalidate omitted
raw metadata. This reduced package cannot satisfy a live full-directory custody
API requiring those four physical input files.

Original outer registration wall time was 4.716977859963663 s; its inner
4.040809753001668 s excludes final sealing and must not be added again.
Original RSS fields are explicitly nonaggregate. Successful archive preparation
was 2.7835568419541232 s before manifest creation. Costs concern apparatus, not
knowledge acquisition, theorem solving or a lifetime cognition comparison.

The first packaging attempt used Python 3.8.10 and stopped at an unsupported
str.removesuffix call after writing the first archive. The partial directory
and failure record remain external under registration-records-preparation-failure-v1.
The unchanged script succeeded under the pinned standalone Python 3.11.14.
Guard v1 receipts are retained separately from the repaired v2 qualification.
