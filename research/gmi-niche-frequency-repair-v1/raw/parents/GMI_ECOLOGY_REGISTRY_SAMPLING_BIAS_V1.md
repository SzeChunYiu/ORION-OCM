# The registered ecologies are not a representative sample of the construction space

Date: 2026-09-13. Prompted by the `P4` failure in `GMI_CAPABILITY_MAP_PROSPECTIVE_TEST_V1.md`, where five
freshly drawn ecologies turned out to have systematically stronger constant baselines than the six the
corpus tests on. Closed-form computation only — best constants, no lifecycle runs, no search.

## Method

3 000 coefficient 4-tuples drawn uniformly from the grid `{i/16 : i ∈ [−8, 8]}` (`random.Random(4242)`),
each turned into an ecology by the registry's own `spec_smooth`, and its best constant computed over the
unseen criterion exactly as `eco_axis.best_constant` does for registered ecologies.

## Result

| uniform sample (n = 3 000) | value |
|---|---:|
| mean | 0.8363 |
| median | 0.8333 |
| p10 / p25 / p75 / p90 | 0.7812 / 0.8125 / 0.8646 / 0.8958 |

| registered ecology | best constant | percentile of the uniform space |
|---|---:|---:|
| `E_wit1` | 0.7083 | **0.2 %** |
| `E_sym5` | 0.7917 | 12.2 % |
| `E_smooth3` | 0.8125 | 22.9 % |
| `E_smooth1` | 0.8333 | 36.4 % |
| `E_parity` | 0.8333 | 36.4 % |
| `E_sym3` | 0.8750 | 78.2 % |

**Five of the six sit below the median, and the registered mean is 0.8090 against the space's 0.8363.**
The registry over-samples ecologies whose constant baseline is weak — which is precisely where a
non-constant family has room to clear the rule-40 margin.

## The sharpest consequence

**`E_wit1` is at the 0.2nd percentile.** It is weaker than 99.8 % of the construction space, and it is:

* the **only** registered ecology where any `gradient_net` is admissible
  (`GMI_LEARNER_ADMISSIBILITY_MAP_V1.md`);
* the **only** task where `RV-377-210` returned `FAMILY_COEXISTENCE` rather than a single family;
* the witness-bearing case that the class-rate law's `C` clause singles out
  ("coefficient class ≤ 1/3 on witness-free ecologies; no bound where witness-bearing").

Three independent results in this corpus turn on one ecology that is a 1-in-500 outlier for baseline
weakness. Stated at full strength: **in this construction, the learner family's niche requires an ecology
weaker than roughly 99.8 % of the space.** That is a quantitative statement about where learners can live,
and it is far more restrictive than "admissible on 1 of 6".

## What this does and does not do to the corpus

**It scopes rather than invalidates.** Every measured number stands; what changes is the population those
numbers describe. Family-admissibility counts of the form "n of 6 registered ecologies" are counts over a
sample skewed toward the easy end, so they **overstate** how often a non-constant family finds room. The
prospective test is the check: on five representative draws, exact search still held everywhere while
memory — admissible on 3 of the 6 registered — cleared the margin **nowhere**.

**It does not impugn the registry's construction.** A registry assembled to exhibit interesting behaviour
will naturally concentrate where behaviour is interesting; that is what it is for. The defect is only in
reading counts over it as frequencies over the space, which is what I did earlier today when I calibrated
`P4`.

**It does not touch reachability.** `DU-1` stands regardless; this is entirely a statement about the
static admissibility side.

## Registered consequence for future family claims

Any claim of the form "family F is admissible on k of n ecologies" should carry the **percentile of those
n ecologies' constants within the construction space**, or be stated over a uniform draw. Without it the
count is a property of the registry rather than of the family — and on the one comparison available so
far, the two differ enough to reverse a family's apparent standing.
