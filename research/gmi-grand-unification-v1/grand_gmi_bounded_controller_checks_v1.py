"""Independent product-graph oracle and small exhaustive bounded-controller census."""
from itertools import product
import json
from pathlib import Path
import sys

# The capsule runs standalone checkers with -I; this bound sibling is explicit.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grand_gmi_bounded_controller_model_v1 import (
    Model, controllers, decode_controller, decode_model, encode_controller,
    encode_model, evaluate, search, validate, width,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def graph_winning(model, controller):
    """Independent backwards reachability; no forward trace, cycle test, or step bound."""
    winning, edges = set(), {}
    for state in range(len(model.transitions)):
        for node, (opcode, destinations) in enumerate(controller):
            pair = (state, node)
            if opcode < model.actions:
                if model.goals[state] & (1 << opcode):
                    winning.add(pair)
            else:
                edge = model.transitions[state][opcode-model.actions]
                if edge is not None:
                    target, observation = edge
                    edges[pair] = (target, destinations[observation])
    while True:
        enlarged = winning | {pair for pair, target in edges.items() if target in winning}
        if enlarged == winning:
            return all((state, 0) in winning for state in model.initial)
        winning = enlarged


def blind_chain(length=2, feedback=False):
    rows = [((s+1, int(feedback and s == length-1)),) for s in range(length)]
    return Model(tuple(rows)+((None,),), (0,)*length+(1,), (0,), 1, 2 if feedback else 1)


def canonical_chain_controller(length=2):
    return tuple((1, (q+1,)) for q in range(length))+((0, ()),)


def census():
    comparisons = wins = payloads = models = 0
    options = (None, (0, 0), (1, 0))
    for transitions in product(options, repeat=2):
        for goals in product((0, 1), repeat=2):
            for initial in ((0,), (1,), (0, 1)):
                model = Model(tuple((edge,) for edge in transitions), goals, initial)
                models += 1
                require(decode_model(encode_model(model), 2, 1, 1, 1) == model,
                        "model payload failed exact round trip")
                for j in (1, 2):
                    for controller in controllers(model, j):
                        report = evaluate(model, controller)
                        require(report["success"] == graph_winning(model, controller),
                                "trace verifier disagrees with independent product graph")
                        encoded = encode_controller(model, controller)
                        require(decode_controller(encoded, model, j) == controller,
                                "controller payload failed exact round trip")
                        require(len(encoded) == j*(1+width(j)), "payload length mismatch")
                        if report["success"]:
                            require(max(t for _, t in report["runs"]) < 2*j,
                                    "successful run exceeded product bound")
                        comparisons += 1
                        wins += report["success"]
                        payloads += 1
    return {"models": models, "model_controller_pairs": comparisons,
            "successful_pairs": wins, "failed_pairs": comparisons-wins,
            "controller_payload_round_trips": payloads, "model_payload_round_trips": models}


def summary(result):
    return {key: value for key, value in result.items() if key != "winners"} | {
        "successful_controllers": len(result["winners"]),
        "joint_profiles": sorted(set(profile for _, profile in result["winners"]))}


def run():
    blind = blind_chain()
    rejected, revived = search(blind, 2), search(blind, 3)
    require(not rejected["winners"] and revived["winners"], "blind state-bound separation failed")
    witness = canonical_chain_controller()
    require(evaluate(blind, witness)["profile"] == (2, 9, 12, 2, 5), "charged witness profile changed")
    require(all(graph_winning(blind, controller) for controller, _ in revived["winners"]),
            "revival controller is not independently successful")
    require(not search(blind, 3, (1, 9, 12, 2, 5))["winners"], "live memory ceiling bypassed")
    require(not search(blind, 3, (2, 8, 12, 2, 5))["winners"], "stored program ceiling bypassed")
    require(not search(blind, 3, (2, 9, 11, 2, 5))["winners"], "model payload ceiling bypassed")
    require(search(blind, 3, (2, 9, 12, 2, 5))["winners"], "exact full profile falsely rejected")
    feedback = blind_chain(feedback=True)
    feedback_controller = ((1, (0, 1)), (0, ()))
    feedback_report = evaluate(feedback, feedback_controller)
    require(feedback_report["success"] and graph_winning(feedback, feedback_controller),
            "physical-progress loop revival failed")
    hidden = Model((((1, 0),), (None,)), (0, 1), (0, 1))
    require(not search(hidden, 3)["winners"], "controller rows leaked hidden physical state")
    loop = Model((((0, 0),),), (0,), (0,))
    require(evaluate(loop, ((1, (0,)),))["runs"] == (("LOOP", 1),), "losing loop accepted")
    require(evaluate(hidden, ((1, (0,)),))["runs"][1][0] == "ILLEGAL", "illegal action accepted")
    result = census()
    require(result["model_controller_pairs"] == 1188 and result["models"] == 108,
            "exhaustive register omitted candidates")
    return {"schema": "bounded-controller-resource-v1", "all_checks_green": True,
            "terminal": "BOUNDED_CONTROLLER_RESOURCE_FINITE_GREEN",
            "scope": "deterministic Moore tables; complete finite physical states; strong termination",
            "profile_order": ["live_node_bits", "stored_controller_bits", "model_input_bits",
                              "worst_controls", "worst_runtime_table_accesses"],
            "blind_bound_2": summary(rejected), "blind_bound_3": summary(revived),
            "blind_witness_profile": evaluate(blind, witness)["profile"],
            "final_retained_action_bits": 0,
            "feedback_bound_2_profile": feedback_report["profile"],
            "hidden_initial_state_consistency_control": "ALL_CONTROLLERS_REJECTED_THROUGH_3_NODES",
            "census": result,
            "development_count_scope": "candidate evaluations, initial runs, inspected distinct product pairs and physical transition lookups; excludes parsing, allocation and encoding work",
            "representation_scope": "fixed dimension binary table payloads; header/interpreter/interface and physical costs require a separate implementation ledger"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
