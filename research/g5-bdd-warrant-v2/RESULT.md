# G5.3 ROBDD result

**Terminal:** `BDD_PARENT_N3_PARITY_SUPPORTED`

- Independent Bryant ROBDD (stdlib unique table + apply). No BDD package.
- Exhaustive n=3: 168/168 legal intervals expand to the antichain; 1344/1344
  revocation liveness checks match **DAG and antichain**.
- Certified-profile ⊕/⊗: 400/400 join and 400/400 meet expand to the antichain.
- Enumeration overflow is `CANNOT_CHECK_OUTPUT_SIZE`, not an approximation.
- ZDD left OPEN. Production `warrant.py` unchanged. No production adoption.

v1 `FACTORED_WARRANT_VALUE_SUPPORTED` is not rewritten.
