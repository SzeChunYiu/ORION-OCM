from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import permutations, product
import json
from typing import Dict, Iterable, Mapping, Sequence, Tuple, FrozenSet

CLAIM_CEILING = "GMI_G0_COST_LABEL_BLINDNESS_AND_STRUCTURAL_PRIVILEGE_BOUNDARY_AT_REGISTERED_SCOPE"
FREEZE_COMMIT = "abaf2c1dc252c5138bb43c5ba83bbde64d6c212f"
SOURCE_MAIN = "e91ab6c799d35453addadf4101fbc9f774472d37"
WEIGHTS: Tuple[Tuple[int,int], ...] = ((1,1),(2,1),(1,2),(4,1),(1,4))
FAMILY_LABELS = ("F0","F1","F2")
SEMANTICS = ("ALPHA","BETA","GAMMA")

@dataclass(frozen=True, order=True)
class Presentation:
    presentation_id: str
    semantic_class: str
    family_label: str
    L: int
    d: int
    def __post_init__(self) -> None:
        if not self.presentation_id:
            raise ValueError("empty presentation id")
        if self.semantic_class not in SEMANTICS:
            raise ValueError("unknown semantic class")
        if self.family_label not in FAMILY_LABELS:
            raise ValueError("unknown family label")
        if self.L <= 0 or self.d < 0:
            raise ValueError("invalid raw cost vector")
    @property
    def rho(self) -> Tuple[int,int]:
        return (self.L, self.d)

BASE: Tuple[Presentation, ...] = (
    Presentation("pA0","ALPHA","F0",1,4),
    Presentation("pA1","ALPHA","F0",3,2),
    Presentation("pB0","BETA","F1",4,1),
    Presentation("pB1","BETA","F1",2,3),
    Presentation("pG0","GAMMA","F2",3,3),
    Presentation("pG1","GAMMA","F2",5,0),
)
BASE_EDGES: FrozenSet[Tuple[str,str]] = frozenset({
    ("pA0","pA1"), ("pA1","pB1"), ("pB1","pB0"),
    ("pB0","pG0"), ("pG0","pG1"), ("pG1","pA0")
})

class AuditError(ValueError):
    pass

def cost(p: Presentation, w: Tuple[int,int]) -> Fraction:
    a,b = w
    if a <= 0 or b <= 0:
        raise AuditError("NONPOSITIVE_WEIGHT")
    return Fraction(a*p.L + b*p.d, 1)

def group_by_semantic(ps: Sequence[Presentation]) -> Dict[str, Tuple[Presentation,...]]:
    out: Dict[str,list[Presentation]] = {s: [] for s in SEMANTICS}
    for p in ps:
        out[p.semantic_class].append(p)
    return {s: tuple(sorted(v, key=lambda x:x.presentation_id)) for s,v in out.items() if v}

def class_minima(ps: Sequence[Presentation], w: Tuple[int,int]) -> Dict[str, Fraction]:
    return {s: min(cost(p,w) for p in group) for s,group in group_by_semantic(ps).items()}

def selection(ps: Sequence[Presentation], w: Tuple[int,int]) -> FrozenSet[str]:
    mins = class_minima(ps,w)
    m = min(mins.values())
    return frozenset(s for s,v in mins.items() if v == m)

def permute_labels(ps: Sequence[Presentation], perm: Mapping[str,str]) -> Tuple[Presentation,...]:
    if set(perm) != set(FAMILY_LABELS) or set(perm.values()) != set(FAMILY_LABELS):
        raise AuditError("INVALID_LABEL_PERMUTATION")
    return tuple(replace(p, family_label=perm[p.family_label]) for p in ps)

def label_blindness_certificate() -> dict:
    point_checks = class_checks = selection_checks = 0
    for images in permutations(FAMILY_LABELS):
        perm = dict(zip(FAMILY_LABELS, images))
        q = permute_labels(BASE, perm)
        by_id_q = {p.presentation_id:p for p in q}
        for w in WEIGHTS:
            for p in BASE:
                qp = by_id_q[p.presentation_id]
                point_checks += 1
                if qp.rho != p.rho or cost(qp,w) != cost(p,w):
                    raise AssertionError("label permutation changed point cost")
            class_checks += len(SEMANTICS)
            if class_minima(q,w) != class_minima(BASE,w):
                raise AssertionError("label permutation changed class minima")
            selection_checks += 1
            if selection(q,w) != selection(BASE,w):
                raise AssertionError("label permutation changed selection")
    return {
        "label_permutations": 6,
        "weights": len(WEIGHTS),
        "point_cost_checks": point_checks,
        "class_minimum_checks": class_checks,
        "selection_checks": selection_checks,
        "failures": 0,
    }

