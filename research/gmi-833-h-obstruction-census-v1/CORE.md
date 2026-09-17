# GMI #833 Section H obstruction census V1

This package answers the aggregate question “which families cannot be
recovered and why?” only for a frozen finite registry of operational hallmark
contracts.  One common family-name-free Boolean grammar, one ecology, one cost
budget, and one complete search rule classify all 43 named Section H rows.

The result is exact: 36 registered hallmark contracts are not recoverable—21
by an analytic expressivity obstruction, 9 by exact resource lower bounds, and
6 by non-identifiability.  Seven controls are uniquely recovered.  The primary
bit-table implementation and source-separated tuple-table oracle agree.

This is a diagnostic census, not a family derivation result.  It proves no
universal non-recoverability and closes none of the 43 named family rows.  The
frozen mapping from names to hallmark contracts is a disclosed post-hoc
evaluation prior.  The aggregate Issue #833 obstruction-quantification row is
the only row eligible for reconciliation.

Run:

```bash
python3 obstruction_census_v1.py --check
python3 independent_oracle_v1.py --check
python3 -m unittest -v test_obstruction_census_v1.py
python3 -O -m unittest -v test_obstruction_census_v1.py
```

