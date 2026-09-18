# Z15 parent-ownership disclosure

## External parents (nothing here is claimed novel against them)

| parent | what it owns | citation |
|---|---|---|
| Falsificationism | the demand that a theory name what would refute it, and the asymmetry between corroboration and proof | Popper, *Logik der Forschung*, Springer 1935; *The Logic of Scientific Discovery*, Hutchinson 1959 |
| Severe testing | the requirement that a test have a high probability of detecting an error if one is present — i.e. that a falsifier must be able to fire | Mayo, *Error and the Growth of Experimental Knowledge*, University of Chicago Press 1996, ISBN 978-0-226-51198-2; Mayo, *Statistical Inference as Severe Testing*, CUP 2018, doi:10.1017/9781107286184 |
| Preregistration and publication of negative results | publishing failed preregistered predictions beside successful ones | Nosek, Ebersole, DeHaven & Mellor, *PNAS* 115(11):2600-2606, 2018, doi:10.1073/pnas.1708274114 |
| Identifiability / resolution limits | the general fact that a finite design localizes a parameter only to within the design's own resolution | classical experimental-design identifiability; `Z15-F1-BLIND` is its exact finite instance here, not a new principle |
| Invariance as a theory constraint | requiring predictions to be invariant under transformations claimed physically irrelevant | Wigner, *Comm. Pure Appl. Math.* 13(1):1-14, 1960, doi:10.1002/cpa.3160130102 |

**Not claimed novel:** falsifiability, severe testing, preregistration,
identifiability, or invariance as concepts.

## On-main parents (their results are what the falsifiers decide)

| package | what it owns | how this package uses it |
|---|---|---|
| `gmi-833-heldout-20-transitions-v1` (#901) | the 20 held-out worlds, the boundary law, the 65,552-candidate universe, the two search procedures, the shifted-boundary control | the registered world set for `F1/F1+`, `F2`, `F4`; route B independently reproduces its recorded controls |
| `gmi-833-capability-predictor-evaluation-v1` (#1022) | the frozen capability prediction sets and external truth sets, and its own `KE-6` coverage result | the scored population for `F3`; three register entries quote its published failures |
| `gmi-833-theory-baseline-v1` | the audited corpus baseline, the OVERSTRONG adjudication, the open revival tickets | two register entries quote it |
| `gmi-833-z-z12-prediction-scoring-v1` (this session) | the Z12 scoring instrument | one register entry quotes its own recorded instrument defect |

## The named residual of this tranche

1. **Four executable falsifiers**, each with a planted positive and a clean
   no-alarm case, stated so that a reader who has not read the corpus can apply
   them — the thing row 1 actually asks for.
2. **`Z15-F1-BLIND`**: the proof, the counterexample `r = 6/7`, and the *measured
   confirmation* that the frozen falsifier's blind set is exactly the analytically
   predicted interval — 57 survivors realizing 12 distinct multipliers, all
   inside `(1/2, 3/2)`, none outside.
3. **`F1PLUS-DEC`**: the revival that turns a conditional falsifier into an
   unconditional one using evidence the frozen design already contained, proved
   and measured at `200/200`.
4. **The invariance pair** (`F4a`/`F4b`): silent on the irrelevant transformation,
   firing on the relevant one, which is what stops an invariance check from being
   a constant `False`.
5. **A machine-checked failed-prediction register** in which a negative control is
   labelled a control rather than counted as a discovered failure.