def remint_names(ps: Sequence[Presentation], edges: FrozenSet[Tuple[str,str]], mapping: Mapping[str,str]):
    ids = {p.presentation_id for p in ps}
    if set(mapping) != ids or len(set(mapping.values())) != len(ids):
        raise AuditError("NON_BIJECTIVE_REMINT")
    q = tuple(replace(p, presentation_id=mapping[p.presentation_id]) for p in ps)
    qe = frozenset((mapping[a],mapping[b]) for a,b in edges)
    return q, qe

def audit_isometric_remint(
    source: Sequence[Presentation], source_edges: FrozenSet[Tuple[str,str]],
    target: Sequence[Presentation], target_edges: FrozenSet[Tuple[str,str]],
    mapping: Mapping[str,str],
) -> str:
    ids = {p.presentation_id for p in source}
    if set(mapping) != ids or len(set(mapping.values())) != len(ids):
        return "NON_BIJECTIVE_REMINT"
    t = {p.presentation_id:p for p in target}
    if set(t) != set(mapping.values()):
        return "NON_BIJECTIVE_REMINT"
    for p in source:
        q = t[mapping[p.presentation_id]]
        if q.semantic_class != p.semantic_class or q.rho != p.rho:
            return "NON_ISOMETRIC_REMINT"
    expected_edges = frozenset((mapping[a],mapping[b]) for a,b in source_edges)
    if expected_edges != target_edges:
        return "NON_ISOMETRIC_REMINT"
    return "ISOMETRIC_REMINT"

def isometry_certificate() -> dict:
    ids = tuple(p.presentation_id for p in BASE)
    checks = 0
    for image_ids in permutations(tuple("uvwxyz")):
        mapping = dict(zip(ids, image_ids))
        q, qe = remint_names(BASE, BASE_EDGES, mapping)
        if audit_isometric_remint(BASE, BASE_EDGES, q, qe, mapping) != "ISOMETRIC_REMINT":
            raise AssertionError("valid isometry rejected")
        for w in WEIGHTS:
            if class_minima(q,w) != class_minima(BASE,w):
                raise AssertionError("isometry changed class minima")
            if selection(q,w) != selection(BASE,w):
                raise AssertionError("isometry changed selection")
        checks += 1
    return {"name_isometries": checks, "weights": len(WEIGHTS), "failures":0}

def structural_bias_counterexample() -> dict:
    ga = (
        Presentation("ga_a","ALPHA","F0",1,1),
        Presentation("ga_b","BETA","F1",3,2),
    )
    gb = (
        Presentation("gb_a","ALPHA","F0",3,2),
        Presentation("gb_b","BETA","F1",1,1),
    )
    w=(1,1)
    sa=selection(ga,w); sb=selection(gb,w)
    if sa != frozenset({"ALPHA"}) or sb != frozenset({"BETA"}):
        raise AssertionError("frozen structural reversal failed")
    return {
        "semantic_coverage_equal": sorted({p.semantic_class for p in ga}) == sorted({p.semantic_class for p in gb}),
        "weight": list(w),
        "GA_selection": sorted(sa),
        "GB_selection": sorted(sb),
        "terminal": "NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE",
    }

def audit_family_adjustment(adjustments: Mapping[str, Fraction]) -> str:
    if set(adjustments) != set(FAMILY_LABELS):
        return "CANNOT_AUDIT_FAMILY_ADJUSTMENT"
    vals = set(adjustments.values())
    return "FAMILY_LABEL_COST_LEAK" if len(vals) > 1 else "NO_LABEL_ADJUSTMENT_LEAK"

def audit_macro(p: Presentation, raw_override: Tuple[int,int] | None = None) -> str:
    raw = p.rho if raw_override is None else raw_override
    if raw == (0,0):
        return "ZERO_COST_FAMILY_MACRO"
    if raw[0] <= 0 or raw[1] < 0:
        return "INVALID_RAW_COST"
    return "MACRO_COST_REGISTERED"

def selection_with_tie_policy(ps: Sequence[Presentation], w: Tuple[int,int], tie_break: str | None=None):
    s = selection(ps,w)
    if len(s)>1 and tie_break in {"family_label","presentation_id"}:
        return "LABEL_DEPENDENT_TIE_BREAK"
    return sorted(s)

