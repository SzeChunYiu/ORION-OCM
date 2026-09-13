# PR568 learning/memory correction and replay

Parent:6e879c5f7c0fa59e8bdded6dcb1b67d16a86d5ac.
The original two learning files remain in the separately frozen PR568 audit
packet; this correction does not rewrite that historical record or the
formal-derivation unit at1858f7b9.

| Corrected claim | Decisive countercontrol | Retained positive theorem |
| --- | --- | --- |
| LMT-1 signed regret must converge to zero | Predictable zero-loss switching gives average regret−1/2 | One-sided no regret permits outperforming fixed comparators |
| LMT-3 class cardinality alone | Sample-dependent size2 ERM has zero training risk and population risk≥3/4 | Pre-data fixed measurable class/loss plus proper ERM |
| LMT-5 marginal observation identity | Private action A and observation A xor world identify jointly | Equal complete-view laws under each claimed learner |
| LMT-7 forgotten-state collision alone | A fresh revealing observation restores the lost bit | Equal complete later views prevent two distinct exact answers |

The properness control also shows that empirical near-optimality outside the
registered class need not generalize. Output kernels explicitly allow
abstention and other wrong outputs. The pilot/independent-scoring construction
revives data-selected hypotheses without reusing the unqualified cardinality
argument.

The closest PAC parent is Shalev-Shwartz/Ben-David §2.3 and Corollary4.6,
linked in LEARNING_RISK_AND_REGRET_V1.md. This adaptation restores their
fixed-function and proper-selection premises. Their online treatment uses
a worst-case regret convention; the corrected realized-sequence convention
is explicitly one-sided. The view/forgetting proofs use common probability
kernels, with the repository's existing complete-interface discipline.
No stronger statistical rate, new belief-revision calculus, or capability
advantage is claimed.

## Validation

Run only these focused tests on laptop billy with CPython3.12:

    python3 -I -B -m unittest discover -s research/gmi-recursive-theory-closure-v1 -p 'test_learning_memory*v1.py'
    python3 -O -I -B -m unittest discover -s research/gmi-recursive-theory-closure-v1 -p 'test_learning_memory*v1.py'

The tests retain the original four controls and add exact finite probability,
joint-view, side-information, regret and fixed/sample-dependent-class cases.
Finite enumerations check the stated examples; they do not replace the
analytic iid/convergence proofs. No ecology, search campaign or timing result
is produced. Existing CORE, ledger, GAC and grand registers remain untouched.
