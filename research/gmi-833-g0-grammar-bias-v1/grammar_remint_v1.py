@dataclass(frozen=True)
class FiniteGrammar:
    nodes: Tuple[str, ...]
    semantic: Mapping[str, str]
    length: Mapping[str, int]
    edges: FrozenSet[Tuple[str, str]]
    starts: FrozenSet[str]


def validate_finite_grammar(grammar: FiniteGrammar) -> Tuple[str, ...]:
    errors = []
    nodes = set(grammar.nodes)
    if not nodes:
        errors.append("EMPTY_NODES")
    if len(nodes) != len(grammar.nodes):
        errors.append("DUPLICATE_NODES")
    if set(grammar.semantic) != nodes:
        errors.append("SEMANTIC_DOMAIN_MISMATCH")
    if set(grammar.length) != nodes:
        errors.append("LENGTH_DOMAIN_MISMATCH")
    if any(type(v) is not int or v < 0 for v in grammar.length.values()):
        errors.append("INVALID_LENGTH")
    if not grammar.starts or not set(grammar.starts) <= nodes:
        errors.append("INVALID_START_SET")
    for u, v in grammar.edges:
        if u not in nodes or v not in nodes:
            errors.append("EDGE_OUTSIDE_NODES")
            break
    return tuple(errors)


def generic_distances(grammar: FiniteGrammar) -> Dict[str, int]:
    errors = validate_finite_grammar(grammar)
    if errors:
        raise ValueError(";".join(errors))
    adj = {n: set() for n in grammar.nodes}
    for u, v in grammar.edges:
        adj[u].add(v)
    return bfs_distances({k: frozenset(v) for k, v in adj.items()}, grammar.starts)


def grammar_bias_rows(grammar: FiniteGrammar) -> Dict[str, Dict[str, object]]:
    errors = validate_finite_grammar(grammar)
    if errors:
        raise ValueError(";".join(errors))
    dist = generic_distances(grammar)
    by_sem: Dict[str, list[str]] = defaultdict(list)
    for n in grammar.nodes:
        by_sem[grammar.semantic[n]].append(n)
    total_by_budget = {
        b: sum(grammar.length[n] <= b for n in grammar.nodes) for b in sorted(set(grammar.length.values()))
    }
    rows = {}
    for sem, nodes in sorted(by_sem.items()):
        finite_d = [dist[n] for n in nodes if n in dist]
        max_len = max(grammar.length.values())
        rows[sem] = {
            "L": min(grammar.length[n] for n in nodes),
            "d": min(finite_d) if finite_d else "INF",
            "N": {str(b): sum(grammar.length[n] <= b for n in nodes) for b in sorted(total_by_budget)},
            "Q": {
                str(b): _fraction_text(Fraction(sum(grammar.length[n] <= b for n in nodes), total_by_budget[b]))
                for b in sorted(total_by_budget)
                if total_by_budget[b]
            },
            "A": {
                str(k): sum(n in dist and dist[n] <= k for n in nodes)
                for k in range(0, max(dist.values(), default=0) + 1)
            },
            "max_length": max_len,
        }
    return rows


def certify_isometric_remint(source: FiniteGrammar, target: FiniteGrammar, phi: Mapping[str, str]) -> Tuple[bool, str]:
    src_errors = validate_finite_grammar(source)
    tgt_errors = validate_finite_grammar(target)
    if src_errors:
        return False, "INVALID_SOURCE:" + ";".join(src_errors)
    if tgt_errors:
        return False, "INVALID_TARGET:" + ";".join(tgt_errors)
    if set(phi) != set(source.nodes) or set(phi.values()) != set(target.nodes) or len(set(phi.values())) != len(phi):
        return False, "NON_BIJECTIVE_NODE_MAP"
    for p in source.nodes:
        q = phi[p]
        if target.semantic[q] != source.semantic[p]:
            return False, "SEMANTIC_MAP_CORRUPTION"
        if target.length[q] != source.length[p]:
            return False, "DESCRIPTION_LENGTH_CORRUPTION"
    transported_edges = frozenset((phi[u], phi[v]) for u, v in source.edges)
    if transported_edges != target.edges:
        return False, "EDGE_CORRUPTION"
    transported_starts = frozenset(phi[x] for x in source.starts)
    if transported_starts != target.starts:
        return False, "START_SET_CORRUPTION"
    return True, "ISOMETRIC_SEMANTIC_REMINT"


def remint_grammar(source: FiniteGrammar, phi: Mapping[str, str]) -> FiniteGrammar:
    if set(phi) != set(source.nodes) or len(set(phi.values())) != len(phi):
        raise ValueError("phi must be a bijection on source nodes")
    nodes = tuple(phi[n] for n in source.nodes)
    return FiniteGrammar(
        nodes=nodes,
        semantic={phi[n]: source.semantic[n] for n in source.nodes},
        length={phi[n]: source.length[n] for n in source.nodes},
        edges=frozenset((phi[u], phi[v]) for u, v in source.edges),
        starts=frozenset(phi[n] for n in source.starts),
    )


