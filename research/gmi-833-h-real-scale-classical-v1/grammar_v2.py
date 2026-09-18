"""Revival-pass grammar budget for gmi-833-h-real-scale-classical-v1.

FREEZE_V2_ADDENDUM.md lever L3. `grammar_v1.py` is imported unchanged: the
operations, the leaves, the probe grid, the evaluator, the classifier and the
cost model are all exactly those of V1. The only differences are

  * HEAD_MAX_NODES 4 -> 5, so that an expression containing all three of S,
    STATE and BIAS is reachable at all (three distinct leaves need 2n-1 = 5
    nodes); at 4 nodes no parameterised state update exists in the grammar;
  * a target-independent quotient that keeps only heads whose denotation depends
    on S, plus exactly one canonical representative of the S-independent class
    (`C0`), so a candidate that ignores the fold entirely is still reachable.

Neither change looks at any target, response, family name or outcome. Both are
applied identically at all four scopes.
"""
import hashlib

import grammar_v1 as G

HEAD_MAX_NODES = 5
S_INDEPENDENT_REPRESENTATIVE = ("L", "C0")


def build_candidates_v2():
    braw = G.enumerate_exprs(G.BODY_MAX_NODES, G.BODY_LEAVES)
    hraw = G.enumerate_exprs(HEAD_MAX_NODES, G.HEAD_LEAVES)
    bq, _, nbr, nbc = G.quotient(braw, G.body_probe_points())
    hq, _, nhr, nhc = G.quotient(hraw, G.head_probe_points())
    keep = [e for e in hq if G._depends_on(e, "S", None, ["BIAS", "STATE"])]
    keep.append(S_INDEPENDENT_REPRESENTATIVE)
    pairs = [(b, h) for b in bq for h in keep]
    meta = {"body_raw": nbr, "body_classes": nbc,
            "head_raw": nhr, "head_classes": nhc,
            "head_kept_s_dependent": len(keep) - 1,
            "head_kept_total": len(keep),
            "pairs": len(pairs),
            "head_max_nodes": HEAD_MAX_NODES,
            "grammar_digest": digest_v2()}
    return pairs, meta


def digest_v2():
    h = hashlib.sha256()
    h.update(G.grammar_digest().encode())
    h.update(("HEAD_MAX_NODES=%d" % HEAD_MAX_NODES).encode())
    h.update(b"FILTER=depends_on_S+one_canonical_S_independent_representative")
    return h.hexdigest()


def raw_sets():
    return (G.enumerate_exprs(G.BODY_MAX_NODES, G.BODY_LEAVES),
            G.enumerate_exprs(HEAD_MAX_NODES, G.HEAD_LEAVES))
