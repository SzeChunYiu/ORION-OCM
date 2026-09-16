# PASS-L58 — applied downgrade of the confirmed OVERSTRONG claim

**Finding (registered, #939 verdict table):** CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1
is the corpus's one confirmed OVERSTRONG — "The universal phrasing 'for any two
capabilities' exceeds a pure 27x27 finite classification once the rules rest on unproven
equalities (joint=sum / joint=max)." The applied downgrade was the missing step (ledger L58).

**Applied action (commit b2b5a9d9, this PR):**
1. Section 2 reworded: Theorem CI is now headed and scoped as a "27x27 finite
   classification at registered scope" over the 729 ordered / 351 unordered pairs of the
   frozen 27-row A4 contract; the universal "for any two capabilities" phrasing is gone
   (0 occurrences post-edit).
2. Mandatory joint-burden caveat attached (Section 2 note + Section 5): joint=sum /
   joint=max are DEFINING classification criteria under the A4 frozen accounting at
   registered scope, not proven resource accounting for arbitrary implementations.
3. PVR-3 no-interference inheritance scoped to Theorem IF's (tranche 3) bounded finite
   scope — inherited, not re-proved.
4. MANIFEST.json audit_trail entry: finding -> verdict -> new wording -> controls.

**Verification:** defect-clause re-check post-edit (universal phrase count 0; 27x27
scoping present in header/Section 2/Section 5; caveat present twice); controls
`python3 -I -B test_interactions.py` 27/27 pass at pre-edit and post-edit states; custody
check: no test/executor reads the .md (frozen verdict records referencing the theorem id
are records about the pre-edit state and are not edited). Consistency: ARRIVAL_21
(capability-bounds-interactions) already records the overlap-only rule as "explicitly
retracted" — this downgrade aligns the unified theorem with that registered position.

**FIN2UNIV population:** nothing to do (0 downgrades, #949 adjudicated all 283 PROPER).

**Claim:** the one confirmed unsupported overclaim in the corpus now carries its registered
disposition as an applied edit; one claim only; no other object touched.
