# Static operation

From this directory, with Python3.12:

```sh
python3 -I -B -m unittest discover -s . -p 'test_*.py'
python3 -I -O -B -m unittest discover -s . -p 'test_*.py'
python3 -I -B replay_v1.py
python3 -I -B scan_retained_v1.py /path/to/retained/json-directory
```

Replay validates complete manifest membership before and after the checker,
retaining the initial manifest and whole REPAIR_RECEIPT_V1.json bytes.
Direct check_consumer_repair_v1.py emits that same full payload.
The active gmi_microscope/b6_dense_consumer_scan.py delegates to this CLI
after checking that its adjacent VM/IR match the bound source. Invocation
does not evaluate genotypes or import the native VM. Incomplete/unknown
input returns exit2; source-contract drift refuses execution.
The source packet contains earlier raw records unchanged; it does not
authenticate the host or reconstruct the newly reported677-cell archive.
