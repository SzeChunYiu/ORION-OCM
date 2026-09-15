# Symbolic selector derivation V1

This bundle closes issue #602 B14's remaining formal gap: deriving selectors as well as emitters.

- [Formal theorem](SYMBOLIC_SELECTOR_DERIVATION_THEOREM_V1.md)
- [Machine-readable disposition](SELECTOR_DERIVATION_LEDGER_V1.json)
- [Issue #602 six-row reconciliation](ISSUE_602_FORMAL_RECONCILIATION_V1.md)
- [Exact enumerator](selector_derivation_v1.py)
- [Hostile controls](test_selector_derivation_v1.py)
- [Cross-artifact fail-closed validator](validate_issue_602_reconciliation_v1.py)

Run from this directory:

```bash
python3 -m unittest -v test_selector_derivation_v1.py
python3 validate_issue_602_reconciliation_v1.py
python3 selector_derivation_v1.py
```

Expected terminal: seven tests pass and the JSON result reports the XOR/MUX selector-family reversal. No empirical, prospective, real-scale, universal-selector, or new-domain claim is made.
