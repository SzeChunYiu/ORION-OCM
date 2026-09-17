# gmi-novel-intelligence-w4-prospective-v1

Revival package for ticket **REV-L47-NOVEL-INTELLIGENCE-W4**: prospective
re-establishment of the novel-intelligence W4 claim after the corpus passes
v2 L47 adjudication of the parent package (`gmi-novel-intelligence-w4-v1`)
as POST_HOC_SUSPECT (freeze document committed 89 min after the green
result; double-verified, independently re-verified — the defect is
permanent and recorded, not erased).

What this package re-earns is prospective-ness of the CONTENT at the
original claim strength, per the registered revival lever: the
family-member search is re-run from the parent's pre-existing frozen seed
under the NEW freeze `FREEZE_V2_PROSPECTIVE.{md,json}`, committed before
any executor/result of this package existed (CI enforces the add-order).

## Claim ceilings (unchanged from the parent package)

```text
W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE
NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE
```

Not claimed: `NEW_DOMAIN`/J4, `NEW_FORM_OF_INTELLIGENCE_PROVEN`,
phase-hole occupancy, P4 surviving-unseen-domain. The budget-derived
extended held-out {6,7,8} and the negative-control family G(k) corroborate
the claim at its registered scope F(k), k in {2,3,4}; they do not widen it.

## Artifacts

- `FREEZE_V2_PROSPECTIVE.md` / `.json` — prospective custody (committed
  first): hypothesis, registered predictions, negative control, independent
  route, determinism protocol, decision rule D1-D5
- `novel_intelligence_w4_prospective_v1.py` — replication executor
  (imports the parent W4 + upstream V6 witnesses for the re-run legs)
- `independent_route_v1.py` — no-import verification route (fiber counting,
  first-occurrence canonical labeling, pigeonhole bounds, brute-force
  tightness witnesses)
- `make_multihost_receipt_v1.py` — completes D5 across two hosts
- `test_novel_intelligence_w4_prospective_v1.py` — unit + checker-validation
  + CI-scope campaign tests
- `RESULT_V1.json` / `RUNTIME_V1.json` / `RECEIPT_MULTIHOST_V1.json` —
  campaign receipt (deterministic content only), runtime charging, two-host
  protocol record (produced off-Mac; see RUNTIME for hosts)

## Run

```bash
python test_novel_intelligence_w4_prospective_v1.py -v   # unit + CI scope
python novel_intelligence_w4_prospective_v1.py --scope full --protocol
python make_multihost_receipt_v1.py --primary-result RESULT_V1.json \
  --primary-runtime RUNTIME_V1.json --secondary-result RESULT_HOST2.json \
  --secondary-runtime RUNTIME_HOST2.json --out RECEIPT_MULTIHOST_V1.json
```

Requires sibling packages `research/gmi-novel-intelligence-w4-v1/` and
`research/gmi-unseen-form-prediction-v1/` (read-only).
