# G5.3 ZDD result

**Terminal:** `ZDD_PARENT_N3_PARITY_SUPPORTED`

- Independent Minato ZDD (stdlib unique table + apply; hi=0 nodes suppressed).
  No ZDD package.
- Exhaustive n=3: 168/168 legal intervals expand to the antichain; 1344/1344
  revocation liveness checks match **DAG, ROBDD and antichain**.
- Certified-profile ⊕/⊗: 400/400 join (family OR) and 400/400 meet (family
  product) expand to the antichain. Family XOR is implemented and is **not**
  warrant ⊕ (caught by mutant).
- Enumeration overflow is `CANNOT_CHECK_OUTPUT_SIZE`, not an approximation.
- Production `warrant.py` unchanged. No production adoption.
  `PHYSICAL_DENOMINATOR_CLEAN` is not claimed.

v1 `FACTORED_WARRANT_VALUE_SUPPORTED` and v2 `BDD_PARENT_N3_PARITY_SUPPORTED`
are not rewritten. GitHub #165 G5.3 checkboxes are not ticked.
