"""Support-family discovery: the whole set of minimal ways to break a belief.

This module is experiment ``E6`` of the cognitive-ladder programme.  It exists
because of one sentence in ``ROOT_CAUSE_ANALYSIS_V1.md``:

    the probe granularity was fixed at one element by design, so the instrument
    could not express the structure it was looking for

That root, ``PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED``, is the parent of
claim ``C11-ABLATION-ATTRIBUTION-INCOMPLETE``.  E3 measured the damage: between
16.3% and 25% of methods had support that no single-element ablation could see,
because where evidence ``A`` alone suffices and ``B`` alone suffices, removing
either changes nothing while removing both breaks the method.  E3 called that a
limitation and stopped.  This experiment changes the instrument.

What is discovered here
-----------------------

Not one dependency set.  The **support family**: the set of MINIMAL SUPPORT
SETS.  For a method ``m``:

    a *support set* is a subset ``S`` of ``m``'s candidate evidence whose
    removal breaks ``m``; it is *minimal* when no proper subset of ``S`` breaks
    ``m``.  The *support family* of ``m`` is the set of all minimal support
    sets.

One object expresses every structure E3 could not:

===========================  ==================================================
single support               one minimal set of size 1
alternative support          several derivations, one minimal set of size >= 2
                             (the C11 shape: neither element alone matters)
two-of-three                 three minimal sets of size 2
redundant support            a singleton AND a pair in the same family, so
                             leave-one-out gets half the answer and stops
conditional support          an element that is load-bearing only once another
                             is gone
higher-order interaction     a minimal set of size 3 with no smaller subset
no load-bearing evidence     the empty family
===========================  ==================================================

The world
---------

A **justification network**, which is the oldest available way to write these
structures down and is deliberately not novel.  Three node kinds:

``evidence``   an assumption.  IN exactly when it is live.  This is what a
               revocation is applied to, so it is an addressable object.
``derived``    IN when some justification's antecedents are all IN.
``method``     a derived (or axiomatic) node the store serves as a competence.

Derivability is the LEAST fixpoint, which is what makes the cyclic archetype
honest: a node supported only by a cycle through itself is not IN, so an arm
cannot manufacture support out of a loop.

Ground truth
------------

**Exhaustive enumeration over the evidence powerset**, in the scorer only.
``support_family`` tests every one of the ``2**B - 1`` non-empty subsets of a
method's candidate evidence, keeps those that break it, and reduces to the
minimal ones under inclusion.  ``B`` is frozen at
``SUPPORT_PLAN["evidence_per_method"]``; the powerset bound is therefore
``2**B - 1`` non-empty subsets per method, stated in the plan and asserted in
the tests, and the oracle is exactly computable rather than approximated.  No
arm may call it and ``test_support.py`` enforces that by source inspection, in
the same way ``test_depend.py`` enforces the leave-one-out separation.

The oracle is not hidden information; it is EXPENSIVE information.  Every arm
can reach it by spending ``2**B - 1`` interventions, and
``exhaustive_powerset_parent`` does exactly that.  This is the same structure
E3 declared: an arm that runs the oracle's own procedure scores perfectly
against the oracle and that is arithmetic, not evidence.  The coordinate that
separates arms is **interventions spent to reach a given support-family
precision and recall**.

Discipline
----------

* Every ablation is a charged **intervention** against a declared budget.  An
  arm that wants to know whether removing three blocks breaks a method has to
  spend an intervention finding out, and the meter refuses when the budget is
  gone.
* Two arms are declared BUDGET EXEMPT, with the exemption printed in the
  receipt: ``exhaustive_powerset_parent``, because a truncated exhaustive
  enumeration is a different arm and not a ceiling, and the on-demand
  disclosure path of ``lazy_parent``, because that path is a receipt for a
  qualifier and not a discovery strategy.
* Stale survivors and collateral invalidations are counted separately and are
  NEVER summed, exactly as in ``depend.py``.
* No wall-clock anywhere.  Stdlib only.  Frozen dataclasses for records,
  mutable ledgers for accumulation.

Limitations, stated before any number
-------------------------------------

* The evidence CANDIDATE set per method is still declared, exactly as in E3.
  Which of a method's blocks matter is discovered; that they are its blocks is
  given.  A harness in which the candidate set had to be discovered too is a
  different and larger experiment.
* ``B = 6`` so that the powerset oracle is exactly computable.  Every claim
  about interventions is a claim about a six-element candidate set, and the
  interesting asymptotics of minimal-hitting-set enumeration are outside this
  world by construction.
* The archetypes are AUTHORED.  Their support families are the ones the
  experiment wanted to see, which is the point of a microscope and is also the
  reason no rate quoted here transfers anywhere.  E3's rate came from an
  induction world that produced the shapes on its own; this one does not
  pretend to.
* Nothing here is new machinery.  Computing minimal supporting environments is
  what an ATMS has done since de Kleer (1986); shrinking a breaking set to a
  minimal one is QuickXplain (Junker 2004); enumerating the whole family and
  hitting-setting the dual is Reiter (1987) and the MARCO/CAMUS line
  (Liffiton & Sakallah; Liffiton, Previti, Malik & Marques-Silva).  No novelty
  is claimed for any of it.  A sibling lane of this same programme
  (``research/epistemic-structure-discovery-20260908``) has independently
  implemented an antichain minimal-support learner and already reported the
  shape this experiment's decisive coordinate is testing: *active model
  enumeration lowers queries but costs more*.  The contribution here is the
  PARENT COMPARISON and the FAMILY TAXONOMY, not the learner.
* Consequently INTERVENTIONS and TOTAL COUNTED OPERATIONS are reported side by
  side and never summed.  "Cheaper on the coordinate we optimised, not cheaper
  in total" is the outcome to be argued against rather than assumed away; it is
  what the sibling lane found, and it is what ``results/REINDEX_E9_V1.json``
  found in a different place.

Parents: assumption-based truth maintenance (de Kleer); model-based diagnosis
and minimal hitting sets (Reiter, Greiner et al.); minimal unsatisfiable subset
extraction and enumeration (Junker; Liffiton & Sakallah; MARCO); delta
debugging (Zeller & Hildebrandt); program slicing; database view maintenance.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Iterator, Mapping, Sequence

from prereg import Commitment, canonical_json, commit
from scaling import (
    INDEX_ENTRY_BYTES,
    SPARSE_FRACTION,
    CheckStatus,
    ResourceRecord,
    RevisionRecord,
    TouchLedger,
    fit_loglog,
    record_from_ledger,
)

__all__ = [
    "SUPPORT_PLAN",
    "COMMITMENT",
    "Justification",
    "Archetype",
    "ARCHETYPES",
    "SupportInstance",
    "SupportCatalogue",
    "SupportObject",
    "SupportStore",
    "SupportWorld",
    "BudgetExhausted",
    "InterventionMeter",
    "RevocationStep",
    "SupportFamilyRecord",
    "build_catalogue",
    "populate_store",
    "build_world",
    "archetype_order",
    "powerset_bound",
    "subsets_of",
    "minimal_sets",
    "hitting_sets",
    "support_family",
    "oracle_families",
    "oracle_minimal_environments",
    "oracle_changed_methods",
    "oracle_holds",
    "classify_family",
    "family_shapes",
    "leave_one_out_blind_methods",
    "revocation_schedule",
    "declared_candidate_family",
    "score_family",
    "EVIDENCE_PER_METHOD",
    "INTERVENTION_BUDGET",
    "fit_loglog",
    "CheckStatus",
    "ResourceRecord",
    "RevisionRecord",
    "TouchLedger",
    "record_from_ledger",
    "INDEX_ENTRY_BYTES",
    "SPARSE_FRACTION",
]


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Editing any value changes the commitment and
#: therefore changes the archetype order and every per-instance evidence
#: permutation, which is what makes analysis drift mechanically visible
#: (CL-D4).  A third party re-derives the whole catalogue from this hash.
SUPPORT_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "rung": "CL-D-E6 support-family discovery under charged group ablation",
    "answers_root_cause": "PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED",
    "answers_claim": "C11-ABLATION-ATTRIBUTION-INCOMPLETE",
    "evidence_per_method": 6,
    "multipliers": [1, 2, 5, 10],
    "intervention_budget_per_method": 24,
    "budget_rule": (
        "four times the candidate set size, declared before the run. Every arm gets the "
        "same budget for the DISCOVERY phase. Re-derivation performed at revocation or "
        "query time is charged as work and counted as its own intervention column; it is "
        "not drawn against the discovery budget, because an arm that discovers nothing is "
        "not thereby forbidden from serving a revocation."
    ),
    "budget_curve_points": [4, 8, 12, 24, 48, 63],
    "budget_curve_disclosure": (
        "THE REGISTERED BUDGET IS 24 AND ITS ROW IS REPORTED UNCHANGED. The curve over "
        "the other points was added after a pilot run at the registered budget showed the "
        "budget to be BINDING for the adaptive arm on two of eleven archetypes. It is "
        "added because the declared residual coordinate is 'interventions spent to reach "
        "a given support-family precision and recall', and a single budget reports one "
        "point on that curve rather than the curve. The registered budget was NOT changed "
        "in response to the pilot, and this note exists so that the addition is visible "
        "rather than silent."
    ),
    "budget_exempt": {
        "exhaustive_powerset_parent": (
            "a truncated exhaustive enumeration is a different arm, not a correctness "
            "ceiling. The exemption is declared here and its interventions are reported "
            "in full so that the exponential cost is visible rather than excused."
        ),
        "lazy_parent.disclosure": (
            "lazy_parent holds no support family. Asking it for one costs it the whole "
            "enumeration it skipped, and that cost is the receipt for the phrase 'cheap "
            "to build'. It is reported separately and never folded into total work, "
            "because serving a revocation does not require publishing a family."
        ),
    },
    "ground_truth": (
        "exhaustive enumeration over the evidence powerset. A subset S of method m's "
        "candidate evidence is a SUPPORT SET iff m holds with all evidence live and does "
        "not hold with S withdrawn; it is MINIMAL iff no proper subset of S is a support "
        "set. The support family of m is the set of its minimal support sets. Computed by "
        "brute force in the scorer, never handed to any arm."
    ),
    "second_ground_truth": (
        "minimal supporting environments, the ATMS label. The minimal support sets are "
        "exactly the minimal transversals of the minimal environments; both objects are "
        "computed by the scorer and the duality is asserted in the tests rather than "
        "assumed, because an arm that enumerates one and converts to the other must be "
        "scored against a truth that does not depend on which side it started from."
    ),
    "arms": [
        "adaptive_arm",
        "leave_one_out_parent",
        "lazy_parent",
        "atms_gifted_parent",
        "atms_discovering_parent",
        "exhaustive_powerset_parent",
        "random_group_ablation_parent",
    ],
    "required_families": [
        "SINGLE_SUPPORT",
        "ALTERNATIVE_SUPPORTS",
        "TWO_OF_THREE",
        "REDUNDANT_SUPPORTS",
        "CONDITIONAL_SUPPORT",
        "HIGHER_ORDER_INTERACTION",
        "DEEP_CHAIN",
        "CYCLIC",
        "SHARED_GLOBAL",
        "REPRESENTATION_DEPENDENT",
        "NO_LOAD_BEARING",
    ],
    "endpoints": [
        "support-family precision and recall against the powerset oracle, per arm and "
        "per archetype",
        "interventions spent, split into discovery / disclosure / revocation / query",
        "stale survivors (true dependents left live) counted exactly, never summed with",
        "collateral invalidations (non-dependents torn down) counted exactly",
        "discovery work, revocation work, query work, update (index maintenance) work",
        "persistent bytes",
        "total work against lazy_parent INCLUDING discovery",
    ],
    "residual_coordinate": (
        "interventions spent to reach a given support-family precision and recall. The "
        "only place a residual could live is whether adaptive_arm beats "
        "random_group_ablation_parent and approaches exhaustive_powerset_parent at "
        "materially lower cost than atms_discovering_parent needs when it is NOT handed "
        "the justifications."
    ),
    "two_column_rule": (
        "INTERVENTIONS AND TOTAL COUNTED OPERATIONS ARE REPORTED SIDE BY SIDE, PER ARM, "
        "AND ARE NEVER SUMMED OR TRADED OFF INTO ONE FIGURE. An arm that spends fewer "
        "interventions while spending more total work has not been shown to be cheaper; "
        "it has been shown to be cheaper on the coordinate it optimises. Reporting only "
        "the interventions column would reproduce the flattering half of that picture."
    ),
    "replication_target": {
        "source": (
            "branch research/epistemic-structure-discovery-20260908, antichain "
            "(minimal-support) learner: 256/256 recovered, 164 source queries, 146401 "
            "counted operations; 'active model enumeration lowers queries but costs "
            "more'"
        ),
        "second_source": (
            "results/REINDEX_E9_V1.json, incremental re-index: a large saving on the "
            "optimised coordinate that did not change which arm was cheaper overall"
        ),
        "hypothesis_under_test": (
            "adaptive group selection lowers INTERVENTIONS while raising TOTAL COUNTED "
            "OPERATIONS relative to the undirected parents. If adaptive_arm shows that "
            "shape here, this experiment is an independent replication of an existing "
            "result in this programme and reports it as the headline, not as a caveat."
        ),
        "novelty": (
            "NONE IS CLAIMED FOR THE LEARNER. Minimal-support / antichain learning is "
            "parent-owned (de Kleer 1986; Reiter 1987; Junker 2004; Liffiton & Sakallah; "
            "MARCO) and has now also been independently implemented elsewhere in this "
            "programme. What this experiment contributes is the PARENT COMPARISON and "
            "the FAMILY TAXONOMY, not the learner."
        ),
    },
    "sparse_fraction": SPARSE_FRACTION,
    "index_entry_bytes": INDEX_ENTRY_BYTES,
    "loglog_residual_threshold": 0.05,
    "fit_basis": "log10, ordinary least squares, 4 points, 2 free parameters",
}

COMMITMENT: Commitment = commit(SUPPORT_PLAN)

#: Candidate evidence blocks per method.  The powerset oracle enumerates
#: ``2 ** EVIDENCE_PER_METHOD - 1`` non-empty subsets per method; at six that is
#: 63, which is exactly computable and is the bound this experiment states.
EVIDENCE_PER_METHOD: int = SUPPORT_PLAN["evidence_per_method"]

#: Interventions each arm may spend per method during discovery.
INTERVENTION_BUDGET: int = SUPPORT_PLAN["intervention_budget_per_method"]


def powerset_bound() -> int:
    """The exact size of the oracle's search, stated rather than implied."""
    return 2**EVIDENCE_PER_METHOD - 1


