# Portable native evidence

The three archives preserve 1,327 files and 41,861,955 raw bytes in 6,764,607
compressed bytes: all 1,203 development files, all 123 qualification files and
the original independent review. Every archive was regenerated twice with
identical bytes and read back against original member hashes. No additional raw
file was omitted.

Read [the archive index](native-records/CORE.md) and
[the authored result](NATIVE-QUALIFICATION.md). Large executables, toolchain and
compiled inputs remain explicitly hash-bound external prerequisites, as before;
the archive is not a standalone native execution image.

From this directory, run the stdlib-only portable custody audit:

```sh
python3 -I -S native_evidence.py --seal-sha256 523531c5bb7ca79b4f3ff5d5e6316960cef38dcddcd82dc335421341280ffe2e
```

Expected terminal: ARCHIVE_CUSTODY_PASS, with 1,327 archive members and 47 current
source bindings. It checks every sealed file, every regular archive member,
count/byte/hash identity and registered current source. It neither follows
archived absolute paths nor extracts files onto the filesystem. Current source
paths must resolve inside the repository research directory.

The final actual run used system Python 3.8 from /tmp with -I -S and passed.
[Its exact process envelope](NATIVE-ARCHIVE-VALIDATION.json) retains raw streams.
Eighteen authored controls cover member tampering, missing/extra/duplicate paths,
links/traversal, replaced seals, current-source drift, malformed duplicate JSON,
Boolean counts and inconsistent index bindings; clean cases pass.

The initial package seal, source bindings, guard and real byte-review receipt are
preserved inside native-records. Three guard-only gaps were reproduced and repaired
before the successor seal above. PACKAGING_SUCCESSION.json retains exact
development/validation logs. Archive payloads and native sources never changed.

This audit establishes byte custody and current registered source identity.
It does not rerun or independently re-establish kernel outcomes, validate omitted
host binaries, qualify the evaluator build profile, or produce corpus, learning,
scaling or FLT results.
