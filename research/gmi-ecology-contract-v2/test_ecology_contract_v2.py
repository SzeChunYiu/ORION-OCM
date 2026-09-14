"""Exact and adversarial controls for #602 A2 ecology registration."""

from pathlib import Path
import copy
import importlib.util
import unittest

path = Path(__file__).with_name("ecology_contract_v2.py")
spec = importlib.util.spec_from_loader("ecology_contract_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class ContractControls(unittest.TestCase):
    def test_exact_contract_is_valid(self):
        self.assertEqual(mod.validate_contract(), [])
        self.assertEqual(len(mod.EXPECTED_COORDINATES), 16)

    def test_missing_coordinate_rejected(self):
        data = mod.load_contract()
        data = copy.deepcopy(data)
        del data["required_coordinates"]["social_topology"]
        self.assertTrue(any("coordinate set mismatch" in e for e in mod.validate_contract(data)))

    def test_g1_claim_ceiling_enforced(self):
        data = mod.load_contract()
        data = copy.deepcopy(data)
        data["claim_ceiling"] = "G5"
        self.assertTrue(any("ceiling must be G1" in e for e in mod.validate_contract(data)))

    def test_anti_leakage_registry_exact(self):
        data = mod.load_contract()
        data = copy.deepcopy(data)
        data["anti_leakage"]["forbidden_agent_visible_fields_by_default"].remove("remint_id")
        self.assertTrue(any("anti-leakage" in e for e in mod.validate_contract(data)))


class InstanceControls(unittest.TestCase):
    def test_finite_witness_covers_two_adaptive_agents(self):
        world = mod.witness_instance()
        self.assertEqual(mod.validate_instance(world), [])
        self.assertEqual(sum(1 for a in world["agents"] if a["adaptive"]), 2)

    def test_adaptive_agent_without_update_contract_rejected(self):
        world = mod.witness_instance()
        world["agents"][1]["adaptation_contract"] = ""
        self.assertTrue(any("lacks adaptation_contract" in e for e in mod.validate_instance(world)))

    def test_bad_social_edge_rejected(self):
        world = mod.witness_instance()
        world["social_edges"].append(["learner", "ghost"])
        self.assertTrue(any("unknown agent" in e for e in mod.validate_instance(world)))

    def test_protected_remint_identity_leak_rejected(self):
        world = mod.witness_instance()
        world["agent_visible_fields"].append("remint_id")
        self.assertTrue(any("protected fields visible" in e for e in mod.validate_instance(world)))

    def test_split_overlap_rejected(self):
        world = mod.witness_instance()
        world["split"]["heldout"].append("warm_task")
        self.assertTrue(any("splits must be disjoint" in e for e in mod.validate_instance(world)))

    def test_negative_verification_loss_rejected(self):
        world = mod.witness_instance()
        world["verifier"]["false_adoption_loss"] = -1
        self.assertTrue(any("false_adoption_loss" in e for e in mod.validate_instance(world)))


class ResourceControls(unittest.TestCase):
    def test_hard_budget_not_recoverable_from_price_scalar(self):
        budget = {"x": 1, "y": 2}
        price = {"x": 1, "y": 1}
        infeasible = {"x": 2, "y": 0}
        feasible = {"x": 0, "y": 2}
        self.assertEqual(mod.scalar_price(infeasible, price), mod.scalar_price(feasible, price))
        self.assertFalse(mod.componentwise_feasible(infeasible, budget))
        self.assertTrue(mod.componentwise_feasible(feasible, budget))

    def test_negative_prices_refused(self):
        with self.assertRaises(ValueError):
            mod.scalar_price({"x": 1}, {"x": -1})


class RemintControls(unittest.TestCase):
    def maps(self):
        first = {
            "learner": "agent_A", "peer": "agent_B",
            "cold": "state_A", "hot": "state_B",
            "blue": "obs_A", "red": "obs_B",
            "stay": "act_A", "toggle": "act_B",
            "force_cold": "intervene_A",
            "warm_task": "task_A", "cool_task": "task_B", "held_task": "task_C",
            "stable": "regime_A", "thermometer": "sensor_A", "switch": "actuator_A",
        }
        second = {v: "r2_%s" % i for i, v in enumerate(first.values())}
        return first, second

    def test_remint_reflexive(self):
        world = mod.witness_instance()
        self.assertTrue(mod.remint_equivalent(world, world, {}))

    def test_remint_symmetric_via_inverse(self):
        world = mod.witness_instance()
        first, _ = self.maps()
        renamed = mod.remint(world, first)
        self.assertTrue(mod.remint_equivalent(world, renamed, first))
        self.assertTrue(mod.remint_equivalent(renamed, world, mod.inverse_map(first)))

    def test_remint_transitive_via_composed_bijections(self):
        world = mod.witness_instance()
        first, second = self.maps()
        once = mod.remint(world, first)
        twice = mod.remint(once, second)
        composed = mod.compose_maps(first, second)
        self.assertTrue(mod.remint_equivalent(world, twice, composed))

    def test_semantic_change_is_not_a_remint(self):
        world = mod.witness_instance()
        first, _ = self.maps()
        renamed = mod.remint(world, first)
        renamed["verifier"]["false_adoption_loss"] += 1
        self.assertFalse(mod.remint_equivalent(world, renamed, first))

    def test_non_bijective_remint_rejected(self):
        world = mod.witness_instance()
        with self.assertRaises(ValueError):
            mod.remint(world, {"cold": "same", "hot": "same"})

    def test_run(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["a2_coordinates"], 16)
        self.assertEqual(result["claim_ceiling"], "G1")
        self.assertEqual(result["adaptive_agents"], 2)
        self.assertTrue(result["protected_fields_hidden"])


if __name__ == "__main__":
    unittest.main()