# --------------------------------------------------------------------------
# the archetypes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Justification:
    """``consequent <- antecedents``.  The unit of the world's structure."""

    consequent: str
    antecedents: tuple[str, ...]


def _j(consequent: str, *antecedents: str) -> Justification:
    return Justification(consequent=consequent, antecedents=tuple(antecedents))


@dataclass(frozen=True)
class Archetype:
    """One authored support structure, with its expected shape declared.

    ``expected_shape`` is written before the run and is asserted against the
    powerset oracle by ``test_support.py``.  It is prose next to a mechanical
    check, not a substitute for one.

    ``revocation`` is the registered schedule for this archetype, in local
    evidence names, applied cumulatively.  Its steps are ordered so that the
    no-op steps come first and the breaking step last, for the same reason
    ``depend.py`` orders its schedule that way: a step's lesson must not be
    contaminated by an earlier step having already invalidated the method.
    """

    archetype_id: str
    structure: str
    evidence: tuple[str, ...]
    methods: tuple[str, ...]
    derived: tuple[str, ...]
    axioms: tuple[str, ...]
    justifications: tuple[Justification, ...]
    expected_shape: str
    revocation: tuple[tuple[str, ...], ...]
    note: str = ""

    @property
    def padding(self) -> int:
        return EVIDENCE_PER_METHOD - len(self.evidence)

    def __post_init__(self) -> None:
        if len(self.evidence) > EVIDENCE_PER_METHOD:
            raise ValueError(
                f"{self.archetype_id} names more structural evidence than the frozen "
                f"candidate width {EVIDENCE_PER_METHOD}; the powerset oracle would stop "
                "being exactly computable"
            )
        if len(set(self.evidence)) != len(self.evidence):
            raise ValueError(f"{self.archetype_id} repeats an evidence name")


