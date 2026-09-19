# gmi-833-af5-verification-barriers-v1

Freeze-first AF5 verification-contract programme.

```bash
PKG=research/gmi-833-af5-verification-barriers-v1
python3 -I -B "$PKG/af5_verification_barriers_v1.py" --output /tmp/result.json
cmp "$PKG/RESULT_V1.json" /tmp/result.json
python3 -I -B "$PKG/independent_oracle_v1.py" --output /tmp/oracle.json
cmp "$PKG/ORACLE_RESULT_V1.json" /tmp/oracle.json
python3 -I -B "$PKG/test_af5_verification_barriers_v1.py"
python3 -I -O -B "$PKG/test_af5_verification_barriers_v1.py"
```
