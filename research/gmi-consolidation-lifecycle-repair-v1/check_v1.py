"""Complete source-bound finite consolidation correction receipt."""
import hashlib
import json
from itertools import product
from finite_machine_v1 import Machine, labels, refine, quotient, execute, preserving_update
from independent_oracle_v1 import census, distinguishing_word
from cost_controls_v1 import controls as cost_controls
from source_evidence_v1 import HERE, verify_sources, original_replay, independent_original

def future_control():
    m = Machine((0, 0, 1, 1), ((0, 2), (1, 1), (2, 2), (3, 3)),
                ((0, 2), (0, 2), (1, 2), (1, 2)))
    current = labels(m.q)
    try:
        quotient(m, current)
    except ValueError:
        pass
    else:
        raise ValueError("current quotient must reject teaching conflict")
    e = refine(m)
    if e != (0, 1, 2, 2):
        raise ValueError("wrong developmental quotient")
    small, e = quotient(m, e)
    word = distinguishing_word(m, 0, 1)
    if word is None or execute(m, 0, (1, 0))[0] == execute(m, 1, (1, 0))[0]:
        raise ValueError("future-teach countermodel failed")
    checked = 0
    for length in range(7):
        for actions in product(range(2), repeat=length):
            for s in range(4):
                raw, target = execute(m, s, actions)
                compressed, z = execute(small, e[s], actions)
                if raw != compressed or z != e[target]:
                    raise ValueError("constructed quotient failed")
                checked += 1
    return {"current_classes": len(set(current)), "future_classes": len(set(e)),
            "encoding": list(e), "shortest_distinguishing_word": list(word),
            "teach_query_traces": [execute(m, s, (1, 0))[0] for s in (0, 1)],
            "bounded_direct_trace_controls": checked,
            "all_words_proof": "complete finite homomorphism criterion"}

def update_control():
    q = tuple(range(4))
    destructive = (0, 0, 0, 0)
    preserved = (2, 0, 3, 1)
    if preserving_update(q, destructive) is not None:
        raise ValueError("capacity is not preservation")
    decoder = preserving_update(q, preserved)
    if any(decoder[preserved[s]] != q[s] for s in range(4)):
        raise ValueError("inverse decoder failed")
    return {"available_states": 4, "semantic_classes": 4,
            "destructive_update": list(destructive), "destructive_decodable": False,
            "preserving_update": list(preserved),
            "inverse_decoder": {str(k): v for k, v in decoder.items()}}

def run():
    bindings = verify_sources()
    historical, stdout = original_replay()
    if historical != independent_original():
        raise ValueError("independent full historical payload mismatch")
    return {"schema": "ConsolidationLifecycleRepairV1", "status": "PASS",
            "original_payload": historical, "original_script_stdout": stdout,
            "future_control": future_control(), "update_control": update_control(),
            "machine_census": census(), "cost_controls": cost_controls(),
            "source_files": bindings["files"],
            "native_or_campaign_calls": 0,
            "claim_scope": "finite supplied semantics and authored complete costs only"}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