#: The eleven registered archetypes.  Every structure the support family was
#: introduced to express appears here, including the two that E3's instrument
#: could not represent at all and the one where NO evidence is load-bearing.
ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        archetype_id="SINGLE_SUPPORT",
        structure="m <- a",
        evidence=("a",),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a"),),
        expected_shape="exactly one minimal support set, {a}, of size 1",
        revocation=(("p0",), ("a",)),
        note=(
            "the case leave-one-out was built for. It is here so that a group-ablation "
            "arm has to pay for the easy case too, rather than only being measured where "
            "the parent fails."
        ),
    ),
    Archetype(
        archetype_id="ALTERNATIVE_SUPPORTS",
        structure="m <- a ; m <- b",
        evidence=("a", "b"),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a"), _j("m", "b")),
        expected_shape="exactly one minimal support set, {a, b}, of size 2",
        revocation=(("a",), ("b",)),
        note=(
            "THE C11 SHAPE. Two evidence blocks each suffice alone, so removing either "
            "changes nothing and single-element ablation reports that the method rests on "
            "nothing at all. Removing both breaks it. The registered two-step revocation "
            "walks straight into it."
        ),
    ),
    Archetype(
        archetype_id="TWO_OF_THREE",
        structure="m <- a,b ; m <- a,c ; m <- b,c",
        evidence=("a", "b", "c"),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a", "b"), _j("m", "a", "c"), _j("m", "b", "c")),
        expected_shape="three minimal support sets, {a,b}, {a,c} and {b,c}, each of size 2",
        revocation=(("a",), ("b",)),
        note=(
            "a threshold structure. No single block is load-bearing and no single block "
            "is dispensable either; the family has three overlapping pairs, which is a "
            "shape a single dependency SET cannot represent however it is computed."
        ),
    ),
    Archetype(
        archetype_id="REDUNDANT_SUPPORTS",
        structure="m <- a,c ; m <- b,c",
        evidence=("a", "b", "c"),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a", "c"), _j("m", "b", "c")),
        expected_shape="two minimal support sets, {c} of size 1 and {a,b} of size 2",
        revocation=(("a",), ("b",)),
        note=(
            "the sharpest test of the E3 instrument, because leave-one-out gets HALF the "
            "answer here: it finds {c} and reports a complete result. An arm that stops "
            "when it has found a dependency is wrong in a way that looks like success."
        ),
    ),
    Archetype(
        archetype_id="CONDITIONAL_SUPPORT",
        structure="m <- a ; m <- b,c",
        evidence=("a", "b", "c"),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a"), _j("m", "b", "c")),
        expected_shape="two minimal support sets, {a,b} and {a,c}, both of size 2",
        revocation=(("a",), ("b",)),
        note=(
            "b and c are load-bearing only once a is gone. Conditionality is a property "
            "of the family and has no representation in a flat dependency set."
        ),
    ),
    Archetype(
        archetype_id="HIGHER_ORDER_INTERACTION",
        structure="m <- a ; m <- b ; m <- c",
        evidence=("a", "b", "c"),
        methods=("m",),
        derived=(),
        axioms=(),
        justifications=(_j("m", "a"), _j("m", "b"), _j("m", "c")),
        expected_shape="exactly one minimal support set, {a,b,c}, of size 3",
        revocation=(("a",), ("b",), ("c",)),
        note=(
            "a minimal set of size three with no smaller subset. Pairwise ablation is as "
            "blind to it as single-element ablation is to the C11 pair; the registered "
            "schedule needs three steps before anything happens."
        ),
    ),
    Archetype(
        archetype_id="DEEP_CHAIN",
        structure="d1 <- a,b ; d2 <- d1,d ; d3 <- d2 ; m <- d3",
        evidence=("a", "b", "d"),
        methods=("m",),
        derived=("d1", "d2", "d3"),
        axioms=(),
        justifications=(
            _j("d1", "a", "b"),
            _j("d2", "d1", "d"),
            _j("d3", "d2"),
            _j("m", "d3"),
        ),
        expected_shape="three minimal support sets, {a}, {b} and {d}, each of size 1",
        revocation=(("p0",), ("a",)),
        note=(
            "support reached through four derivation steps. Every block is individually "
            "load-bearing, so leave-one-out is exactly right here; the archetype exists "
            "to check that depth alone does not create blindness and to charge the "
            "group-ablation arms for a case where the cheap parent is correct."
        ),
    ),
    Archetype(
        archetype_id="CYCLIC",
        structure="p <- q,a ; q <- p,b ; p <- c ; q <- d ; m <- p,q",
        evidence=("a", "b", "c", "d"),
        methods=("m",),
        derived=("p", "q"),
        axioms=(),
        justifications=(
            _j("p", "q", "a"),
            _j("q", "p", "b"),
            _j("p", "c"),
            _j("q", "d"),
            _j("m", "p", "q"),
        ),
        expected_shape="three minimal support sets, {c,d}, {a,c} and {b,d}, each of size 2",
        revocation=(("c",), ("d",)),
        note=(
            "p and q support each other. Under the LEAST fixpoint the loop grounds out "
            "only through c or d, so support that exists solely inside the cycle is not "
            "support. An arm that propagated labels without a fixpoint would invent "
            "support here, and the powerset oracle would catch it."
        ),
    ),
    Archetype(
        archetype_id="SHARED_GLOBAL",
        structure="m1 <- g,a ; m2 <- g,b",
        evidence=("g", "a", "b"),
        methods=("m1", "m2"),
        derived=(),
        axioms=(),
        justifications=(_j("m1", "g", "a"), _j("m2", "g", "b")),
        expected_shape=(
            "m1 has minimal support sets {g} and {a}; m2 has {g} and {b}. g is a global "
            "support shared by both methods"
        ),
        revocation=(("a",), ("g",)),
        note=(
            "locality is not guaranteed by construction: one block is load-bearing for "
            "every method in the instance. Its revocation is the registered globally "
            "shared step and an arm that assumes a small neighbourhood fails it."
        ),
    ),
    Archetype(
        archetype_id="REPRESENTATION_DEPENDENT",
        structure="r1 <- a,b ; r2 <- c ; m <- r1 ; m <- r2",
        evidence=("a", "b", "c"),
        methods=("m",),
        derived=("r1", "r2"),
        axioms=(),
        justifications=(_j("r1", "a", "b"), _j("r2", "c"), _j("m", "r1"), _j("m", "r2")),
        expected_shape="two minimal support sets, {a,c} and {b,c}, both of size 2",
        revocation=(("c",), ("a",)),
        note=(
            "the same conclusion holds through two different representations. Committing "
            "to r1 says the support is {a} and {b}; committing to r2 says it is {c}. "
            "NEITHER is the support family of m, which is why 'what does this rest on' is "
            "not answerable from a single representation and why an arm that keeps only "
            "the derivation it happened to use reports a confident wrong answer."
        ),
    ),
    Archetype(
        archetype_id="NO_LOAD_BEARING",
        structure="m is an axiom; six evidence blocks are candidates and none matter",
        evidence=(),
        methods=("m",),
        derived=(),
        axioms=("m",),
        justifications=(),
        expected_shape="the EMPTY support family: no subset of the evidence breaks m",
        revocation=(("p0",), ("p1",)),
        note=(
            "the false-positive control. Nothing an arm does to the evidence can change "
            "this method, so every believed support set here is spurious and every "
            "invalidation is collateral. An arm tuned to find structure finds it here."
        ),
    ),
)