def selection(grammar: FiniteGrammar, candidates: Iterable[str]) -> str:
    rows = grammar_bias_rows(grammar)
    candidates = tuple(candidates)
    if not candidates:
        raise ValueError("candidate set empty")
    for c in candidates:
        if c not in rows:
            raise ValueError("candidate semantic class absent")
    def key(c: str):
        d = rows[c]["d"]
        d_key = math.inf if d == "INF" else int(d)
        return (int(rows[c]["L"]), d_key, c)
    return min(candidates, key=key)


def remint_fixture() -> FiniteGrammar:
    nodes = ("root", "a_short", "a_long", "b")
    undirected = (("root", "a_short"), ("a_short", "a_long"), ("root", "b"))
    edges = frozenset([e for u, v in undirected for e in ((u, v), (v, u))])
    return FiniteGrammar(
        nodes=nodes,
        semantic={"root": "ROOT", "a_short": "A", "a_long": "A", "b": "B"},
        length={"root": 0, "a_short": 1, "a_long": 2, "b": 1},
        edges=edges,
        starts=frozenset({"root"}),
    )


def remint_exhaustive_certificate() -> Dict[str, object]:
    source = remint_fixture()
    src_rows = grammar_bias_rows(source)
    src_sel = selection(source, ("A", "B"))
    names = ("w", "x", "y", "z")
    certified = invariant_failures = certification_failures = 0
    for perm in permutations(names):
        phi = dict(zip(source.nodes, perm))
        target = remint_grammar(source, phi)
        ok, reason = certify_isometric_remint(source, target, phi)
        if not ok:
            certification_failures += 1
            continue
        certified += 1
        if grammar_bias_rows(target) != src_rows or selection(target, ("A", "B")) != src_sel:
            invariant_failures += 1
    return {
        "permutations": 24,
        "certified": certified,
        "certification_failures": certification_failures,
        "invariant_failures": invariant_failures,
        "selection": src_sel,
    }


def nonisometric_hostile_pair() -> Tuple[FiniteGrammar, FiniteGrammar]:
    def bidi(path: Sequence[Tuple[str, str]]) -> FrozenSet[Tuple[str, str]]:
        return frozenset(e for u, v in path for e in ((u, v), (v, u)))
    ga = FiniteGrammar(
        nodes=("root", "a", "b"),
        semantic={"root": "ROOT", "a": "A", "b": "B"},
        length={"root": 0, "a": 1, "b": 2},
        edges=bidi((('root', 'a'), ('a', 'b'))),
        starts=frozenset({"root"}),
    )
    gb = FiniteGrammar(
        nodes=("root2", "a2", "b2"),
        semantic={"root2": "ROOT", "a2": "A", "b2": "B"},
        length={"root2": 0, "a2": 2, "b2": 1},
        edges=bidi((('root2', 'b2'), ('b2', 'a2'))),
        starts=frozenset({"root2"}),
    )
    return ga, gb


def hostile_remint_results() -> Dict[str, str]:
    source = remint_fixture()
    base_phi = {"root": "w", "a_short": "x", "a_long": "y", "b": "z"}
    target = remint_grammar(source, base_phi)
    out: Dict[str, str] = {}

    bad = dict(base_phi); bad["b"] = "y"
    out["non_bijective"] = certify_isometric_remint(source, target, bad)[1]

    sem = dict(target.semantic); sem["x"] = "B"
    t_sem = FiniteGrammar(target.nodes, sem, target.length, target.edges, target.starts)
    out["semantic"] = certify_isometric_remint(source, t_sem, base_phi)[1]

    lengths = dict(target.length); lengths["x"] += 1
    t_len = FiniteGrammar(target.nodes, target.semantic, lengths, target.edges, target.starts)
    out["length"] = certify_isometric_remint(source, t_len, base_phi)[1]

    edges = set(target.edges); edges.remove(("w", "x"))
    t_edge = FiniteGrammar(target.nodes, target.semantic, target.length, frozenset(edges), target.starts)
    out["edge"] = certify_isometric_remint(source, t_edge, base_phi)[1]

    t_start = FiniteGrammar(target.nodes, target.semantic, target.length, target.edges, frozenset({"x"}))
    out["start"] = certify_isometric_remint(source, t_start, base_phi)[1]

    ga, gb = nonisometric_hostile_pair()
    semantic_only_phi = {"root": "root2", "a": "a2", "b": "b2"}
    out["semantic_only"] = certify_isometric_remint(ga, gb, semantic_only_phi)[1]
    return out
