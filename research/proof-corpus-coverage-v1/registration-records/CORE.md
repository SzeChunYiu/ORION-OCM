# Registration evidence

The original registration fixed all 29,511 entries, selected its first four, and
left every workload stage NOT_DISPATCHED. This is registration apparatus only.

Run the portable record guard from this package with Python 3.11 or newer:

```sh
python3 -I -S registration_evidence.py
```

It checks two authenticated archives, the original seal, the full stored ordering,
four assignments/cursor, and 18 current source, document, test and recorder files.
It returns DERIVED_REGISTRATION_RECORDS_PASS only after these checks.
RECORD_REJECTED exits 1; unavailable evidence returns CANNOT_CHECK and exits 2.
No Git, Lean runtime, network, registrar or proof process is invoked.

- [Retention and limits](RETENTION.md): exact external inputs and custody scope.
- [Manifest](MANIFEST.json): authenticated derived/supporting archives and maps.
- [Omissions](OMITTED.json): precisely four original input files.
- [Guard qualification](GUARD_QUALIFICATION.json): 47 portable controls and CLI.
- [Independent review](guard/registration-independent-final-review-v1.json).
- [Package inventory](PACKAGE_SEAL.json): all record-package files except itself.

The 58 original registrar tests and new 47 record-guard controls are separate.
Neither count is a new run of the earlier native environment control matrix.
No real-corpus build, semantic coverage, reconstruction, learning or FLT result
is established by these records.