_ARCHETYPE_BY_ID: dict[str, Archetype] = {a.archetype_id: a for a in ARCHETYPES}


# --------------------------------------------------------------------------
# the commitment-derived catalogue
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def archetype_order() -> tuple[str, ...]:
    """The frozen archetype order: a deterministic shuffle of the plan hash.

    Used for the round-robin instance order below, so that a catalogue at any
    multiplier holds exactly ``multiplier`` replicates of every archetype and
    is a prefix of every larger catalogue.  Nested scales matter: if each scale
    drew its own archetypes, a change in any endpoint between scales could be a
    change of world rather than a change of ``N``.
    """
    ids = [a.archetype_id for a in ARCHETYPES]
    rng = random.Random(COMMITMENT.stream("support-archetype-order-v1") % (2**63))
    rng.shuffle(ids)
    return tuple(ids)


@dataclass(frozen=True)
class SupportInstance:
    """One archetype laid down with concrete object identities.

    The per-instance permutation is a deterministic function of the plan hash.
    It matters: without it, "slot 0 is load-bearing" would be true of every
    instance of an archetype and an arm could score by probing slot 0 first.
    With it, an arm that wants to know which slot carries which role has to
    intervene.
    """

    instance_id: str
    archetype_id: str
    replicate: int
    evidence_ids: tuple[str, ...]
    method_ids: tuple[str, ...]
    derived_ids: tuple[str, ...]
    axiom_ids: tuple[str, ...]
    justifications: tuple[Justification, ...]
    revocation_steps: tuple[tuple[str, ...], ...]

    @property
    def all_node_ids(self) -> tuple[str, ...]:
        return self.evidence_ids + self.derived_ids + self.method_ids

    @property
    def n_objects(self) -> int:
        return len(self.evidence_ids) + len(self.derived_ids) + len(self.method_ids)


def _instantiate(archetype: Archetype, replicate: int) -> SupportInstance:
    instance_id = f"{archetype.archetype_id}#{replicate}"
    locals_ = list(archetype.evidence) + [f"p{i}" for i in range(archetype.padding)]
    rng = random.Random(
        COMMITMENT.stream(f"support-instance-permutation-v1::{instance_id}") % (2**63)
    )
    slots = list(range(EVIDENCE_PER_METHOD))
    rng.shuffle(slots)
    evidence_id_of = {
        name: f"S:{instance_id}:e{slots[i]}" for i, name in enumerate(locals_)
    }
    evidence_ids = tuple(
        evidence_id_of[name] for name in sorted(locals_, key=lambda n: slots[locals_.index(n)])
    )
    method_id_of = {name: f"M:{instance_id}:{name}" for name in archetype.methods}
    derived_id_of = {name: f"D:{instance_id}:{name}" for name in archetype.derived}
    node_id_of: dict[str, str] = {**evidence_id_of, **derived_id_of, **method_id_of}
    return SupportInstance(
        instance_id=instance_id,
        archetype_id=archetype.archetype_id,
        replicate=replicate,
        evidence_ids=evidence_ids,
        method_ids=tuple(method_id_of[m] for m in archetype.methods),
        derived_ids=tuple(derived_id_of[d] for d in archetype.derived),
        axiom_ids=tuple(node_id_of[a] for a in archetype.axioms),
        justifications=tuple(
            Justification(
                consequent=node_id_of[j.consequent],
                antecedents=tuple(node_id_of[a] for a in j.antecedents),
            )
            for j in archetype.justifications
        ),
        revocation_steps=tuple(
            tuple(evidence_id_of[name] for name in step)
            for step in archetype.revocation
        ),
    )


