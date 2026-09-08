"""Exposed authored controls. Independent algorithms here are NOT independent review."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1
import importlib.util
from itertools import combinations, product
from pathlib import Path
import unittest

import contracts as c

PARENT_BLOB = "4b32940e1a10705001ea0540f20c5067e578a348"
PARENT_PATH = Path(__file__).resolve().parents[1] / "decision-core-successor-repair-v1/decision_core.py"
raw = PARENT_PATH.read_bytes()
if sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != PARENT_BLOB:
    raise RuntimeError("CANNOT_CHECK_PARENT_SOURCE_DRIFT")
spec = importlib.util.spec_from_file_location("pinned_decision_core", PARENT_PATH)
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)


def observation(answer="same"):
    return dict(answer=answer, status="LIVE", warrant="fixture-checked",
                scope="exposed", authority="fixture-only", polarity="positive",
                support=["e1"], dependencies=["e1"], receipt="fixture-receipt",
                failure=None)


def action(name, successor, cost=0, answer="same"):
    return dict(id=name, observation=observation(answer), cost=[cost], outcomes=[(1, successor)])


def model(states=("s", "t")):
    return {
        "manifest": dict(source="4c5d3ec35cfa694572b968b4a85bd03321b0cf8d",
                         constitution="EXPOSED_FIXTURE_C1", operators="EXPOSED_FIXTURE_O1",
                         projection="EXPOSED_FIXTURE_P1", ecology="EXPOSED_FIXTURE_E1"),
        "resources": ["additive_work"],
        "states": {s: dict(stop=dict(observation=observation(), cost=[2]),
                           actions=[action("query", s)]) for s in states},
    }


def legacy_bisim(m, blocks):
    problem = c.meta_problem(m, [1])
    contracts = {(s, a["id"]): (a["observation"], a["cost"])
                 for s, node in m["states"].items() for a in node["actions"]}
    return parent.is_contract_bisimulation(
        problem["states"], problem["cognitive_actions"], contracts,
        problem["transitions"], blocks)


def partitions3():
    return [dict(zip(("0", "1", "2"), p)) for p in (
        ("a", "a", "a"), ("a", "a", "b"), ("a", "b", "a"),
        ("a", "b", "b"), ("a", "b", "c"))]


def literal_oracle(m, blocks):
    # Deliberately no calls into the production comparison or snapshot helpers.
    states = m["states"]
    for s, t in combinations(states, 2):
        if blocks[s] != blocks[t]:
            continue
        left, right = states[s], states[t]
        if left["stop"] != right["stop"]:
            return False
        if [a["id"] for a in left["actions"]] != [a["id"] for a in right["actions"]]:
            return False
        for a, b in zip(left["actions"], right["actions"]):
            if a["observation"] != b["observation"] or a["cost"] != b["cost"]:
                return False
            for block in set(blocks.values()):
                lmass = sum(p for p, target in a["outcomes"] if blocks[target] == block)
                rmass = sum(p for p, target in b["outcomes"] if blocks[target] == block)
                if lmass != rmass:
                    return False
    return True


def trace_signature(m, state, depth):
    # Separate deterministic one-action language oracle for the 3-state census.
    trace = []
    for step in range(depth + 1):
        node = m["states"][state]
        a = node["actions"][0]
        trace.append((node["stop"]["observation"]["answer"], tuple(node["stop"]["cost"]),
                      a["id"], a["observation"]["answer"], tuple(a["cost"])))
        state = a["outcomes"][0][1]
    return trace


class ContractsTests(unittest.TestCase):
    def test_parent_bytes_are_exact(self):
        self.assertEqual(len(raw), 12540)

    def test_reproduce_empty_version_parent_boundary(self):
        self.assertEqual(parent.contained_decision_actions([], {"execute": {"s"}}), {"execute"})
        with self.assertRaises(ValueError):
            parent.common_actions([], {"s": {"execute"}})
        with self.assertRaises(ValueError):
            c.common_actions_checked([], {"s": ["execute"]})

    def test_nonempty_common_actions_and_false_singleton_limit(self):
        good = {"s": ["a", "b"], "t": ["b"], "outside": ["c"]}
        self.assertEqual(c.common_actions_checked(["s", "t"], good), {"b"})
        self.assertEqual(c.common_actions_checked(["s"], good), {"a", "b"})
        # A nonempty result does not prove the true world is in the version set.
        self.assertFalse(c.common_actions_checked(["s"], good) & set(good["outside"]))
        self.assertEqual(c.common_actions_checked(["s", "outside"], good), set())

    def test_version_input_hostiles(self):
        for version, good in [(["s", "s"], {"s": []}), (["ghost"], {"s": []}),
                              ([True], {True: []}), (["s"], {"s": ["a", "a"]})]:
            with self.subTest(version=version), self.assertRaises((ValueError, TypeError)):
                c.common_actions_checked(version, good)

    def test_equivalent_states_valid(self):
        m = model()
        r = c.check_partition(m, {"s": "same", "t": "same"})
        self.assertEqual(r["status"], "TABLE_CONTRACT_VALID")
        self.assertIsNone(r["witness"])
        self.assertTrue(c.verify_receipt(m, r["partition"], r))

    def test_stop_cost_not_covered_by_parent_action_bisimulation(self):
        m, p = model(), {"s": "same", "t": "same"}
        m["states"]["t"]["stop"]["cost"] = [3]
        self.assertTrue(legacy_bisim(m, p))
        self.assertEqual(c.check_partition(m, p)["witness"]["reason"], "STOP_CONTRACT")
        values, _ = parent.finite_meta_dp(**c.meta_problem(m, [1]), budget=0)
        self.assertNotEqual(values[0]["s"], values[0]["t"])

    def test_every_stop_observable_is_preserved(self):
        for key in c.OBSERVATIONS:
            m = model()
            m["states"]["t"]["stop"]["observation"][key] = "changed"
            with self.subTest(field=key):
                self.assertEqual(c.check_partition(m, {"s": "a", "t": "a"})["status"], "REJECTED")

    def test_every_action_observable_is_preserved(self):
        for key in c.OBSERVATIONS:
            m = model()
            m["states"]["t"]["actions"][0]["observation"][key] = "changed"
            with self.subTest(field=key):
                self.assertEqual(c.check_partition(m, {"s": "a", "t": "a"})["witness"]["reason"], "ACTION_CONTRACT")

    def test_equal_value_does_not_preserve_selected_action(self):
        m, p = model(("s", "t", "z")), {"s": "a", "t": "a", "z": "z"}
        m["states"]["z"]["stop"]["cost"] = [0]
        m["states"]["z"]["actions"] = []
        for s, order in [("s", ["a", "b"]), ("t", ["b", "a"])]:
            m["states"][s]["actions"] = [action(a, "z") for a in order]
        self.assertTrue(legacy_bisim(m, p))
        values, policy = parent.finite_meta_dp(**c.meta_problem(m, [1]), budget=1)
        self.assertEqual(values[1]["s"], values[1]["t"])
        self.assertEqual((policy[1]["s"], policy[1]["t"]), ("a", "b"))
        self.assertEqual(c.check_partition(m, p)["witness"]["reason"], "ORDERED_ACTIONS")

    def test_revocation_breaks_current_answer_equivalence(self):
        m = model(("s", "t", "u", "v"))
        m["states"]["u"]["stop"]["observation"]["status"] = "UNKNOWN"
        m["states"]["s"]["actions"] = [action("revoke:e1", "u")]
        m["states"]["t"]["actions"] = [action("revoke:e1", "v")]
        p = {"s": "live", "t": "live", "u": "unknown", "v": "other"}
        self.assertEqual(c.check_partition(m, p)["witness"]["reason"], "SUCCESSOR_BLOCK_MASS")

    def test_explicit_restart_transition_is_checked_not_actual_restart_claimed(self):
        m = model()
        for node in m["states"].values():
            node["actions"].append(action("restart", "s", 1))
        self.assertEqual(c.check_partition(m, {"s": "a", "t": "a"})["status"], "TABLE_CONTRACT_VALID")

    def test_stochastic_mass_is_aggregated(self):
        m = model()
        m["states"]["s"]["actions"][0]["outcomes"] = [(Fraction(1, 3), "s"), (Fraction(2, 3), "t")]
        m["states"]["t"]["actions"][0]["outcomes"] = [(1, "t"), (0, "s")]
        self.assertEqual(c.check_partition(m, {"s": "a", "t": "a"})["status"], "TABLE_CONTRACT_VALID")

    def test_equivalent_kernel_encodings_have_same_identity(self):
        m = model()
        r = c.check_partition(m, {"s": "a", "t": "a"})
        m["states"]["s"]["actions"][0]["outcomes"] = [(Fraction(1, 2), "s"), (Fraction(1, 2), "s"), (0, "t")]
        self.assertTrue(c.verify_receipt(m, r["partition"], r))

    def test_exact_json_distinguishes_bool_and_integer(self):
        m = model()
        m["states"]["s"]["stop"]["observation"]["answer"] = True
        m["states"]["t"]["stop"]["observation"]["answer"] = 1
        self.assertEqual(c.check_partition(m, {"s": "a", "t": "a"})["status"], "REJECTED")

    def test_input_mutation_does_not_mutate_receipt(self):
        m = model()
        p = {"s": "a", "t": "a"}
        r = c.check_partition(m, p)
        old = deepcopy(r)
        p["s"] = "changed"
        m["states"]["s"]["stop"]["observation"]["support"].append("new")
        self.assertEqual(r, old)
        self.assertFalse(c.verify_receipt(m, old["partition"], old))

    def test_every_manifest_axis_invalidates_stale_receipt(self):
        for key in c.MANIFEST:
            m = model()
            r = c.check_partition(m, {"s": "a", "t": "a"})
            m["manifest"][key] = "f" * 40 if key == "source" else "successor"
            with self.subTest(axis=key):
                self.assertFalse(c.verify_receipt(m, r["partition"], r))

    def test_operator_extension_must_revalidate(self):
        m = model()
        r = c.check_partition(m, {"s": "a", "t": "a"})
        m["states"]["s"]["actions"].append(action("new", "s", answer="left"))
        m["states"]["t"]["actions"].append(action("new", "t", answer="right"))
        self.assertFalse(c.verify_receipt(m, r["partition"], r))
        self.assertEqual(c.check_partition(m, r["partition"])["status"], "REJECTED")

    def test_forged_receipt_rejected(self):
        m = model()
        p = {"s": "a", "t": "a"}
        r = c.check_partition(m, p)
        for field, value in [("status", "ACCEPTED"), ("checker_sha256", "0" * 64),
                             ("witness", {}), ("model_sha256", "0" * 64)]:
            bad = dict(r, **{field: value})
            with self.subTest(field=field):
                self.assertFalse(c.verify_receipt(m, p, bad))

    def test_invalid_fields_fail_closed(self):
        mutations = [
            lambda m: m.update(extra=True),
            lambda m: m["manifest"].pop("projection"),
            lambda m: m["states"]["s"].pop("stop"),
            lambda m: m["states"]["s"]["stop"]["observation"].pop("failure"),
            lambda m: m["states"]["s"]["actions"][0].update(extra=1),
            lambda m: m["states"].clear(),
            lambda m: m.update(resources=[]),
            lambda m: m.update(resources=["x", "x"]),
            lambda m: m["states"]["s"]["actions"].append(deepcopy(m["states"]["s"]["actions"][0])),
            lambda m: m["states"]["s"]["actions"][0].update(id=c.STOP),
        ]
        for index, mutation in enumerate(mutations):
            m = model()
            mutation(m)
            with self.subTest(case=index), self.assertRaises((ValueError, TypeError)):
                c.check_partition(m, {"s": "a", "t": "a"})

    def test_invalid_numbers_fail_closed(self):
        for bad in [True, 0.5, float("nan"), float("inf"), -1, "1"]:
            for where in ("stop", "action", "probability"):
                m = model()
                if where == "stop":
                    m["states"]["s"]["stop"]["cost"] = [bad]
                elif where == "action":
                    m["states"]["s"]["actions"][0]["cost"] = [bad]
                else:
                    m["states"]["s"]["actions"][0]["outcomes"] = [(bad, "s")]
                with self.subTest(bad=repr(bad), where=where), self.assertRaises((TypeError, ValueError)):
                    c.check_partition(m, {"s": "a", "t": "a"})

    def test_zero_mass_unknown_and_invalid_unreachable_kernel(self):
        for outcomes in [[(1, "s"), (0, "ghost")], [], [(Fraction(1, 2), "s")], [(2, "s")]]:
            m = model()
            m["states"]["t"]["actions"][0]["outcomes"] = outcomes
            with self.subTest(outcomes=outcomes), self.assertRaises(ValueError):
                c.meta_problem(m, [1])

    def test_partition_requires_exact_coverage(self):
        for p in [{}, {"s": "a"}, {"s": "a", "t": "a", "ghost": "a"}, {"s": None, "t": "a"}]:
            with self.subTest(partition=p), self.assertRaises(ValueError):
                c.check_partition(model(), p)

    def test_cost_dimensions_and_weights(self):
        m = model()
        for weights in [[], [1, 2], [True], [-1], [0.5]]:
            with self.subTest(weights=weights), self.assertRaises((ValueError, TypeError)):
                c.meta_problem(m, weights)
        m["states"]["s"]["stop"]["cost"] = [1, 2]
        with self.assertRaises(ValueError):
            c.check_partition(m, {"s": "a", "t": "a"})

    def test_vector_costs_all_declared_prices_preserve_dp(self):
        m = model()
        m["resources"] = ["work", "io_bytes"]
        for node in m["states"].values():
            node["stop"]["cost"] = [2, 5]
            node["actions"][0]["cost"] = [0, Fraction(1, 3)]
        self.assertEqual(len(set(c.coarsest_partition(m).values())), 1)
        for weights in ([0, 0], [1, 0], [0, 1], [Fraction(2, 3), 5]):
            values, policies = parent.finite_meta_dp(**c.meta_problem(m, weights), budget=4)
            for h in range(5):
                self.assertEqual(values[h]["s"], values[h]["t"])
                self.assertEqual(policies[h]["s"], policies[h]["t"])

    def test_stochastic_dp_and_stop_ties(self):
        m = model(("s", "t", "z"))
        m["states"]["z"]["stop"]["cost"] = [0]
        m["states"]["z"]["actions"] = []
        for state in ("s", "t"):
            m["states"][state]["stop"]["cost"] = [5]
            m["states"][state]["actions"][0]["outcomes"] = [(Fraction(1, 2), state), (Fraction(1, 2), "z")]
        p = {"s": "a", "t": "a", "z": "z"}
        self.assertEqual(c.check_partition(m, p)["status"], "TABLE_CONTRACT_VALID")
        values, policies = parent.finite_meta_dp(**c.meta_problem(m, [1]), budget=7)
        for h in range(8):
            self.assertEqual(values[h]["s"], values[h]["t"])
            self.assertEqual(policies[h]["s"], policies[h]["t"])
        m = model()
        _, policies = parent.finite_meta_dp(**c.meta_problem(m, [1]), budget=4)
        self.assertTrue(all(policy["s"] is None for policy in policies))

    def test_non_json_observations_fail_closed(self):
        for bad in [0.5, {"set"}, object(), Fraction(1, 2)]:
            m = model()
            m["states"]["t"]["stop"]["observation"]["answer"] = bad
            with self.subTest(value=repr(bad)), self.assertRaises(TypeError):
                c.check_partition(m, {"s": "a", "t": "a"})

    def test_state_input_order_does_not_change_canonical_partition(self):
        m = model()
        p = c.coarsest_partition(m)
        m["states"] = dict(reversed(list(m["states"].items())))
        self.assertEqual(p, c.coarsest_partition(m))

    def test_exhaustive_three_state_census(self):
        checked, accepted = 0, 0
        for labels in product(range(2), repeat=3):
            for costs in product(range(2), repeat=3):
                for successors in product(range(3), repeat=3):
                    m = model(("0", "1", "2"))
                    for index, node in enumerate(m["states"].values()):
                        node["stop"]["observation"]["answer"] = labels[index]
                        node["stop"]["cost"] = [labels[index] + 1]
                        node["actions"] = [action("step", str(successors[index]), costs[index])]
                    for p in partitions3():
                        valid = c.check_partition(m, p)["status"] == "TABLE_CONTRACT_VALID"
                        self.assertEqual(valid, literal_oracle(m, p))
                        checked += 1
                        accepted += valid
                    coarse = c.coarsest_partition(m)
                    for s, t in combinations(m["states"], 2):
                        self.assertEqual(coarse[s] == coarse[t],
                                         trace_signature(m, s, 2) == trace_signature(m, t, 2))
                    values, policies = parent.finite_meta_dp(**c.meta_problem(m, [1]), budget=4)
                    for s, t in combinations(m["states"], 2):
                        if coarse[s] == coarse[t]:
                            for h in range(5):
                                self.assertEqual(values[h][s], values[h][t])
                                self.assertEqual(policies[h][s], policies[h][t])
        self.assertEqual(checked, 8640)
        type(self).census = dict(models=1728, partitions=checked, accepted=accepted,
                                 rejected=checked-accepted, horizons=[0, 1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
