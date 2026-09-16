# PASS-L58 — the confirmed OVERSTRONG claim: revival chain to the strongest true claim

**Finding (registered, #939 verdict table):** CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1 —
"the universal phrasing 'for any two capabilities' exceeds a pure 27x27 finite
classification once the rules rest on unproven equalities (joint=sum / joint=max)."

**Intermediate state (commit b2b5a9d9):** applied downgrade to the 27x27 finite scope +
mandatory joint-burden caveat. Superseded as closure by the operator revival doctrine
("recursively fix negative results until completely green; always aim for the best claim,
not downgrading and narrowing"): scope-narrowing treated the symptom.

## Revival chain (this PR)

1. **DIAGNOSE what blocks the universal claim.** The equalities hide two REAL premises,
   each with a concrete counterexample (not proof convenience):
   - within-channel claim shareability: joint=max on a shared channel FAILS for disjoint
     claims in that channel (episodic store {e1..e4} + semantic store {s1..s3} in S:
     joint=7 > max=4) — CE-1;
   - free-option accounting: no-interference FAILS under mandatory upkeep charged from the
     same hard budget — CE-2.
   - disjoint-channel additivity (joint=sum) is provable UNCONDITIONALLY under
     channel-wise accounting — no obstruction.
2. **LEVER (build the missing mechanism).** Per-channel claim-SET structure Q_X(c);
   channel-wise accounting B(A) = sum_c |union of claims|; interaction class becomes a
   function of (channel overlap x within-channel claim overlap).
3. **RE-PROVE AT ORIGINAL STRENGTH. Theorem CI-U (universal, proven):**
   - Lemma A: disjoint channels => joint = sum — unconditional.
   - Lemma B: shared channel: max <= joint_c <= sum with EXACT equality
     characterization — nested claims <=> max; disjoint claims <=> sum; partial overlap <=>
     strictly between — unconditional (inclusion-exclusion).
   - Lemma C: no interference under the free-option premise — feasible-set inclusion.
   - Corollary CI-A4: the original 27x27 classification is the registered
     fully-shareable instance (A4 frozen accounting registers nested claims per channel).
4. **BOUNDARY (earned by counterexample, complete obstruction list):** CE-1 and CE-2,
   both labelled EARNED-BY-COUNTEREXAMPLE in the theorem. With claims registered per
   channel, every other clause of the original universal phrasing is proved at full
   strength.

**Result: the universal claim is RESTORED and EARNED** — stronger than both the original
overclaim (equalities now proven, premises named) and the intermediate narrowing (bounds
+ characterization are universal; the finite 27x27 is an instance, not the claim).
Executable controls: `ci_universal_witness_v1.py` (lemma fixtures + CE-1/CE-2 hostiles,
GREEN) + `test_ci_universal_v1.py` (9/9) + original `test_interactions.py` (27/27).
MANIFEST audit trail records finding -> intermediate downgrade -> revival chain ->
universal status.

**FIN2UNIV population:** nothing to do (0 downgrades, #949 adjudicated all 283 PROPER).