@dataclass(frozen=True)
class SupportCatalogue:
    """The frozen contents of the persistent state at one scale."""

    scale_id: str
    multiplier: int
    instances: tuple[SupportInstance, ...]

    @property
    def n_objects(self) -> int:
        return sum(i.n_objects for i in self.instances)

    @property
    def method_ids(self) -> tuple[str, ...]:
        return tuple(m for i in self.instances for m in i.method_ids)

    @property
    def n_methods(self) -> int:
        return len(self.method_ids)

    @property
    def n_evidence(self) -> int:
        return sum(len(i.evidence_ids) for i in self.instances)

    def instance_of_method(self, method_id: str) -> SupportInstance:
        for instance in self.instances:
            if method_id in instance.method_ids:
                return instance
        raise KeyError(method_id)

    def instance_of_evidence(self, evidence_id: str) -> SupportInstance:
        for instance in self.instances:
            if evidence_id in instance.evidence_ids:
                return instance
        raise KeyError(evidence_id)

    def first_replicates(self) -> tuple[SupportInstance, ...]:
        return tuple(i for i in self.instances if i.replicate == 0)


@lru_cache(maxsize=None)
def _instance_sequence(count: int) -> tuple[SupportInstance, ...]:
    """Round-robin over the committed archetype order, replicate by replicate.

    Taking the first ``len(ARCHETYPES) * multiplier`` of this one sequence makes
    every scale hold exactly ``multiplier`` replicates of every archetype AND a
    prefix of every larger scale.  Both properties are needed: completeness so
    no required family drops out at a small scale, nesting so a change between
    scales is a change of ``N``.
    """
    order = archetype_order()
    out: list[SupportInstance] = []
    replicate = 0
    while len(out) < count:
        for archetype_id in order:
            out.append(_instantiate(_ARCHETYPE_BY_ID[archetype_id], replicate))
            if len(out) == count:
                break
        replicate += 1
    return tuple(out)


@lru_cache(maxsize=None)
def build_catalogue(multiplier: int) -> SupportCatalogue:
    """The catalogue at scale ``multiplier``; nested in the smaller scales."""
    return SupportCatalogue(
        scale_id=f"{multiplier}x",
        multiplier=multiplier,
        instances=_instance_sequence(len(ARCHETYPES) * multiplier),
    )


# --------------------------------------------------------------------------
# the persistent store
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SupportObject:
    """One persistent, identity-bearing logical object.

    Three classes, all counting towards ``N``: ``evidence`` (an assumption, and
    the thing a revocation is applied to), ``derived`` (an intermediate
    conclusion, persisted because a chain that is not persisted is not a chain)
    and ``method`` (the competence the store serves).

    The payload carries the object's own identity and its instance, which is
    public metadata of exactly the kind an ordinary database index already
    holds.  It deliberately does NOT carry the archetype, the expected shape or
    the justifications: those are the answer, and ``test_support.py`` refuses
    any arm whose source mentions them.
    """

    object_id: str
    object_class: str
    instance_id: str
    payload: Mapping[str, Any]
    byte_cost: int
    candidates: tuple[str, ...] = ()


