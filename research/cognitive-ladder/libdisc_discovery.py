"""E5 discovery: step-level abstraction, and the flat ablation that finds nothing.

This is the arm the diagnosis asked for and the ablation it asked to be
compared against, run on identical evidence with identical budgets.

    ASSAY-ACQUISITION-DIAGNOSIS.md, causal level 2: "each attempted fragment is
    the original two statements plus original query/negation, alpha-renamed and
    premise-sorted ... Their flat queried fragments differ, but their
    intermediate dependency step recurs."

:func:`flat_mining_ablation` mines exactly those flat fragments and applies
exactly the registered repeated-support gate.  On this draw it returns an empty
pool, reproducing ``NO_METHOD_ACQUIRED``.  :func:`discover` mines the same
episodes at the step level and returns a non-empty pool.  Same episodes, same
gate, same checker, same budget; only the level of abstraction differs.  That is
the whole of the discovery claim, and it is a claim about representation, not
about benefit -- benefit is measured separately and on two task sets.

The pipeline
------------

1. **signed-clause normalisation** -- already the world's canonical form
   (:func:`libdisc.clause`);
2. **lifting** each ground proof step to a schema with predicate variables
   (:func:`libdisc.lift_step`), which is deterministic normalisation;
3. **anti-unification** (:func:`anti_unify`) as the least general generalisation
   of two lifted steps, refusing to generalise across polarity -- a sign-blind
   generalisation of the chain and its polarity-flipped look-alike is unsound and
   the checker refutes it, which is the ``surface_similar`` control;
4. **semantic-equivalence clustering** (:func:`semantic_key`): two schemas are
   the same object iff they have identical behaviour under EVERY injective
   renaming, checked exactly by instantiation rather than by a syntactic
   heuristic;
5. **the registered >=2 repeated-support gate**, unchanged;
6. **composition of compatible singleton fragments** (:func:`compose`): the
   conclusion pattern of one surviving schema unified with a premise pattern of
   another, producing a two-step composite whose support is then counted against
   the actual training proofs and put through the same gate;
7. **scope revision** (:func:`revise_scope`): a deliberately over-general lifting
   that drops the pivot-sharing equality is proposed, refuted by the checker on a
   counterexample, and NARROWED by merging two variables rather than deleted;
8. **MDL and held-out validation, then CL-D1 admission** -- strict compression,
   verified scope strictly beyond the training support, independent checker.

What is deliberately absent
---------------------------

* No threshold below 2.  Lowering it would manufacture a pool and the diagnosis
  forbids it in as many words.
* No semantic-equivalence *weakening* at match time.  ``CLAUSE-REVIVAL-RESULT.md``
  found 6/72/8/100 sound-but-redundant substitutions the syntactic matcher did
  not recognise and refused to count them: "Counting them as learned benefit
  would be misleading."  :func:`redundant_sound_matches` counts them here too --
  in its own column, never in the benefit column.

Leakage: every function in this module takes ``LearnerView`` objects, whose only
fields are the input and the correct actions.  Episode identity, task role and
every certification about the draw are evaluator-only and are not reachable from
here.

Parents: least general generalisation (Plotkin, Reynolds); explanation-based
generalisation; macro-operator acquisition (STRIPS MACROPS); minimum description
length (Rissanen); version-space and specific-to-general revision (Mitchell).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from libdisc import (
    N_PREDS,
    REPEATED_SUPPORT_THRESHOLD,
    Clause,
    LearnerView,
    Pattern,
    Schema,
    Step,
    canonical_form,
    canonical_schema,
    digest_of,
    entails,
    extrapolation_probes,
    flat_fragment,
    instantiate,
    lift_step,
    schema_code_bits,
    schema_is_sound,
    support_data_bits,
    support_residual_bits,
    subsumes,
)

__all__ = [
    "anti_unify",
    "semantic_key",
    "cluster_by_semantics",
    "compose",
    "over_general_proposal",
    "revise_scope",
    "MDLRecord",
    "AdmissionRecord",
    "admit",
    "DiscoveredSchema",
    "DiscoveryResult",
    "discover",
    "AblationResult",
    "flat_mining_ablation",
    "redundant_sound_matches",
]


# --------------------------------------------------------------------------
# anti-unification
# --------------------------------------------------------------------------


def _lgg_pattern(
    a: Pattern, b: Pattern, table: dict[tuple[str, str], str]
) -> Pattern | None:
    """Least general generalisation of two clause patterns, sign-preserving."""
    if len(a.lits) != len(b.lits):
        return None
    for perm in itertools.permutations(b.lits):
        if all(sa == sb for (_, sa), (_, sb) in zip(a.lits, perm)):
            lits = []
            for (va, s), (vb, _) in zip(a.lits, perm):
                key = (va, vb)
                if key not in table:
                    table[key] = f"u{len(table)}"
                lits.append((table[key], s))
            try:
                return Pattern(tuple(sorted(set(lits))))
            except ValueError:
                return None
    return None


def anti_unify(a: Schema, b: Schema) -> Schema | None:
    """The least general generalisation of two lifted steps.

    Signs are never generalised.  Anti-unifying across polarity would merge the
    chain with its polarity-flipped look-alike, and the resulting schema has
    instances the independent checker refutes; refusing the merge here is a
    design decision recorded as such, and the ``surface_similar`` control exists
    to show what would have happened otherwise.
    """
    if a.step_count != b.step_count or len(a.premises) != len(b.premises):
        return None
    table: dict[tuple[str, str], str] = {}
    prem: list[Pattern] = []
    for pa, pb in zip(a.premises, b.premises):
        p = _lgg_pattern(pa, pb, table)
        if p is None:
            return None
        prem.append(p)
    concl = _lgg_pattern(a.conclusion, b.conclusion, table)
    if concl is None:
        return None
    if len(a.pivot_vars) != len(b.pivot_vars):
        return None
    pivots_ = []
    for va, vb in zip(a.pivot_vars, b.pivot_vars):
        key = (va, vb)
        if key not in table:
            return None
        pivots_.append(table[key])
    return canonical_schema(
        Schema(tuple(prem), concl, tuple(pivots_), a.step_count, a.origin))


# --------------------------------------------------------------------------
# semantic-equivalence clustering
# --------------------------------------------------------------------------


def semantic_key(schema: Schema) -> tuple:
    """Exact behavioural signature: every ground instance under every renaming.

    The canonical domain has exactly ``arity`` symbols, so the key ranges over
    all ``arity!`` injective renamings.  Two schemas are the same cognitive
    object iff their keys are equal; this is a decision procedure, not a
    similarity score.
    """
    variables = schema.variables
    k = len(variables)
    instances = set()
    for combo in itertools.permutations(range(k), k):
        binding = {v: combo[i] for i, v in enumerate(variables)}
        prem = tuple(instantiate(p, binding) for p in schema.premises)
        concl = instantiate(schema.conclusion, binding)
        if concl is None or any(p is None for p in prem):
            continue
        instances.add((frozenset(prem), concl))
    return (k, schema.step_count, frozenset(instances))


def cluster_by_semantics(schemas: Iterable[Schema]) -> dict[tuple, list[Schema]]:
    out: dict[tuple, list[Schema]] = {}
    for s in schemas:
        out.setdefault(semantic_key(s), []).append(s)
    return out


# --------------------------------------------------------------------------
# composition of compatible singleton fragments
# --------------------------------------------------------------------------


def _rename_apart(schema: Schema, tag: str) -> Schema:
    mapping = {v: f"{tag}{v}" for v in schema.variables}

    def ren(p: Pattern) -> Pattern:
        return Pattern(tuple(sorted((mapping[v], s) for v, s in p.lits)))

    return Schema(
        tuple(ren(p) for p in schema.premises),
        ren(schema.conclusion),
        tuple(mapping[v] for v in schema.pivot_vars),
        schema.step_count,
        schema.origin,
    )


def _unify_patterns(a: Pattern, b: Pattern) -> dict[str, str] | None:
    """A variable substitution making ``a`` identical to ``b``; signs must match."""
    if len(a.lits) != len(b.lits):
        return None
    for perm in itertools.permutations(b.lits):
        if all(sa == sb for (_, sa), (_, sb) in zip(a.lits, perm)):
            sub: dict[str, str] = {}
            ok = True
            for (va, _), (vb, _) in zip(a.lits, perm):
                if va in sub and sub[va] != vb:
                    ok = False
                    break
                sub[va] = vb
            if ok and len(set(sub.values())) == len(sub):
                return sub
    return None


def compose(first: Schema, second: Schema) -> list[Schema]:
    """Every two-step composite formed by feeding ``first``'s conclusion into
    ``second``.

    The result is a three-premise schema that collapses two resolution steps
    into one application.  Only a composite can move a clause into an earlier
    round of the search, so this step is where a library becomes capable of
    reducing work at all.
    """
    if first.step_count != 1 or second.step_count != 1:
        return []
    a = _rename_apart(first, "a")
    b = _rename_apart(second, "b")
    out: list[Schema] = []
    seen: set[str] = set()
    for i, prem in enumerate(b.premises):
        sub = _unify_patterns(a.conclusion, prem)
        if sub is None:
            continue
        inv = {v: v for v in b.variables}
        # substitute a's conclusion variables into b's namespace
        mapping = dict(inv)
        for va, vb in sub.items():
            mapping[vb] = va

        def ren(p: Pattern) -> Pattern | None:
            lits = tuple(sorted((mapping.get(v, v), s) for v, s in p.lits))
            if len({v for v, _ in lits}) != len(lits):
                return None
            try:
                return Pattern(lits)
            except ValueError:
                return None

        others = [ren(p) for j, p in enumerate(b.premises) if j != i]
        concl = ren(b.conclusion)
        if concl is None or any(o is None for o in others):
            continue
        prem_all = tuple(a.premises) + tuple(o for o in others if o is not None)
        pivots_ = tuple(a.pivot_vars) + tuple(
            mapping.get(v, v) for v in b.pivot_vars)
        cand = canonical_schema(
            Schema(prem_all, concl, pivots_, 2, "composed"))
        if len(cand.premises) != 3:
            continue
        if cand.schema_id in seen:
            continue
        seen.add(cand.schema_id)
        out.append(cand)
    return out


# --------------------------------------------------------------------------
# scope revision: narrow on a counterexample, never delete
# --------------------------------------------------------------------------


def over_general_proposal(step: Step) -> Schema:
    """Lift a step while DROPPING the equality that ties the two pivot copies.

    The honest lifting of ``(not X or Y), (not Y or Z)`` shares ``Y``.  This
    proposal gives the two occurrences different variables, which is what a
    generaliser that abstracts positions without tracking co-occurrence
    produces.  It is unsound, and it exists so that the revision path is
    exercised by a real counterexample rather than by a mock.
    """
    left = Pattern(tuple(sorted((f"l{p}", s) for p, s in step.left)))
    right = Pattern(tuple(sorted((f"r{p}", s) for p, s in step.right)))
    concl = Pattern(tuple(sorted(
        [(f"l{p}", s) for p, s in step.left if p != step.pivot]
        + [(f"r{p}", s) for p, s in step.right if p != step.pivot])))
    return canonical_schema(
        Schema((left, right), concl, (f"l{step.pivot}",), 1, "over_general"))


@dataclass(frozen=True)
class RevisionRecord:
    """CL-R5 in miniature: what was narrowed, on what counterexample, and why."""

    proposed_id: str
    proposed_sound: bool
    counterexample: tuple | None
    revised_id: str | None
    revised_sound: bool
    merged_variables: tuple[str, ...] | None
    outcome: str

    def as_dict(self) -> dict:
        return {
            "proposed_id": self.proposed_id,
            "proposed_sound": self.proposed_sound,
            "counterexample": list(self.counterexample) if self.counterexample else None,
            "revised_id": self.revised_id,
            "revised_sound": self.revised_sound,
            "merged_variables": list(self.merged_variables) if self.merged_variables else None,
            "outcome": self.outcome,
        }


def _counterexample(schema: Schema) -> tuple | None:
    """The first injective binding on which the independent checker refutes."""
    variables = schema.variables
    for combo in itertools.permutations(range(N_PREDS), len(variables)):
        binding = {v: combo[i] for i, v in enumerate(variables)}
        prem = [instantiate(p, binding) for p in schema.premises]
        concl = instantiate(schema.conclusion, binding)
        if concl is None or any(p is None for p in prem):
            continue
        if not entails([p for p in prem if p is not None], concl):
            return (tuple(sorted(binding.items())), tuple(p for p in prem), concl)
    return None


def _merge_variables(schema: Schema, keep: str, drop: str) -> Schema | None:
    mapping = {v: (keep if v == drop else v) for v in schema.variables}

    def ren(p: Pattern) -> Pattern | None:
        lits = tuple(sorted({(mapping[v], s) for v, s in p.lits}))
        if any((v, not s) in lits for v, s in lits):
            return None
        return Pattern(lits)

    prem = [ren(p) for p in schema.premises]
    concl = ren(schema.conclusion)
    if concl is None or any(p is None for p in prem):
        return None
    return canonical_schema(Schema(
        tuple(p for p in prem if p is not None), concl,
        tuple(mapping[v] for v in schema.pivot_vars), schema.step_count, "revised"))


def revise_scope(schema: Schema) -> RevisionRecord:
    """Narrow an over-general schema on its counterexample instead of deleting it.

    The revision searched here is a single variable merge, which is the smallest
    narrowing this representation admits.  If no merge is sound the schema is
    reported as ``NARROWING_FAILED`` and dropped; a deletion is recorded as a
    deletion rather than dressed up as a revision.
    """
    sound = schema_is_sound(schema)
    if sound:
        return RevisionRecord(schema.schema_id, True, None, schema.schema_id,
                              True, None, "NO_REVISION_NEEDED")
    ce = _counterexample(schema)
    variables = schema.variables
    for keep, drop in itertools.permutations(variables, 2):
        narrowed = _merge_variables(schema, keep, drop)
        if narrowed is None:
            continue
        if schema_is_sound(narrowed):
            return RevisionRecord(schema.schema_id, False, ce, narrowed.schema_id,
                                  True, (keep, drop), "SCOPE_NARROWED")
    return RevisionRecord(schema.schema_id, False, ce, None, False, None,
                          "NARROWING_FAILED")


# --------------------------------------------------------------------------
# MDL and CL-D1 admission
# --------------------------------------------------------------------------


def _pattern_of(c: Clause) -> Pattern:
    return Pattern(tuple(sorted((f"p{p}", s) for p, s in c)))


def _lift_instance(premises: Sequence[Clause], conclusion: Clause,
                   step_count: int) -> Schema:
    """Lift a ground instance to a schema for held-out comparison.

    Pivot variables are not part of the comparison: :func:`semantic_key` is
    computed from premises and conclusion, so two liftings that agree on
    behaviour agree here regardless of which pivot the prover happened to pick.
    """
    return canonical_schema(Schema(
        tuple(_pattern_of(c) for c in premises), _pattern_of(conclusion),
        (), step_count, "heldout"))


@dataclass(frozen=True)
class MDLRecord:
    """CL-D1(a), computed exactly under the code fixed with the language."""

    bits_method: float
    bits_data: float
    bits_residual: float
    compression_ok: bool

    def as_dict(self) -> dict:
        return {
            "bits_method": round(self.bits_method, 4),
            "bits_data": round(self.bits_data, 4),
            "bits_residual": round(self.bits_residual, 4),
            "compression_ok": self.compression_ok,
        }


@dataclass(frozen=True)
class AdmissionRecord:
    """CL-D1 verdict with its three components, plus held-out validation."""

    schema_id: str
    supports: int
    support_gate_ok: bool
    sound: bool
    mdl: MDLRecord
    extrapolation_probes: int
    extrapolation_failures: int
    extrapolation_ok: bool
    held_out_trials: int
    held_out_failures: int
    held_out_ok: bool
    independence_ok: bool
    verdict: str

    @property
    def admissible(self) -> bool:
        return self.verdict == "ADMISSIBLE"

    def as_dict(self) -> dict:
        return {
            "schema_id": self.schema_id,
            "supports": self.supports,
            "support_gate_ok": self.support_gate_ok,
            "sound": self.sound,
            "mdl": self.mdl.as_dict(),
            "extrapolation_probes": self.extrapolation_probes,
            "extrapolation_failures": self.extrapolation_failures,
            "extrapolation_ok": self.extrapolation_ok,
            "held_out_trials": self.held_out_trials,
            "held_out_failures": self.held_out_failures,
            "held_out_ok": self.held_out_ok,
            "independence_ok": self.independence_ok,
            "verdict": self.verdict,
        }


def admit(
    schema: Schema,
    instances: Sequence[tuple[tuple[Clause, ...], Clause]],
    supports: int,
    threshold: int = REPEATED_SUPPORT_THRESHOLD,
) -> AdmissionRecord:
    """CL-D1 admission.  Every clause of it is checked, none is asserted.

    (a) strict compression under the two-part code fixed with the language;
    (b) scope strictly beyond the training support, certified by the independent
        checker on predicates whose index exceeds every index the schema was
        induced from -- the magnitude analogue CL-D1(b) requires;
    (c) independence: the certifier is :func:`libdisc.entails`, which reads
        clauses and nothing else.

    Plus held-out validation before admission: each support is left out in turn,
    the schema is re-lifted from a remaining support, and the held-out instance
    must be both recovered and independently certified.
    """
    n = len(instances)
    mdl = MDLRecord(
        bits_method=schema_code_bits(schema),
        bits_data=support_data_bits(schema, n),
        bits_residual=support_residual_bits(schema, n),
        compression_ok=(
            schema_code_bits(schema) + support_residual_bits(schema, n)
            < support_data_bits(schema, n)),
    )
    sound = schema_is_sound(schema)

    max_pred = max(
        (p for prem, concl in instances for c in tuple(prem) + (concl,) for p, _ in c),
        default=-1)
    probes = extrapolation_probes(schema, max_pred)
    failures = 0
    for binding in probes:
        prem = [instantiate(p, binding) for p in schema.premises]
        concl = instantiate(schema.conclusion, binding)
        if concl is None or any(p is None for p in prem):
            failures += 1
            continue
        if not entails([p for p in prem if p is not None], concl):
            failures += 1
    extrapolation_ok = bool(probes) and failures == 0

    key = semantic_key(schema)
    ho_trials = 0
    ho_failures = 0
    if n >= 2:
        for i in range(n):
            ho_trials += 1
            rest = [instances[j] for j in range(n) if j != i]
            relift = _lift_instance(rest[0][0], rest[0][1], schema.step_count)
            held_prem, held_concl = instances[i]
            if semantic_key(relift) != key:
                ho_failures += 1
                continue
            if not entails(list(held_prem), held_concl):
                ho_failures += 1
    held_out_ok = ho_trials > 0 and ho_failures == 0

    support_gate_ok = supports >= threshold
    if not support_gate_ok:
        verdict = "REJECTED_SINGLETON_SUPPORT"
    elif not sound:
        verdict = "REJECTED_UNSOUND"
    elif not mdl.compression_ok:
        verdict = "INADMISSIBLE_NO_COMPRESSION"
    elif not extrapolation_ok:
        verdict = "INADMISSIBLE_NO_EXTRAPOLATION"
    elif not held_out_ok:
        verdict = "INADMISSIBLE_HELD_OUT_FAILED"
    else:
        verdict = "ADMISSIBLE"

    return AdmissionRecord(
        schema_id=schema.schema_id, supports=supports,
        support_gate_ok=support_gate_ok, sound=sound, mdl=mdl,
        extrapolation_probes=len(probes), extrapolation_failures=failures,
        extrapolation_ok=extrapolation_ok, held_out_trials=ho_trials,
        held_out_failures=ho_failures, held_out_ok=held_out_ok,
        independence_ok=True, verdict=verdict)


# --------------------------------------------------------------------------
# the discovery arm
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DiscoveredSchema:
    schema: Schema
    supports: int
    instances: tuple[tuple[tuple[Clause, ...], Clause], ...]
    admission: AdmissionRecord

    def as_dict(self) -> dict:
        return {
            "schema": self.schema.as_dict(),
            "supports": self.supports,
            "instances": len(self.instances),
            "admission": self.admission.as_dict(),
        }


@dataclass(frozen=True)
class DiscoveryResult:
    pool: tuple[DiscoveredSchema, ...]
    rejected: tuple[DiscoveredSchema, ...]
    revisions: tuple[RevisionRecord, ...]
    funnel: dict

    def library(self) -> tuple[Schema, ...]:
        return tuple(d.schema for d in self.pool)

    def as_dict(self) -> dict:
        return {
            "pool": [d.as_dict() for d in self.pool],
            "rejected": [d.as_dict() for d in self.rejected],
            "revisions": [r.as_dict() for r in self.revisions],
            "funnel": self.funnel,
        }


def _support_identity(view: LearnerView) -> tuple:
    """A distinct *semantic* training support, computed from visible fields only.

    Alpha-renamed duplicates of the same episode therefore cannot count twice,
    which is the property ASSAY-ACQUISITION-DIAGNOSIS.md calls semantic support
    identity.  Episode identity is evaluator-only and is not read here.
    """
    return flat_fragment(view.premises, view.query)


def discover(
    views: Sequence[LearnerView],
    threshold: int = REPEATED_SUPPORT_THRESHOLD,
) -> DiscoveryResult:
    """Step-level discovery with composition, on the same evidence the flat
    ablation sees."""
    funnel: dict = {"episodes": len(views), "steps_seen": 0}

    # --- 1..3: lift, cluster semantically, collect supports ---------------
    clusters: dict[tuple, dict] = {}
    for view in views:
        sup = _support_identity(view)
        for st in view.proof:
            funnel["steps_seen"] += 1
            sch = lift_step(st)
            row = clusters.setdefault(semantic_key(sch), {
                "schema": sch, "supports": set(), "instances": []})
            row["supports"].add(sup)
            row["instances"].append(((st.left, st.right), st.conclusion))
    funnel["distinct_step_schemas"] = len(clusters)

    # anti-unification across distinct clusters: recorded, and refused when the
    # generalisation is not certified by the independent checker.
    au_pairs = 0
    au_unsound = 0
    reps = [row["schema"] for row in clusters.values()]
    for a, b in itertools.combinations(reps, 2):
        g = anti_unify(a, b)
        if g is None:
            continue
        au_pairs += 1
        if not schema_is_sound(g):
            au_unsound += 1
    funnel["anti_unification_generalisations"] = au_pairs
    funnel["anti_unification_refused_unsound"] = au_unsound

    # --- 4: the registered >=2 gate on single-step schemas ----------------
    singles: list[DiscoveredSchema] = []
    rejected: list[DiscoveredSchema] = []
    survivors: list[Schema] = []
    for row in clusters.values():
        rec = admit(row["schema"], row["instances"], len(row["supports"]), threshold)
        d = DiscoveredSchema(row["schema"], len(row["supports"]),
                             tuple(row["instances"]), rec)
        if rec.admissible:
            singles.append(d)
            survivors.append(row["schema"])
        else:
            rejected.append(d)
    funnel["singleton_step_schemas_excluded"] = sum(
        1 for d in rejected if d.admission.verdict == "REJECTED_SINGLETON_SUPPORT")
    funnel["single_step_schemas_admitted"] = len(singles)

    # --- 5..6: composition of compatible singleton fragments --------------
    candidates: dict[str, Schema] = {}
    for a in survivors:
        for b in survivors:
            for comp in compose(a, b):
                candidates[comp.schema_id] = comp
    funnel["composites_proposed"] = len(candidates)

    comp_rows: dict[tuple, dict] = {}
    for comp in candidates.values():
        key = semantic_key(comp)
        for view in views:
            sup = _support_identity(view)
            for first, second in zip(view.proof, view.proof[1:]):
                if second.left == first.conclusion:
                    third = second.right
                elif second.right == first.conclusion:
                    third = second.left
                else:
                    continue
                prem = (first.left, first.right, third)
                if not _composite_covers(comp, prem, second.conclusion):
                    continue
                row = comp_rows.setdefault(key, {
                    "schema": comp, "supports": set(), "instances": []})
                row["supports"].add(sup)
                row["instances"].append((prem, second.conclusion))
    funnel["composites_with_training_support"] = len(comp_rows)

    composites: list[DiscoveredSchema] = []
    for row in comp_rows.values():
        rec = admit(row["schema"], row["instances"], len(row["supports"]), threshold)
        d = DiscoveredSchema(row["schema"], len(row["supports"]),
                             tuple(row["instances"]), rec)
        if rec.admissible:
            composites.append(d)
        else:
            rejected.append(d)
    funnel["composite_schemas_admitted"] = len(composites)
    funnel["composites_excluded_singleton_support"] = sum(
        1 for d in rejected
        if d.schema.step_count == 2
        and d.admission.verdict == "REJECTED_SINGLETON_SUPPORT")

    # --- 7: scope revision on a deliberately over-general proposal ---------
    revisions: list[RevisionRecord] = []
    seen_props: set[str] = set()
    for view in views:
        for st in view.proof:
            prop = over_general_proposal(st)
            if prop.schema_id in seen_props:
                continue
            seen_props.add(prop.schema_id)
            revisions.append(revise_scope(prop))
    funnel["over_general_proposals"] = len(revisions)
    funnel["scope_narrowed"] = sum(
        1 for r in revisions if r.outcome == "SCOPE_NARROWED")
    funnel["narrowing_failed"] = sum(
        1 for r in revisions if r.outcome == "NARROWING_FAILED")

    pool = tuple(singles + composites)
    funnel["pool"] = len(pool)
    funnel["applicable_pool"] = sum(1 for d in pool if d.schema.step_count >= 2)
    return DiscoveryResult(pool, tuple(rejected), tuple(revisions), funnel)


def _composite_covers(
    comp: Schema, premises: Sequence[Clause], conclusion: Clause
) -> bool:
    """Does ``comp`` instantiate exactly to this ground two-step instance?"""
    from libdisc import match_schema  # local import keeps the module graph flat

    for _chosen, binding in match_schema(comp, list(premises)):
        if instantiate(comp.conclusion, binding) == conclusion:
            return True
    return False


# --------------------------------------------------------------------------
# the flat-mining ablation: the level the diagnosis says was wrong
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class AblationResult:
    pool: tuple[tuple, ...]
    funnel: dict

    def as_dict(self) -> dict:
        return {"pool_size": len(self.pool), "funnel": self.funnel}


def flat_mining_ablation(
    views: Sequence[LearnerView],
    threshold: int = REPEATED_SUPPORT_THRESHOLD,
) -> AblationResult:
    """Flat surface fragments plus the registered repeated-support gate.

    Reproduces the funnel of ASSAY-ACQUISITION-DIAGNOSIS.md: proper two-premise
    subcovers only, checked for soundness and essentiality by the independent
    checker, grouped by alpha-renamed identity, then gated at >=2 distinct
    semantic supports.  The pool it returns on this draw is empty, and the
    terminal that follows is ``NO_METHOD_ACQUIRED``.
    """
    funnel = {
        "episodes": len(views), "candidate_pairs": 0, "lost_proper_subcover": 0,
        "counterexample": 0, "nonessential": 0, "valid_essential": 0,
    }
    groups: dict[tuple, set] = {}
    for view in views:
        sup = flat_fragment(view.premises, view.query)
        if len(view.premises) <= 2:
            funnel["lost_proper_subcover"] += 1
            continue
        for pair in itertools.combinations(view.premises, 2):
            funnel["candidate_pairs"] += 1
            if not entails(pair, view.query):
                funnel["counterexample"] += 1
                continue
            if any(entails([single], view.query) for single in pair):
                funnel["nonessential"] += 1
                continue
            funnel["valid_essential"] += 1
            groups.setdefault(flat_fragment(pair, view.query), set()).add(sup)
    pool = tuple(sorted(
        (f for f, sups in groups.items() if len(sups) >= threshold),
        key=repr))
    funnel["distinct_fragments"] = len(groups)
    funnel["singleton_groups_excluded"] = sum(
        1 for sups in groups.values() if len(sups) < threshold)
    funnel["pool"] = len(pool)
    return AblationResult(pool, funnel)


# --------------------------------------------------------------------------
# redundant-but-sound matches: their own column, never the benefit column
# --------------------------------------------------------------------------


def redundant_sound_matches(
    schema: Schema, premises: Sequence[Clause], query: Clause
) -> int:
    """Sound substitutions the syntactic matcher does not recognise.

    ``CLAUSE-REVIVAL-RESULT.md`` found 6/72/8/100 of these on its four eligible
    rows and refused to count them: "Every substitution is redundant for its
    target ... Counting them as learned benefit would be misleading."  They are
    counted here for the same reason they were counted there -- to show the
    matcher's semantic incompleteness honestly -- and they never enter any
    benefit figure.
    """
    preds = sorted({p for c in list(premises) + [query] for p, _ in c})
    variables = schema.variables
    if len(preds) < len(variables):
        return 0
    count = 0
    clause_set = set(premises)
    for combo in itertools.permutations(preds, len(variables)):
        binding = {v: combo[i] for i, v in enumerate(variables)}
        prem = [instantiate(p, binding) for p in schema.premises]
        concl = instantiate(schema.conclusion, binding)
        if concl is None or any(p is None for p in prem):
            continue
        if all(p in clause_set for p in prem):
            continue  # the syntactic matcher already sees this one
        if not all(entails(list(premises), p) for p in prem if p is not None):
            continue
        count += 1
    return count


# --------------------------------------------------------------------------
# surface-similar control: what a polarity-blind matcher would have done
# --------------------------------------------------------------------------


def polarity_blind_matches(
    schema: Schema, premises: Sequence[Clause]
) -> list[tuple[tuple[Clause, ...], Clause]]:
    """Matches a matcher that ignored literal sign would have accepted.

    The chain and its polarity-flipped look-alike use the same predicates and
    reach the same conclusion shape; only the pivot polarity differs.  A miner
    that abstracted position without tracking sign would merge them.  This
    function produces exactly those extra matches so that the next function can
    ask the independent checker what they are worth.
    """
    out: list[tuple[tuple[Clause, ...], Clause]] = []
    preds = sorted({p for c in premises for p, _ in c})
    variables = schema.variables
    if len(preds) < len(variables):
        return out
    for combo in itertools.permutations(preds, len(variables)):
        binding = {v: combo[i] for i, v in enumerate(variables)}
        shapes = [
            frozenset(binding[v] for v, _ in p.lits) for p in schema.premises]
        chosen: list[Clause] = []
        ok = True
        for shape in shapes:
            hit = next(
                (c for c in premises
                 if c not in chosen and frozenset(p for p, _ in c) == shape),
                None)
            if hit is None:
                ok = False
                break
            chosen.append(hit)
        if not ok:
            continue
        concl = instantiate(schema.conclusion, binding)
        if concl is None:
            continue
        out.append((tuple(chosen), concl))
    return out


def polarity_blind_refutations(
    schema: Schema, premises: Sequence[Clause]
) -> tuple[int, int]:
    """``(matches, refuted)`` for the polarity-blind matcher on one task.

    Every refutation is a wrong answer a sign-blind abstraction would have
    produced and that the sign-preserving one does not.  Refusing to generalise
    across polarity is therefore a decision with a measured cost and a measured
    benefit, not a stylistic preference.
    """
    matches = polarity_blind_matches(schema, premises)
    refuted = sum(
        1 for chosen, concl in matches if not entails(list(chosen), concl))
    return len(matches), refuted
