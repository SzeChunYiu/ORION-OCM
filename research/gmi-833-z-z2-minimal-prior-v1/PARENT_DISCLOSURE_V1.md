# Z2 parent-ownership disclosure

Assimilation-first: the strongest parent for each claim is named, absorbed, and
credited, and the residual contribution of this tranche is stated afterwards.
Nothing below is claimed novel except what section 3 lists.

## 1. Literature parents

| parent | what it owns | what this package does not claim |
|---|---|---|
| Wolpert & Macready, *No Free Lunch Theorems for Optimization*, IEEE Trans. Evol. Comput. 1(1):67-82, 1997, doi:10.1109/4235.585893 | the averaged-performance identity: over a closed, permutation-symmetric class of objectives every non-repeating search performs identically | this package proves **no** universal no-free-lunch theorem; `MP-1` is an exact statement about one registered encoding's induced measure |
| Mitchell, *The Need for Biases in Learning Generalizations*, Rutgers CBM-TR-117, 1980 | that a learner with no bias cannot generalize beyond its observations | `MP-3` is the exact finite instance of that proposition on one registered universe and one frozen prediction family, with the accuracy numbers attached; the proposition is Mitchell's |
| Moore, *Gedanken-experiments on sequential machines*, Automata Studies, Princeton UP, 1956 | the Moore machine and its defining property (output a function of state alone) | `MP-6` recovers the family from a generic vocabulary; the family and its property are Moore's |
| Mealy, *A method for synthesizing sequential circuits*, Bell Syst. Tech. J. 34(5):1045-1079, 1955, doi:10.1002/j.1538-7305.1955.tb03788.x | the Mealy machine | as above |
| Nerode, *Linear automaton transformations*, Proc. AMS 9:541-544, 1958; Myhill 1957 | the right-congruence quotient of a machine by behavioural equivalence | the semantic collapse `65552 -> 21904` is an instance of behavioural quotienting; the construction is Nerode's |
| Rissanen, *Modeling by shortest data description*, Automatica 14(5):465-471, 1978, doi:10.1016/0005-1098(78)90005-5 | minimum description length; that description cost depends on the code | the observation that description-length quantities are encoding-dependent is Rissanen's tradition; `MP-5` only computes which registered quantities move under which registered re-encoding |
| Blumer, Ehrenfeucht, Haussler & Warmuth, *Occam's razor*, Inf. Proc. Letters 24(6):377-380, 1987, doi:10.1016/0020-0190(87)90114-1 | that a compression bias yields learnability guarantees | `MP-3`'s one-bit preferences are not Occam bounds and no sample-complexity claim is made |

## 2. In-repository parents (pinned in `MANIFEST_V1.json`)

| package | what it owns | what is taken, not re-earned |
|---|---|---|
| `research/gmi-833-heldout-20-transitions-v1` | the registered `65552`-candidate universe, the objective `J`, the analytic boundary `lambda* = eta*p/2`, the `5x4` grid, the `146` risk summaries | the universe and the objective are used verbatim; the boundary law is **not** re-derived and its rows are not touched |
| `research/gmi-833-z-z7-impossibility-v1` | the six registered named families and their syntactic predicates; the vacuity classifier pattern | the family member sets are the ground truth `MP-6` must reproduce; the vacuity classifier idea is reused and re-implemented |
| `research/gmi-833-terminology-migration-v1` | the corpus edit removing bare `prior-free` from paper-facing prose (`MIGRATION_LOG_V1.md`, `MIGRATION_LOG_V2.md`) | row 3's *corpus state* is this lane's work; `MP-7` only verifies it |
| `research/gmi-833-tranche-ab-ac-lit` | `GMI_TERMINOLOGY_CROSSWALK_V2.md` rows 9 and 26 — the literature audit and the migration rule "never bare prior-free" | row 3's *literature audit* precondition is discharged by this parent, cited, not repeated |
| `research/gmi-833-blind-recovery-v2-v1`, `gmi-833-aj9b..aj9h` | the family-blind recovery protocol, the no-smuggling contract, the prior-disclosure discipline | `MP-6` follows the protocol shape; the protocol is theirs |
| `research/gmi-833-no-smuggling-audit-v1` | the architecture-name/macro leakage detectors | the lexical spec audit in `MP-6` is a narrow re-implementation for one vocabulary, not a replacement |
| issue #837 | the `P0..P4` architecture-prior ladder definitions | `MP-5` takes the ladder as given and asks only which quantities survive re-encoding |

## 3. The residual contribution of this tranche

1. An exact measurement of the **encoding-induced semantic prior** of the
   registered universe: `K = 21904`, class sizes `1..785`,
   `D_TV = 3535488/5608793`, with a control encoding and a hostile that both
   return `0` from the same estimator.
2. An exact **bias ladder** on a frozen held-out family — `1/2` at zero bits,
   `23315/39711` at the best of `300` one-bit preferences, `5671/11346` at the
   worst, `80663/119133` at a full uniform measure — with a `200`-feature null
   that no feature in it reaches, and the sub-chance half revived by exhaustive
   sweep after the declared lever failed.
3. The **invariance table** over three verified-bijective re-encodings, from
   which the defensible P3/P4 criterion is read rather than asserted, including
   the refutation of the freeze's own `H7c`.
4. An exact **one-vocabulary recovery** of all six registered named families
   with a `3^12` specification-space null returning `0/200`.
5. A **validated site classifier** for the `prior-free` terminology row, with
   its own three-defect failure recorded.

Everything else in this package is parent property.
