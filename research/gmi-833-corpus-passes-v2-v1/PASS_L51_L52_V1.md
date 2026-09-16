# PASS-L51 / PASS-L52 — hidden iid/stationarity and hidden finite-horizon assumptions

## L51 — hidden independence/iid/stationarity

**Detector:** term/structure scan (iid, i.i.d., stationarity, ergodicity, exchangeability,
time-homogeneity, drift-free, memoryless, fixed-iid-proposal phrasings) over the 7,196
computational-mode census objects; flag when the term appears in the claim while the
package's registration docs lack it. Plants pass (real corpus phrases "fixed iid proposals
with mass p>0" / "exact normalized iid kernels" match; clean text does not).

**7 flags -> 7 REGISTERED_EXPLICIT, 0 hidden.** Every flag's property is declared in the
package's own theorem/scope line, e.g.: adaptive-row-confidence Scope declares "stationary
conditional row laws"; PCA-1 "Fix a deterministic stationary policy... in this finite
stationary scope"; F2 ceilings formalization states the exchangeable perfect-check premise;
T602-19 declares "for iid bounded observations" in-statement; the grand-unification
transfer theorem declares "exactly N iid draws ... only needs within-row iidness".

**False-positive cause recorded:** the screen's registration filter keyed on
FREEZE/ASSUMPTION/RESULT/RECEIPT/README/CORE filenames; this corpus registers premises in
THEOREM/FORMALIZATION docs. **Residual limitation:** word-level screening only — structural
presupposition without the vocabulary is out of mechanical reach; the standing coverage
mechanism is the L34 registration retrofit (in flight, not duplicated here).

## L52 — hidden finite-horizon assumptions

**Detector:** horizon/budget tokens in justification/scope/citations vs the statement, over
all 197 P2 rows (plants pass: "budget <= 7 steps", "8-step budget" match; clean does not).

**3 flags -> 3 DECLARED_HORIZON, 0 hidden:**
- F2-U: "T=2" is the compute-channel parameter of a witness; T is an explicit theorem
  parameter (A^T bound), not a hidden horizon.
- CA-2: statement quantifies over "arbitrary finite history-dependent policies"; the
  horizon-two 390,625-kernel check is a control under the induction proof.
- COST-LABEL: scope is explicitly finite; the termination bound is a derived output.

**Census-side:** 1,336 UNIVERSAL-quantifier objects are statement-side-only
SCREENED-NOT-ADJUDICATED (census objects carry no evidence/justification field — the
evidence-side horizon check is not mechanically possible at P1 scope). False-positive
classes recorded: T-as-channel-variable, control-at-horizon-N, derived-termination-bound.

**Claim:** no hidden iid/stationarity or finite-horizon defect confirmed in either pass's
readable population at frozen scope; both detector layers + their false-positive classes
are registered for the census-refresh round.
