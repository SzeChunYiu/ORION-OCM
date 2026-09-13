# PR #551: source-correct consumer census and its limits

Reviewed head: `7c5162933d6ab4bcfb0d7bab87f4aefa7b19ed4b`.
The scanner and raw records are unchanged from `cf1c0f8e11f2f548f8a5010826b88f1823c2b7de`;
the newer commit appends 49 lines interpreting SEARCH costs. Both exact claim
versions are retained in the bound archive. This correction changes current
interpretation and supplies a versioned scanner; no upstream freeze is mutated.

## 1. The numeric-consumer classifier omits a real native primitive

The [scanner](https://github.com/SzeChunYiu/ORION-OCM/blob/cf1c0f8e11f2f548f8a5010826b88f1823c2b7de/research/machine-intelligence-morphogenesis-v1/gmi_microscope/b6_dense_consumer_scan.py#L12)
uses DOT/LINEAR. The [actual alphabet](https://github.com/SzeChunYiu/ORION-OCM/blob/cf1c0f8e11f2f548f8a5010826b88f1823c2b7de/research/machine-intelligence-morphogenesis-v1/gmi_microscope/morph.py#L47)
has LINEAR for the scalar dot operation and AFFINE for the vector map; DOT
is absent. This is an executable false negative on the retained data.

| Rows in the original 17-row cohort | Connection | Rows |
|---|---|---|
| CROSS/TWIN/S0 and duplicate DISJ/TWIN/S0, archive-best and first-pruned | DENSE→AFFINE parameter port 0 | 4 |
| SAME/CONTINUED/S0 first-pruned and SAME/RESET/S0 archive-best | DENSE→LINEAR parameter port 0 | 2 |

Thus six rows have declared numeric-parameter adjacency. Only three rows have
that numeric node on syntactic OUTPUT ancestry. Neither observation proves
causal coefficient use. LINEAR/AFFINE read parameter names at port 0 and data
at port 1; runtime guards, available coefficient blocks and downstream behavior
still matter. EDGE routing can also hide an indirect connection from the old
immediate-neighbor test. The versioned scanner reports these distinctions.

The archived original probe reproduces its 2/17 count, and a real AFFINE graph
makes it return false while the corrected native-port analysis returns the
recorded adjacency. This correction does not infer that all six rows are
admissible coefficient learners, or that off-ancestry nodes are irrelevant to
feedback, storage or resource cost.

## 2. Retained survivors do not identify the full search or its causal stages

The [reported zero](https://github.com/SzeChunYiu/ORION-OCM/blob/7c5162933d6ab4bcfb0d7bab87f4aefa7b19ed4b/research/machine-intelligence-morphogenesis-v1/GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md#L666)
is reproducible: no GRAD in 70 exported arm rows, of which 43 contain DENSE.
Those are 63 distinct serialized graphs. The 17-row scanner cohort has 15.
They include known repeated CROSS/TWIN and DISJ/TWIN records.

The exporter [retains the best genotype per carrier](https://github.com/SzeChunYiu/ORION-OCM/blob/cf1c0f8e11f2f548f8a5010826b88f1823c2b7de/research/machine-intelligence-morphogenesis-v1/gmi_microscope/b6_development.py#L258),
not every archive cell. The ten arms report 800 final cells but retain only
50 best-per-carrier graphs, plus 20 first-hit raw/pruned graphs. The census
cannot conclude that no other final survivor or searched machine contains GRAD.

There is positive counterevidence to campaign-wide absence: five already-bound
source archives retain **eight GRAD-bearing cells among 350**. Three DENSE
cells and one NONE cell occur in E_smooth1/S1, two DENSE cells in E_smooth3/S0,
and two in E_twin0/S0. Several match recorded arm seed fingerprints. These
source standard capabilities do not establish target adequacy or active gradients.
The complete receipt retains their exact source paths, cells and fingerprints.

The [add-node operator](https://github.com/SzeChunYiu/ORION-OCM/blob/cf1c0f8e11f2f548f8a5010826b88f1823c2b7de/research/machine-intelligence-morphogenesis-v1/gmi_microscope/morphgen.py#L68)
can draw GRAD among 33 kinds, conditional on choosing that operator. Mutation
then retries invalid graphs, while placement caches, evaluates and selects.
Eligibility and retained outcomes do not separate proposal frequency, typing,
evaluation failure and selection. Per-stage, per-kind telemetry is still needed;
the final paragraph's admission of missing telemetry is the correct boundary.

The 7c516293 cost appendix has the same causal limitation. Native
[SEARCH](https://github.com/SzeChunYiu/ORION-OCM/blob/7c5162933d6ab4bcfb0d7bab87f4aefa7b19ed4b/research/machine-intelligence-morphogenesis-v1/gmi_microscope/vm.py#L310)
is a guarded update over a grammar prefix and stored evidence; update nodes
are skipped without feedback. A 2401/16 parameter ratio is not a measured
150-fold workload on every event, nor a universal error bound for compute.
Four retained SEARCH graphs cannot identify selection's causal preference or
the cause of the particular unfinished source. The report of a stall remains
a report; no new bound raw stall trace is added by that 49-line change.
The possibility of an evaluation-count/work mismatch is useful, but its
attribution requires the corresponding operation and event records.

## 3. The all-event S1 positive already belongs to the retained proof

The new witness's raw and pruned strings and all six reported capabilities
are identical to the earlier SAME/CONTINUED/S1 witness. It is not independent
material. The [prior consumer proof](https://github.com/SzeChunYiu/ORION-OCM/blob/bbbc9dec44cc5a25bb2e1995aa2647bde4701e98/research/gmi-witness-mechanism-v1/CONSUMER_SEMANTICS_V1.md#L10)
already covers every finite query/feedback/revoke sequence in the declared VM.
The new [stronger-than-measurement claim](https://github.com/SzeChunYiu/ORION-OCM/blob/7c5162933d6ab4bcfb0d7bab87f4aefa7b19ed4b/research/machine-intelligence-morphogenesis-v1/GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md#L618)
therefore misstates both the object identity and the strongest matched parent.

The positive result survives: the zero-vector replacement preserves query
values, abstention and ordered common stores under the proof's assumptions.
It depends on DENSE string references producing the same INSERT zero key,
EVIDENCE ignoring its input values, and unchanged update order. Mere absence
of particular consumer names would not establish that projection. Memory
updates still constitute learning without GRAD. Representation and lifetime
resource equivalence remain outside the result.

The earlier PROGRAM/DENSE field correction, incomplete-campaign scoring and
missing E_twin1/S1 source remain qualified in the
[previous review](../gmi-grand-unification-v1/PR551_SCIENTIFIC_REVIEW_F359A957_V1.md).
No current-bar empirical result, complete ancestry or new search is claimed.

[Full reproducible census](CONSUMER_CENSUS_RECEIPT_V1.json) ·
[Exact archive bindings](FROZEN_INPUTS_V1.json) · [Operations](OPERATIONS_V1.md).