class SupportStore:
    """``N`` logical objects with an instrumented read path.

    The same discipline as ``scaling.CompetenceStore`` and, where they overlap,
    the same names: :meth:`read` is the only place ``k`` grows, :meth:`scan` is
    the honest cost of not having an index, and revocation state lives in the
    store rather than on the immutable object so that byte accounting does not
    move when evidence is withdrawn.
    """

    def __init__(self, store_id: str) -> None:
        self.store_id = store_id
        self._objects: dict[str, SupportObject] = {}
        self._order: list[str] = []
        self._revoked: set[str] = set()
        self._store_bytes = 0

    @property
    def n_objects(self) -> int:
        return len(self._objects)

    @property
    def store_bytes(self) -> int:
        return self._store_bytes

    @property
    def object_grammar(self) -> str:
        return "SupportStore.v1(evidence|derived|method)"

    def counts_by_class(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for obj in self._objects.values():
            out[obj.object_class] = out.get(obj.object_class, 0) + 1
        return out

    def add(self, obj: SupportObject) -> str:
        if obj.object_id in self._objects:
            raise ValueError(f"duplicate object id {obj.object_id}")
        self._objects[obj.object_id] = obj
        self._order.append(obj.object_id)
        self._store_bytes += obj.byte_cost
        return obj.object_id

    def object_ids(self) -> tuple[str, ...]:
        return tuple(self._order)

    def is_revoked(self, object_id: str) -> bool:
        return object_id in self._revoked

    def revoke_evidence(self, evidence_id: str) -> None:
        if evidence_id not in self._objects:
            raise KeyError(evidence_id)
        self._revoked.add(evidence_id)

    def revoke_method(self, method_id: str) -> None:
        self._revoked.add(method_id)

    def live_evidence(self) -> frozenset[str]:
        return frozenset(
            oid
            for oid in self._order
            if self._objects[oid].object_class == "evidence" and oid not in self._revoked
        )

    def read(self, object_id: str, ledger: TouchLedger) -> SupportObject:
        obj = self._objects[object_id]
        ledger.touch(obj.object_id, obj.byte_cost)
        return obj

    def scan(self, ledger: TouchLedger) -> Iterator[SupportObject]:
        for object_id in self._order:
            ledger.enumerated_items += 1
            yield self.read(object_id, ledger)


def _payload_bytes(payload: Mapping[str, Any]) -> int:
    return len(canonical_json(dict(payload)).encode("utf-8"))


def populate_store(catalogue: SupportCatalogue) -> SupportStore:
    """Build the store for one catalogue.

    Every arm receives a store built by this one function, so ``N``, the byte
    totals and the declared candidate sets are identical across arms and any
    difference in the reported numbers is a difference of discovery
    architecture and nothing else.
    """
    store = SupportStore(f"support@{catalogue.scale_id}")
    for instance in catalogue.instances:
        for slot, evidence_id in enumerate(instance.evidence_ids):
            payload = {
                "kind": "evidence_block",
                "instance": instance.instance_id,
                "slot": slot,
            }
            store.add(
                SupportObject(
                    object_id=evidence_id,
                    object_class="evidence",
                    instance_id=instance.instance_id,
                    payload=payload,
                    byte_cost=_payload_bytes(payload),
                )
            )
        for derived_id in instance.derived_ids:
            payload = {"kind": "derived", "instance": instance.instance_id}
            store.add(
                SupportObject(
                    object_id=derived_id,
                    object_class="derived",
                    instance_id=instance.instance_id,
                    payload=payload,
                    byte_cost=_payload_bytes(payload),
                    candidates=instance.evidence_ids,
                )
            )
        for method_id in instance.method_ids:
            payload = {"kind": "method", "instance": instance.instance_id}
            store.add(
                SupportObject(
                    object_id=method_id,
                    object_class="method",
                    instance_id=instance.instance_id,
                    payload=payload,
                    byte_cost=_payload_bytes(payload),
                    candidates=instance.evidence_ids,
                )
            )
    return store


# --------------------------------------------------------------------------
# the world and its charged intervention channel
# --------------------------------------------------------------------------


class BudgetExhausted(RuntimeError):
    """Raised when an arm asks for an intervention it cannot afford.

    An exception rather than a silent ``None`` because an arm that ran out of
    budget must not be able to continue as though the answer had been ``no``.
    """


@dataclass
class InterventionMeter:
    """The charged budget.  Mutable, like ``games.Work``, and never a record.

    ``phase`` separates the discovery budget from re-derivation performed at
    revocation or query time.  Only ``DISCOVERY`` draws against ``budget``;
    the other phases are counted and reported but not capped, because an arm
    that discovers nothing is not thereby forbidden from serving a revocation.
    That asymmetry is declared in ``SUPPORT_PLAN["budget_rule"]``.
    """

    budget_per_method: int
    exempt: bool = False
    phase: str = "DISCOVERY"
    spent_by_method: dict[str, int] = None  # type: ignore[assignment]
    by_phase: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.spent_by_method is None:
            self.spent_by_method = {}
        if self.by_phase is None:
            self.by_phase = {}

    def charge(self, method_id: str) -> None:
        if self.phase == "DISCOVERY" and not self.exempt:
            spent = self.spent_by_method.get(method_id, 0)
            if spent >= self.budget_per_method:
                raise BudgetExhausted(
                    f"discovery budget of {self.budget_per_method} interventions for "
                    f"{method_id} is spent"
                )
        self.spent_by_method[method_id] = self.spent_by_method.get(method_id, 0) + 1
        self.by_phase[self.phase] = self.by_phase.get(self.phase, 0) + 1

    @property
    def total(self) -> int:
        return sum(self.spent_by_method.values())

    def phase_total(self, phase: str) -> int:
        return self.by_phase.get(phase, 0)

    def remaining(self, method_id: str) -> int:
        if self.exempt:
            return 2**31
        return self.budget_per_method - self.spent_by_method.get(method_id, 0)


def _derive(
    instance: SupportInstance,
    live_evidence: frozenset[str],
    ledger: TouchLedger | None = None,
) -> frozenset[str]:
    """Least-fixpoint derivation inside one instance.

    The world's mechanism, shared by the charged intervention channel and by
    the scorer.  Sharing it is deliberate: an oracle that computed derivability
    differently from the arms' channel would be scoring a different world.
    What the arms do not get is the *enumeration* over the powerset, which is
    where the oracle's cost and its answer both live.

    Least fixpoint, so a node supported only through a cycle back to itself is
    not IN.  A greatest-fixpoint reading would make the ``CYCLIC`` archetype
    self-supporting and would quietly delete the hardest family in the world.
    """
    inside = set(instance.axiom_ids) | (live_evidence & set(instance.evidence_ids))
    changed = True
    while changed:
        changed = False
        if ledger is not None:
            ledger.search_expansions += 1
        for justification in instance.justifications:
            if justification.consequent in inside:
                continue
            if ledger is not None:
                ledger.predicate_evaluations += len(justification.antecedents)
            if all(a in inside for a in justification.antecedents):
                inside.add(justification.consequent)
                changed = True
    return frozenset(inside)


class SupportWorld:
    """The only channel through which an arm can learn anything about support.

    :meth:`ablate` is the primitive: withdraw a group of evidence blocks, ask
    whether a method still holds, pay for the answer.  It is charged to a
    ledger AND metered against the declared budget, and it is the only place in
    this module an arm may reach.  Everything else an arm knows is public store
    metadata.

    Note what this does NOT give an arm: the justifications, the archetype, or
    any enumeration.  An arm that wants the support family has to decide, one
    intervention at a time, which group to remove next -- which is precisely
    the probe-granularity decision that ``PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_
    NOT_ADAPTED`` says was made at design time in every previous experiment.
    """

    def __init__(self, catalogue: SupportCatalogue) -> None:
        self.catalogue = catalogue
        self._instance_of: dict[str, SupportInstance] = {}
        for instance in catalogue.instances:
            for node_id in instance.all_node_ids:
                self._instance_of[node_id] = instance

    def instance_of(self, node_id: str) -> SupportInstance:
        return self._instance_of[node_id]

    def candidates(self, method_id: str) -> tuple[str, ...]:
        """The DECLARED candidate evidence of a method.

        Declared, exactly as in E3, and stated as a limitation rather than
        hidden: which of a method's blocks matter is discovered here; that they
        are its blocks is given.
        """
        return self._instance_of[method_id].evidence_ids

    def ablate(
        self,
        method_id: str,
        removed: frozenset[str],
        ledger: TouchLedger,
        meter: InterventionMeter,
    ) -> bool:
        """One intervention: does ``method_id`` still hold with ``removed`` gone?

        Charged twice over, on purpose.  The ``meter`` counts it as an
        intervention against the declared budget, which is the coordinate the
        experiment is about.  The ``ledger`` counts the derivation it actually
        cost, which is the coordinate that stops "few interventions" from being
        bought with unbounded search.
        """
        meter.charge(method_id)
        instance = self._instance_of[method_id]
        live = frozenset(instance.evidence_ids) - removed
        ledger.probe_index()
        return method_id in _derive(instance, live, ledger)

    def holds(self, method_id: str, live_evidence: frozenset[str]) -> bool:
        """Uncharged derivability, for the scorer and the scaffolding only."""
        instance = self._instance_of[method_id]
        return method_id in _derive(instance, live_evidence & set(instance.evidence_ids))


@lru_cache(maxsize=None)
def build_world(catalogue: SupportCatalogue) -> SupportWorld:
    return SupportWorld(catalogue)


# --------------------------------------------------------------------------
# shared combinatorial utilities
# --------------------------------------------------------------------------
#
# Deliberately ABOVE the ground-truth banner and deliberately available to the
# arms.  Enumerating subsets, reducing a collection to its minimal elements and
# computing minimal transversals are textbook operations on a family that has
# already been established; none of them can tell an arm which subsets break a
# method, which is the only thing an intervention buys.  Keeping them here
# rather than re-implementing them inside each arm stops an incidental
# asymmetry in set arithmetic from being mistaken for an architectural result.

def subsets_of(items: Sequence[str]) -> list[frozenset[str]]:
    """Every subset of ``items``, smallest first.  The oracle's search space."""
    out: list[frozenset[str]] = []
    n = len(items)
    for mask in range(1 << n):
        out.append(frozenset(items[i] for i in range(n) if mask & (1 << i)))
    out.sort(key=lambda s: (len(s), sorted(s)))
    return out


def minimal_sets(sets: Iterable[frozenset[str]]) -> frozenset[frozenset[str]]:
    """Reduce a collection to its minimal elements under inclusion."""
    kept: list[frozenset[str]] = []
    for candidate in sorted(sets, key=lambda s: (len(s), sorted(s))):
        if any(k <= candidate for k in kept):
            continue
        kept.append(candidate)
    return frozenset(kept)


def hitting_sets(family: Iterable[frozenset[str]]) -> frozenset[frozenset[str]]:
    """Minimal transversals of ``family``.

    Used to state and check the ATMS duality: the minimal support sets are the
    minimal hitting sets of the minimal environments, and vice versa.  Reiter
    (1987); no novelty claimed.
    """
    sets = [frozenset(s) for s in family]
    if not sets:
        return frozenset()
    if any(not s for s in sets):
        return frozenset()
    universe = sorted({e for s in sets for e in s})
    out: list[frozenset[str]] = []
    for candidate in subsets_of(tuple(universe)):
        if not candidate:
            continue
        if not all(candidate & s for s in sets):
            continue
        if any(k <= candidate for k in out):
            continue
        out.append(candidate)
    return frozenset(out)


# --------------------------------------------------------------------------
# ground truth, for the scorer only
# --------------------------------------------------------------------------
#
# Everything from here to the end of this section is the oracle.  No arm calls
# any of it; ``test_support.py`` enforces that by source inspection, the way
# ``test_depend.py`` enforces the leave-one-out separation.  The functions are
# memoised because the scorer runs them over nested catalogues; the memoisation
# is a property of the scorer and charges nothing to any arm.


def oracle_holds(
    catalogue: SupportCatalogue, method_id: str, live_evidence: frozenset[str]
) -> bool:
    return build_world(catalogue).holds(method_id, live_evidence)


@lru_cache(maxsize=None)
def support_family(
    instance: SupportInstance, method_id: str
) -> frozenset[frozenset[str]]:
    """THE ORACLE.  Exhaustive enumeration over the evidence powerset.

    ``S`` is a support set of ``m`` iff ``m`` holds with all evidence live and
    does not hold with ``S`` withdrawn.  Minimal under inclusion.  Exactly
    ``2 ** EVIDENCE_PER_METHOD - 1`` non-empty subsets are tested per method,
    which is 63 at the frozen width and is why that width is frozen.

    Returns the EMPTY family when nothing is load-bearing.  That is a real
    answer and not a missing one: the ``NO_LOAD_BEARING`` archetype has it, and
    an arm that cannot express it will report spurious support there.
    """
    everything = frozenset(instance.evidence_ids)
    if method_id not in _derive(instance, everything):
        raise AssertionError(
            f"{method_id} does not hold on its full evidence; the archetype is malformed "
            "and the support family is undefined rather than empty"
        )
    breaking = [
        candidate
        for candidate in subsets_of(instance.evidence_ids)
        if candidate and method_id not in _derive(instance, everything - candidate)
    ]
    return minimal_sets(breaking)


@lru_cache(maxsize=None)
def oracle_minimal_environments(
    instance: SupportInstance, method_id: str
) -> frozenset[frozenset[str]]:
    """The ATMS label: minimal sets of evidence SUFFICIENT to derive ``m``.

    The dual object.  Computed the same exhaustive way so the duality can be
    asserted rather than assumed.  de Kleer (1986); no novelty claimed.
    """
    sufficient = [
        candidate
        for candidate in subsets_of(instance.evidence_ids)
        if method_id in _derive(instance, candidate)
    ]
    return minimal_sets(sufficient)


@lru_cache(maxsize=None)
def oracle_families(
    catalogue: SupportCatalogue,
) -> frozenset[tuple[str, frozenset[str]]]:
    """The complete true support structure as ``(method_id, minimal set)`` pairs."""
    out: set[tuple[str, frozenset[str]]] = set()
    for instance in catalogue.instances:
        for method_id in instance.method_ids:
            for support_set in support_family(instance, method_id):
                out.add((method_id, support_set))
    return frozenset(out)


def declared_candidate_family(
    catalogue: SupportCatalogue,
) -> frozenset[tuple[str, frozenset[str]]]:
    """The DECLARED candidate structure: "every method rests on all its blocks".

    Reported as a ceiling on the same terms ``depend.declared_edges`` is: it
    is what a system that refuses to discover anything would have to believe,
    and the distance between it and the oracle is the quantity under study.
    """
    return frozenset(
        (method_id, frozenset(instance.evidence_ids))
        for instance in catalogue.instances
        for method_id in instance.method_ids
    )


def oracle_changed_methods(
    catalogue: SupportCatalogue,
    live_before: frozenset[str],
    live_after: frozenset[str],
) -> frozenset[str]:
    """Methods that genuinely stop holding when evidence is withdrawn.

    Evaluated against the live evidence rather than the original evidence, so
    a schedule of successive revocations is scored correctly at every step.
    """
    world = build_world(catalogue)
    withdrawn = live_before - live_after
    changed = set()
    for instance in catalogue.instances:
        if not withdrawn & set(instance.evidence_ids):
            continue
        for method_id in instance.method_ids:
            before = world.holds(method_id, live_before)
            after = world.holds(method_id, live_after)
            if before != after:
                changed.add(method_id)
    return frozenset(changed)


#: The registered vocabulary for a support family's shape.  Fixed before the
#: run so that "what shape is this" is a lookup and not a judgement call.
FAMILY_SHAPES: tuple[str, ...] = (
    "NO_LOAD_BEARING",
    "SINGLE",
    "ALTERNATIVE_ONLY",
    "CONJUNCTIVE_ONLY",
    "HIGHER_ORDER",
    "MIXED",
)


def classify_family(family: Iterable[frozenset[str]]) -> str:
    """Name the shape of one support family.

    ``ALTERNATIVE_ONLY``  every minimal set is a singleton and there are two or
                          more of them: several independent things each have to
                          stay for the method to stand.
    ``CONJUNCTIVE_ONLY``  every minimal set has size two or more, so NO single
                          withdrawal changes anything.  This is exactly the
                          region leave-one-out cannot see, and it is where the
                          C11 rate came from.
    ``HIGHER_ORDER``      some minimal set has size three or more.
    ``MIXED``             both singletons and larger sets, which is the case an
                          arm that stops at its first finding gets wrong while
                          appearing to succeed.
    """
    sets = [frozenset(s) for s in family]
    if not sets:
        return "NO_LOAD_BEARING"
    sizes = sorted(len(s) for s in sets)
    if sizes == [1]:
        return "SINGLE"
    if max(sizes) >= 3 and min(sizes) >= 3:
        return "HIGHER_ORDER"
    if all(s == 1 for s in sizes):
        return "ALTERNATIVE_ONLY"
    if all(s >= 2 for s in sizes):
        return "HIGHER_ORDER" if max(sizes) >= 3 else "CONJUNCTIVE_ONLY"
    return "MIXED"


def family_shapes(catalogue: SupportCatalogue) -> dict[str, str]:
    """The registered shape of every archetype, read off the oracle."""
    out: dict[str, str] = {}
    for instance in catalogue.first_replicates():
        shapes = {
            classify_family(support_family(instance, m)) for m in instance.method_ids
        }
        out[instance.archetype_id] = "/".join(sorted(shapes))
    return out


def leave_one_out_blind_methods(catalogue: SupportCatalogue) -> tuple[str, ...]:
    """Methods with at least one minimal support set that has no singleton subset.

    The generalisation of ``depend.redundant_support_methods``.  A method is
    listed here when leave-one-out, run perfectly, still misses part of its
    support family -- whether it misses all of it (``CONJUNCTIVE_ONLY``,
    ``HIGHER_ORDER``) or only some (``MIXED``).
    """
    out = []
    for instance in catalogue.instances:
        for method_id in instance.method_ids:
            family = support_family(instance, method_id)
            if any(len(s) >= 2 for s in family):
                out.append(method_id)
    return tuple(out)


# --------------------------------------------------------------------------
# the registered revocation schedule
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RevocationStep:
    """One registered revocation, named before the numbers exist."""

    step_id: str
    archetype_id: str
    instance_id: str
    evidence_ids: tuple[str, ...]
    intent: str


@lru_cache(maxsize=None)
def revocation_schedule(catalogue: SupportCatalogue) -> tuple[RevocationStep, ...]:
    """The registered schedule: every archetype's own steps, replicate 0 only.

    Restricting the schedule to the first replicate keeps it CONSTANT across
    scales, so a change in revocation work between scales is a change in what
    an arm has to search rather than a change in how many revocations it
    served.  Discovery still runs over every method at every scale, which is
    where ``N`` enters.

    The steps of one archetype run consecutively and no two archetypes share an
    instance, so no two families interact at all.
    """
    steps: list[RevocationStep] = []
    for instance in catalogue.first_replicates():
        archetype = _ARCHETYPE_BY_ID[instance.archetype_id]
        for index, evidence_ids in enumerate(instance.revocation_steps):
            steps.append(
                RevocationStep(
                    step_id=f"{instance.archetype_id}:{index}",
                    archetype_id=instance.archetype_id,
                    instance_id=instance.instance_id,
                    evidence_ids=evidence_ids,
                    intent=archetype.note,
                )
            )
    return tuple(steps)


# --------------------------------------------------------------------------
# the support-family record
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SupportFamilyRecord:
    """One arm's believed support structure, scored against the powerset oracle.

    ``missing`` is the dangerous direction -- a minimal support set the arm
    does not know about, which is a belief it will leave standing when that set
    is withdrawn.  ``extra`` is the wasteful one.  They are kept apart here for
    the same reason stale survivors and collateral invalidations are kept apart
    in the revocation endpoint, and there is deliberately no field that adds
    them.
    """

    arm_id: str
    scale_id: str
    n_true_sets: int
    n_believed_sets: int
    n_correct_sets: int
    interventions: int
    disclosure_work: int
    missing: tuple[tuple[str, tuple[str, ...]], ...]
    extra: tuple[tuple[str, tuple[str, ...]], ...]
    per_archetype: Mapping[str, Mapping[str, float]]
    budget_exhausted_methods: int

    @property
    def precision(self) -> float:
        if self.n_believed_sets == 0:
            return 1.0 if self.n_true_sets == 0 else 0.0
        return self.n_correct_sets / self.n_believed_sets

    @property
    def recall(self) -> float:
        if self.n_true_sets == 0:
            return 1.0
        return self.n_correct_sets / self.n_true_sets

    @property
    def exact(self) -> bool:
        return not self.missing and not self.extra

    def as_dict(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "scale_id": self.scale_id,
            "true_support_sets": self.n_true_sets,
            "believed_support_sets": self.n_believed_sets,
            "correct_support_sets": self.n_correct_sets,
            "precision": round(self.precision, 6),
            "recall": round(self.recall, 6),
            "exact": self.exact,
            "interventions": self.interventions,
            "disclosure_work": self.disclosure_work,
            "missed_sets": len(self.missing),
            "spurious_sets": len(self.extra),
            "missed_sample": [[m, list(s)] for m, s in self.missing[:8]],
            "spurious_sample": [[m, list(s)] for m, s in self.extra[:8]],
            "budget_exhausted_methods": self.budget_exhausted_methods,
            "per_archetype": {k: dict(v) for k, v in self.per_archetype.items()},
        }


def score_family(
    arm_id: str,
    catalogue: SupportCatalogue,
    believed: Mapping[str, Iterable[frozenset[str]]],
    *,
    interventions: int,
    disclosure_work: int,
    budget_exhausted_methods: int = 0,
    sample_cap: int = 32,
) -> SupportFamilyRecord:
    """Score a believed support structure against the powerset oracle.

    The scorer, and the only place ``support_family`` is consulted for this
    endpoint.  Per-archetype precision and recall are reported alongside the
    aggregate, because an arm that is perfect on nine archetypes and blind on
    two has a blindness, and an aggregate that averages it away describes an
    arm that does not exist.
    """
    truth = oracle_families(catalogue)
    claimed = frozenset(
        (method_id, frozenset(s)) for method_id, sets in believed.items() for s in sets
    )
    missing = tuple(sorted((m, tuple(sorted(s))) for m, s in truth - claimed))
    extra = tuple(sorted((m, tuple(sorted(s))) for m, s in claimed - truth))

    per_archetype: dict[str, dict[str, float]] = {}
    for archetype_id in (a.archetype_id for a in ARCHETYPES):
        methods = {
            m
            for instance in catalogue.instances
            if instance.archetype_id == archetype_id
            for m in instance.method_ids
        }
        t = {p for p in truth if p[0] in methods}
        c = {p for p in claimed if p[0] in methods}
        correct = len(t & c)
        per_archetype[archetype_id] = {
            "true_sets": len(t),
            "believed_sets": len(c),
            "correct_sets": correct,
            "precision": round(1.0 if not c else correct / len(c), 6)
            if (c or not t)
            else 0.0,
            "recall": round(1.0 if not t else correct / len(t), 6),
            "exact": t == c,
        }
    return SupportFamilyRecord(
        arm_id=arm_id,
        scale_id=catalogue.scale_id,
        n_true_sets=len(truth),
        n_believed_sets=len(claimed),
        n_correct_sets=len(truth & claimed),
        interventions=interventions,
        disclosure_work=disclosure_work,
        missing=missing[:sample_cap],
        extra=extra[:sample_cap],
        per_archetype=per_archetype,
        budget_exhausted_methods=budget_exhausted_methods,
    )
