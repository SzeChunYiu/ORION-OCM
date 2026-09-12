"""R0 — typed morphology intermediate representation (IR) and canonical serializer
(GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 section 20, R0; GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1 section 8 primitive set;
GMI_BIOSPHERE_SCALING_AND_TRIAGE_V1 section 4 canonical fingerprint; hardening H1 type check, H5 remint invariance).

A genotype is a typed dataflow graph over the NEUTRAL primitive alphabet: every node has a kind from KINDS (state, routing,
computation, update, verification, morphogenesis, compile, decision classes), small integer parameters, typed input ports
and one typed output. No architecture macro (TRANSFORMER, RAG, MOE, CNN, LSTM, VRQM, VGSC, ...) is a kind: those names are
forbidden as kinds and as metadata labels (FORBIDDEN_MACROS), so a search over this IR cannot name its way to a form.

Canonical form: node identifiers, insertion order and surface labels are nuisance (remint set of the no-free-lunch gates,
section 7). canonical() computes an isomorphism-invariant serialization by Weisfeiler-Lehman colour refinement followed by
exact tie-breaking (brute force over the permutations of each remaining colour class; genotypes are small), so that two
genotypes have equal fingerprints iff they are isomorphic as typed parameterized port graphs. remint() applies the nuisance
transformations; test_morph checks canonical(remint(g)) == canonical(g) and that non-isomorphic edits change the fingerprint.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random

# ---------------------------------------------------------------------------------------------------------------------
# neutral primitive alphabet: kind -> (class letter, input port types, output type, parameter names)
# type letters (calculus/biosphere docs): S state, R routing, T local transform, U update, V verification, G morphogenesis,
# H history/memory, C compiler/interface, D decision, P physical placement
VEC, SCA, KEY, TAB, PROG, SET, FLAG = "vec", "sca", "key", "tab", "prog", "set", "flag"
KINDS = {
    # interface
    "INPUT": ("C", (), VEC, ("width",)),
    "TARGET": ("C", (), SCA, ()),                       # the feedback signal (label) available to update nodes
    "OUTPUT": ("D", (SCA,), SCA, ()),
    "CONST": ("S", (), SCA, ("value",)),
    # state primitives
    "DENSE": ("S", (), VEC, ("width",)),                # dense continuous parameter vector (cells)
    "TABLE": ("S", (), TAB, ("keybits",)),              # finite symbol table keyed by bits of the input
    "KVSTORE": ("S", (), TAB, ("cap",)),                # key-value exemplar store
    "PROGRAM": ("S", (), PROG, ("grammar",)),           # a program/term drawn from a declared grammar
    "VERSIONED": ("H", (TAB,), TAB, ("depth",)),        # persistent / versioned wrapper over a table (lineage)
    # routing
    "EDGE": ("R", (VEC,), VEC, ()),                     # fixed edge (identity routing)
    "LOOKUP": ("R", (TAB, VEC), SCA, ()),               # key lookup: table[key(x)]
    "NEAREST": ("R", (TAB, VEC), SCA, ("k", "metric")), # nearest-neighbour retrieval (Hamming metric 0, L1 metric 1)
    "SCORESELECT": ("R", (TAB, VEC), SCA, ("temp",)),   # dynamic score-and-select (soft retrieval / attention-like)
    "SELECT": ("R", (SCA, SCA, FLAG), SCA, ()),         # conditional routing: flag ? a : b
    # local computation
    "LINEAR": ("T", (VEC, VEC), SCA, ()),               # dot product of input with a DENSE parameter vector
    "AFFINE": ("T", (VEC, VEC), VEC, ("width",)),       # width x width map + bias from a DENSE parameter block
    "NONLIN": ("T", (VEC,), VEC, ("fn",)),              # elementwise nonlinear map (0 THRESH, 1 NEG, 2 identity)
    "NONLIN1": ("T", (SCA,), SCA, ("fn",)),
    "GATE": ("T", (VEC, VEC), VEC, ()),                 # gated product
    "SUM": ("T", (SCA, SCA), SCA, ()),
    "PROGEXEC": ("T", (PROG, VEC), SCA, ()),            # execute the program on the input
    "SEARCH": ("U", (PROG, SET), PROG, ("budget",)),    # search expansion over the grammar (black-box optimization of the program state against the evidence set)
    # update laws
    "GRAD": ("U", (VEC, SCA, SCA), VEC, ("lr",)),       # reverse-mode update of a DENSE parameter from (prediction, target)
    "CLOSEDFORM": ("U", (TAB, VEC, SCA), TAB, ()),      # least-squares / exact solve into a table
    "INSERT": ("U", (TAB, VEC, SCA), TAB, ()),          # memory insertion
    "PMUTATE": ("U", (PROG, SET), PROG, ("pop",)),      # population / mutation update of programs
    "NOUPDATE": ("U", (), FLAG, ()),
    # verification
    "VERIFY": ("V", (PROG, SET), FLAG, ()),             # predicate check of a candidate against the evidence set
    "VERIFYTAB": ("V", (TAB, SET), FLAG, ()),
    "ABSTAIN": ("V", (SCA, FLAG), SCA, ()),             # serve value only if flag, else abstain
    "ROLLBACK": ("V", (TAB, TAB, FLAG), TAB, ()),       # keep new table if flag else old
    # history
    "EVIDENCE": ("H", (VEC, SCA), SET, ("cap",)),       # evidence buffer of (input, target) pairs
    # compile / materialize
    "MATERIALIZE": ("C", (PROG,), TAB, ("keybits",)),   # compile a program into a lookup table
    "SHADOW": ("C", (TAB,), TAB, ()),                   # shadow copy (for verify-before-swap)
    # morphogenesis (used by the mutation grammar as reified operators; never evaluated at serve time)
    "MORPH_RULE": ("G", (), FLAG, ("rule",)),
    # physical placement
    "PLACE": ("P", (), FLAG, ("precision", "device")),
}
FORBIDDEN_MACROS = {"TRANSFORMER", "RAG", "MIXTURE_OF_EXPERTS", "MOE", "VRQM", "VGSC", "RQM", "IQL", "LMHM", "SCDI", "CNN", "LSTM", "GRU", "NEURON", "BACKPROP", "ATTENTION", "KNN", "GRADIENT_NET", "BAYES", "PARTICLE_FILTER"}
CLASS_OF = {k: v[0] for k, v in KINDS.items()}


class MorphError(ValueError):
    pass


def make(nodes, edges, meta=None):
    """nodes: {id: (kind, {param: int})}; edges: [(src_id, dst_id, port_index)]; meta: free labels (nuisance)."""
    return {"nodes": {str(i): (k, dict(p)) for i, (k, p) in nodes.items()}, "edges": [(str(a), str(b), int(pt)) for a, b, pt in edges], "meta": dict(meta or {})}


def typecheck(g):
    """H1: kinds exist and are not macros; ports typed; each input port bound at most once; parameters declared; acyclic."""
    nodes, edges = g["nodes"], g["edges"]
    for i, (k, p) in nodes.items():
        if k.upper() in FORBIDDEN_MACROS or k not in KINDS: raise MorphError(f"node {i}: kind {k!r} is not a neutral primitive")
        cls, ins, out, params = KINDS[k]
        if set(p) != set(params): raise MorphError(f"node {i}: parameters {sorted(p)} != declared {list(params)}")
        if any(not isinstance(v, int) for v in p.values()): raise MorphError(f"node {i}: non-integer parameter")
    # meta labels are nuisance (ignored by the canonical form and by every archive descriptor); only kinds are constrained
    bound = {}
    for a, b, pt in edges:
        if a not in nodes or b not in nodes: raise MorphError(f"edge {a}->{b}: unknown node")
        ka, kb = nodes[a][0], nodes[b][0]; ins = KINDS[kb][1]
        if pt >= len(ins): raise MorphError(f"edge {a}->{b}: port {pt} out of range for {kb}")
        if KINDS[ka][2] != ins[pt]: raise MorphError(f"edge {a}->{b}: type {KINDS[ka][2]} into port {pt} of {kb} expecting {ins[pt]}")
        if (b, pt) in bound: raise MorphError(f"node {b} port {pt} bound twice")
        bound[(b, pt)] = a
    # acyclicity over the dataflow edges (feedback through update nodes is expressed by the U nodes' outputs, not cycles)
    order = toposort(g)
    if len(order) != len(nodes): raise MorphError("cycle in dataflow graph")
    return True


def toposort(g):
    nodes = g["nodes"]; preds = {i: [] for i in nodes}
    for a, b, _ in g["edges"]: preds[b].append(a)
    seen = set(); order = []
    def visit(i, stack):
        if i in seen: return
        if i in stack: raise MorphError("cycle")
        for a in preds[i]: visit(a, stack | {i})
        seen.add(i); order.append(i)
    for i in sorted(nodes): visit(i, frozenset())
    return order


def mechanism_vector(g):
    """counts of kinds per class letter — the mechanism descriptor used by the archive (label-free)."""
    v = {c: 0 for c in "SRTUVGHCDP"}
    for k, _ in g["nodes"].values(): v[CLASS_OF[k]] += 1
    return v


# --------------------------------------------------------------------------------------------------------- canonical form
def _wl_classes(g):
    """Weisfeiler-Lehman colour refinement of the typed port graph; returns the colour classes in canonical colour order.
    Factored out of canonical()/canonical_labels() (identical code, identical result) so that the size of the exact
    tie-breaking search can be measured before it is run (see canonical_search_width)."""
    nodes = g["nodes"]; ids = sorted(nodes)
    ins = {i: {} for i in ids}; outs = {i: [] for i in ids}
    for a, b, pt in g["edges"]: ins[b][pt] = a; outs[a].append((b, pt))
    colour = {i: json.dumps([nodes[i][0], sorted(nodes[i][1].items())]) for i in ids}
    for _ in range(len(ids) + 1):
        sig = {i: json.dumps([colour[i], sorted((pt, colour[a]) for pt, a in ins[i].items()), sorted((pt, colour[b]) for b, pt in outs[i])]) for i in ids}
        ranks = {s: r for r, s in enumerate(sorted(set(sig.values())))}
        new = {i: str(ranks[sig[i]]) for i in ids}
        if len(set(new.values())) == len(set(colour.values())): colour = new; break
        colour = new
    classes = {}
    for i in ids: classes.setdefault(colour[i], []).append(i)
    return [classes[c] for c in sorted(classes, key=lambda c: int(c))]


def canonical_search_width(g):
    """the number of labellings canonical() must serialize: the product of the factorials of the WL class sizes. The
    exact tie-break is a brute force, so a genotype with many interchangeable nodes is expensive to canonicalize; a
    search that generates genotypes may use this to refuse a proposal before paying for it (R7/R11 do)."""
    w = 1
    for cl in _wl_classes(g):
        for k in range(2, len(cl) + 1): w *= k
        if w > 10 ** 12: return w
    return w


def canonical(g):
    """isomorphism-invariant serialization of the typed port graph (ids, order and meta are nuisance)."""
    nodes = g["nodes"]; ids = sorted(nodes)
    ordered_classes = _wl_classes(g)
    def serialize(perm_map):
        lab = perm_map
        nl = sorted((lab[i], nodes[i][0], sorted(nodes[i][1].items())) for i in ids)
        el = sorted((lab[a], lab[b], pt) for a, b, pt in g["edges"])
        return json.dumps({"nodes": nl, "edges": el}, sort_keys=True)
    # exact tie-break: minimize the serialization over the product of permutations within each colour class
    best = None
    base = 0; offsets = []
    for cl in ordered_classes: offsets.append(base); base += len(cl)
    for perms in itertools.product(*[itertools.permutations(range(len(cl))) for cl in ordered_classes]):
        lab = {}
        for cl, off, pm in zip(ordered_classes, offsets, perms):
            for pos, i in enumerate(cl): lab[i] = off + pm[pos]
        s = serialize(lab)
        if best is None or s < best: best = s
    return best


def fingerprint(g):
    return hashlib.sha256(canonical(g).encode()).hexdigest()


def canonical_labels(g):
    """{node id: canonical index} — the labelling that realizes canonical(g); id-invariant, so per-node deterministic
    choices (parameter initialization) made from these indices are remint-invariant (H5)."""
    best = canonical(g); nodes = g["nodes"]; ids = sorted(nodes)
    # recover a labelling by re-running the search and keeping the permutation that produced `best`
    ins = {i: {} for i in ids}; outs = {i: [] for i in ids}
    for a, b, pt in g["edges"]: ins[b][pt] = a; outs[a].append((b, pt))
    colour = {i: json.dumps([nodes[i][0], sorted(nodes[i][1].items())]) for i in ids}
    for _ in range(len(ids) + 1):
        sig = {i: json.dumps([colour[i], sorted((pt, colour[a]) for pt, a in ins[i].items()), sorted((pt, colour[b]) for b, pt in outs[i])]) for i in ids}
        ranks = {s: r for r, s in enumerate(sorted(set(sig.values())))}; new = {i: str(ranks[sig[i]]) for i in ids}
        if len(set(new.values())) == len(set(colour.values())): colour = new; break
        colour = new
    classes = {}
    for i in ids: classes.setdefault(colour[i], []).append(i)
    ordered = [classes[c] for c in sorted(classes, key=lambda c: int(c))]; offsets = []; base = 0
    for cl in ordered: offsets.append(base); base += len(cl)
    for perms in itertools.product(*[itertools.permutations(range(len(cl))) for cl in ordered]):
        lab = {}
        for cl, off, pm in zip(ordered, offsets, perms):
            for pos, i in enumerate(cl): lab[i] = off + pm[pos]
        nl = sorted((lab[i], nodes[i][0], sorted(nodes[i][1].items())) for i in ids); el = sorted((lab[a], lab[b], pt) for a, b, pt in g["edges"])
        if json.dumps({"nodes": nl, "edges": el}, sort_keys=True) == best: return lab
    raise MorphError("canonical labelling not found")


def remint(g, seed=0):
    """nuisance transformation: rename node ids, shuffle node and edge order, rewrite meta labels."""
    rng = random.Random(seed); ids = list(g["nodes"]); rng.shuffle(ids)
    new_id = {i: f"n{rng.randrange(10**6)}_{k}" for k, i in enumerate(ids)}
    nodes = {new_id[i]: (g["nodes"][i][0], dict(g["nodes"][i][1])) for i in ids}
    edges = [(new_id[a], new_id[b], pt) for a, b, pt in g["edges"]]; rng.shuffle(edges)
    meta = {f"label{rng.randrange(10**6)}": f"surface{rng.randrange(10**6)}" for _ in g["meta"]}
    return {"nodes": nodes, "edges": edges, "meta": meta}


def to_json(g):
    return json.dumps({"nodes": {i: [k, p] for i, (k, p) in g["nodes"].items()}, "edges": g["edges"], "meta": g["meta"]}, sort_keys=True)


def from_json(s):
    d = json.loads(s); return {"nodes": {i: (k, p) for i, (k, p) in d["nodes"].items()}, "edges": [tuple(e) for e in d["edges"]], "meta": d["meta"]}
