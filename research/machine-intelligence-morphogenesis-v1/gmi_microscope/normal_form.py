"""CP2 / RV-377-115 -- the representation and normal-form question, made executable.

The critical path asks for a representation/normal-form theorem "so known-form results
become domain-wide results".  That lift is only valid if the normal form CHARACTERISES the
semantic class: proving something of a representative transfers to the class exactly when
two genotypes share a normal form IF AND ONLY IF they are observationally equivalent.

`morph.canonical` already gives an isomorphism-invariant serialization, so structural
identity modulo node renaming is solved.  Two things are not:

  SOUNDNESS     a semantic reduction that provably does not change the developmental
                response.  Here: `prune`, backward reachability from OUTPUT.
  COMPLETENESS  whether equal normal form and equal observable behaviour are the SAME
                relation.  If they are not, the lift CP2 asks for does not follow.

Observational equivalence is taken at the finest resolution the corpus supports: the
`response_signature` (served trace and capability) over every registered ecology under
every registered intervention.
"""
from __future__ import annotations

import json

from . import bases, ecology, morph

COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
BOUNDARY = ("INPUT", "OUTPUT", "TARGET")


def prune(g):
    """drop every node that cannot reach OUTPUT. The served answer cannot depend on them."""
    ins = {}
    for a, b, pt in g["edges"]:
        ins.setdefault(b, []).append(a)
    outs = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"]
    keep, stack = set(), list(outs)
    while stack:
        i = stack.pop()
        if i in keep or i not in g["nodes"]:
            continue
        keep.add(i)
        stack.extend(ins.get(i, []))
    # the boundary is structural: an ecology is not well-formed without it
    for i, (k, _) in g["nodes"].items():
        if k in BOUNDARY:
            keep.add(i)
    nodes = {i: v for i, v in g["nodes"].items() if i in keep}
    edges = [(a, b, pt) for a, b, pt in g["edges"] if a in keep and b in keep]
    return morph.make(nodes, edges, meta=dict(g.get("meta") or {}))


def normal_form(g):
    return morph.canonical(prune(g))


def observable(g, ecos=None, interventions=None):
    """the exact developmental response over every registered ecology x intervention."""
    ecos = sorted(ecology.REGISTRY) if ecos is None else ecos
    ivs = sorted(ecology.INTERVENTIONS) if interventions is None else interventions
    sig = {}
    for e in ecos:
        spec = ecology.REGISTRY[e]
        for iv in ivs:
            try:
                r = ecology.run_genotype(spec, g, bases.ALL[COL], iv)
                sig[f"{e}|{iv}"] = ecology.response_signature(r)
            except Exception as ex:
                sig[f"{e}|{iv}"] = f"ERR:{type(ex).__name__}"
    return json.dumps(sig, sort_keys=True)
