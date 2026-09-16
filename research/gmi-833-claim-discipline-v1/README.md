# gmi-833-claim-discipline-v1

Claim-discipline registration tranche for GMI #833 line 34: "Require every result to
state scope, quantifiers, assumptions, falsifiers, strongest parents, and forbidden
extrapolations."

**Deliverables**

- `FREEZE_V1.md` - tranche freeze: universe (234 objects in 4 tranches + typed
  exclusions), the uniform scan rule (S1 score-record status / S2 package-docs
  extraction), status taxonomy, no-boilerplate contract, tranche falsifiers.
- `scan_registers_v1.py` -> `GAP_REGISTER_V1.json` - mechanical S1 scan of all scored
  objects (deterministic; byte-identical under -I -B / -I -O -B).
- `assemble_v1.py` + `authored_g6_v1.py` + `authored_overrides_v1.py` + `evidence/`
  -> `REGISTRATIONS_V1.json` - per-object registration of all five field pairs for
  all 234 objects; every EXTRACTED item carries a file:line citation, every DERIVED
  item carries its basis, every REGISTERED_GAP (8 slots / 7 objects) a typed reason.
- `REGISTRATIONS_TABLE_V1.md` - human-readable per-package index (make_table_v1.py).
- `MATURE_RESCORE_BRIDGE.md` - the seven G6 analytic proofs re-scored under the
  rescore-v2 rubric WITH registered falsifiers: M0/EV0 -> M1/EV1 each (corpus at
  frozen v2 scope: M0 48->41, M1 30->37, EV0 46->39, EV1 30->37). The rescore-v2
  package is NOT modified.
- `ISSUE_833_ADJUDICATION.md` - line-34 coverage adjudication and tick decision.
- `REPORTED_NOT_FIXED.md` - census proof-mode disagreement recount (62 scorer / 99
  equivalence-mapped / 172 raw), MIM M0-M6 terminology collision (G4), crosshand
  consumption record.
- `test_claim_discipline_v1.py` - package invariants (universe, field validity, gap
  enumeration, no-boilerplate, G7-not-bridged, rescore-unmodified).

**Coverage:** 1170 field slots = 394 CARRIED + 713 EXTRACTED + 59 DERIVED + 8
REGISTERED_GAP. Scan base SHA in RESULT_V1.json.

**Standing rules honored:** no boilerplate registrations (cross-object duplicate
check enforces it); every citation verified to exist; rescore packages untouched;
checkbox ticked only with the residual precisely enumerated and owned.
