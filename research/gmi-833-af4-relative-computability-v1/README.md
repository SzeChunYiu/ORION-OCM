# gmi-833-af4-relative-computability-v1

Freeze-first AF4 tranche for issue #833.

Reproduce from repository root:

```bash
PKG=research/gmi-833-af4-relative-computability-v1
python3 -I -B "$PKG/af4_relative_computability_v1.py" --output /tmp/result.json
cmp "$PKG/RESULT_V1.json" /tmp/result.json
python3 -I -B "$PKG/independent_oracle_v1.py" --output /tmp/oracle.json
cmp "$PKG/ORACLE_RESULT_V1.json" /tmp/oracle.json
python3 -I -B "$PKG/test_af4_relative_computability_v1.py"
python3 -I -O -B "$PKG/test_af4_relative_computability_v1.py"
python3 -I -B "$PKG/check_reconciliation_v1.py" --mode static-check
```

The executor validates a parent-derived registry/corollary table. It is not a halting oracle and does not prove the parent Turing-jump or incompleteness theorems.
