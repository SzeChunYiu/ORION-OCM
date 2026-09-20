"""Actual BFS records and explicitly richer finite edge-history profile contexts."""
from core_v24 import need, index, nat, old_af, code_context
from af_model_v24 import POLICIES, graph_checked, legacy_inputs


def edge_histories(graph, start, horizon):
    graph_checked(graph)
    index(start, 4)
    nat(horizon)
    level = [(start, ())]
    result = list(level)
    for _ in range(horizon):
        following = []
        for terminal, path in level:
            for slot, edge in enumerate(graph.rows[terminal]):
                if edge is not None:
                    following.append((edge[1], path + ((terminal, slot),)))
        result.extend(following)
        level = following
    return tuple(sorted(result, key=lambda item: (len(item[1]), item[1], item[0])))


def profile_for(graph, start, target, path):
    graph_checked(graph)
    index(start, 4)
    index(target, 4)
    need(type(path) is tuple, "canonical edge history required")
    terminal = start
    actions = []
    provenance = {"INITIAL_OR_INHERITED_ORGANIZATION"}
    tags = dict(graph.provenance)
    for edge_id in path:
        need(type(edge_id) is tuple and len(edge_id) == 2, "source/slot pair required")
        source, slot = edge_id
        index(source, 4)
        index(slot, len(graph.rows[source]))
        need(source == terminal, "disconnected history")
        edge = graph.rows[source][slot]
        need(edge is not None, "history uses absent slot")
        action, terminal = edge
        actions.append(action)
        provenance.update(tags[action])
    return {
        "machine": POLICIES[terminal],
        "capability": {POLICIES[target] + "_TASK": old_af.score_string(POLICIES[terminal], POLICIES[target])},
        "resources": {"development_steps": len(path),
                      "external_observations": int("EXTERNAL_OBSERVATION" in provenance),
                      "oracle_queries": int("ORACLE_ADVICE_OR_TOOL" in provenance)},
        "provenance": sorted(provenance), "history": actions,
    }


def selected_profiles(graph, start, target):
    graph_checked(graph)
    index(start, 4)
    index(target, 4)
    transitions, provenance = legacy_inputs(graph)
    return tuple(old_af.gamma_profiles(POLICIES[start], transitions, provenance, POLICIES[target]))


def full_profiles(graph, start, target, horizon):
    graph_checked(graph)
    index(start, 4)
    index(target, 4)
    nat(horizon)
    return tuple((path, profile_for(graph, start, target, path))
                 for _, path in edge_histories(graph, start, horizon))


def _context(decoder):
    n = len(decoder)
    relation = tuple(tuple(i == j for j in range(n)) for i in range(n))
    return code_context((True,) * n, (True,) * n, relation), decoder


def selected_context(graph, start, target):
    return _context(selected_profiles(graph, start, target))


def full_context(graph, start, target, horizon):
    return _context(full_profiles(graph, start, target, horizon))