def dominates(x: Tuple[int,int], y: Tuple[int,int]) -> bool:
    return x[0] <= y[0] and x[1] <= y[1] and x != y

def vector_cost(x: Tuple[int,int], w: Tuple[int,int]) -> int:
    return x[0]*w[0] + x[1]*w[1]

def dominance_certificate() -> dict:
    vectors=tuple(product(range(5), repeat=2))
    ordered_pairs=dominance_pairs=dominance_weight_checks=violations=0
    for x in vectors:
        for y in vectors:
            if x==y: continue
            ordered_pairs += 1
            if dominates(x,y):
                dominance_pairs += 1
                for w in WEIGHTS:
                    dominance_weight_checks += 1
                    if not vector_cost(x,w) < vector_cost(y,w):
                        violations += 1
    x=(1,4); y=(4,1)
    reversal = vector_cost(x,(4,1)) < vector_cost(y,(4,1)) and vector_cost(x,(1,4)) > vector_cost(y,(1,4))
    if violations or not reversal:
        raise AssertionError("dominance/reversal certificate failed")
    return {
        "vectors":len(vectors), "ordered_distinct_pairs":ordered_pairs,
        "strict_dominance_pairs":dominance_pairs,
        "dominance_weight_checks":dominance_weight_checks,
        "dominance_violations":violations,
        "incomparable_reversal":reversal,
        "reversal_vectors":[list(x),list(y)],
    }

def hostile_certificate() -> dict:
    family_adjust = audit_family_adjustment({"F0":Fraction(-1),"F1":Fraction(0),"F2":Fraction(0)})
    zero_macro = audit_macro(BASE[0], (0,0))
    tie_fixture=(Presentation("t0","ALPHA","F0",1,1), Presentation("t1","BETA","F1",1,1))
    tie = selection_with_tie_policy(tie_fixture,(1,1),"family_label")
    ids={p.presentation_id for p in BASE}; mapping=dict(zip(sorted(ids), tuple("uvwxyz")))
    q,qe=remint_names(BASE,BASE_EDGES,mapping)
    q_bad=list(q); q_bad[0]=replace(q_bad[0], L=q_bad[0].L+1)
    noniso_raw=audit_isometric_remint(BASE,BASE_EDGES,tuple(q_bad),qe,mapping)
    qe_bad=frozenset(e for i,e in enumerate(sorted(qe)) if i != 0)
    noniso_edge=audit_isometric_remint(BASE,BASE_EDGES,q,qe_bad,mapping)
    expected={
        "family_adjustment": "FAMILY_LABEL_COST_LEAK",
        "zero_cost_macro": "ZERO_COST_FAMILY_MACRO",
        "lexical_tie_break": "LABEL_DEPENDENT_TIE_BREAK",
        "raw_mutation_remint": "NON_ISOMETRIC_REMINT",
        "edge_mutation_remint": "NON_ISOMETRIC_REMINT",
    }
    got={"family_adjustment":family_adjust,"zero_cost_macro":zero_macro,"lexical_tie_break":tie,"raw_mutation_remint":noniso_raw,"edge_mutation_remint":noniso_edge}
    if got != expected:
        raise AssertionError((got,expected))
    return got

def build_receipt() -> dict:
    return {
        "schema":"GMI833G0CostPrivilegeReceiptV1",
        "parent_issue":833,
        "issue":891,
        "source_main":SOURCE_MAIN,
        "freeze_commit":FREEZE_COMMIT,
        "claim_ceiling":CLAIM_CEILING,
        "weights":[list(x) for x in WEIGHTS],
        "label_blindness":label_blindness_certificate(),
        "isometric_remints":isometry_certificate(),
        "structural_bias_boundary":structural_bias_counterexample(),
        "dominance":dominance_certificate(),
        "hostiles":hostile_certificate(),
        "narrow_terminal":"LABEL_BLIND_AND_ISOMETRICALLY_INVARIANT_AT_REGISTERED_SCOPE",
        "row_terminal":"NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE",
        "terminal":"GMI_833_E7_COST_PRIVILEGE_AUDIT_GREEN_AT_REGISTERED_SCOPE",
        "forbidden_promotions":[
            "G0_UNBIASED","NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY",
            "REPRESENTATION_INVARIANT_COST_UNIVERSALLY","SEARCH_NEUTRALITY_PROVED",
            "ARCHITECTURE_PRIOR_FREE_GRAMMAR","ALL_SCALARIZATIONS_AGREE","COMPLETE_GMI"
        ]
    }

def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"

if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
