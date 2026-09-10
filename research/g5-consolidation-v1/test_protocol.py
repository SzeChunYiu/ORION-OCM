import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g5_consolidation", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = E
SPEC.loader.exec_module(E)


class TestProspectiveG54Protocol(unittest.TestCase):
    def test_production_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)

    def test_schemas_are_the_g2_g3_macros_not_a_new_invention(self):
        self.assertEqual(E.SCHEMA_PATTERNS["SDS"], ("square", "dec", "square"))
        self.assertEqual(E.SCHEMA_PATTERNS["SII"], ("square", "inc", "inc"))
        self.assertEqual(E.SCHEMA_PATTERNS["SDD"], ("square", "dec", "dec"))

    def test_salts_are_fresh_and_disjoint_from_g2_g3(self):
        prior = {
            "orion-ocm-g2-macro-training-v1",
            "orion-ocm-g2-macro-validation-v1",
            "orion-ocm-g2-macro-test-v1",
            "orion-ocm-g3-a-training-v1",
            "orion-ocm-g3-b-training-v1",
            "orion-ocm-g3-a-validation-v1",
            "orion-ocm-g3-b-validation-v1",
            "orion-ocm-g3-composition-test-v1",
        }
        self.assertNotIn(E.TRAIN_SALT, prior)
        self.assertNotIn(E.HELDOUT_SALT, prior)
        self.assertNotEqual(E.TRAIN_SALT, E.HELDOUT_SALT)

    def test_frozen_partition_is_small_disjoint_and_length_stratum_4_5(self):
        traces, heldout = E.frozen_partition()
        self.assertEqual((len(traces), len(heldout)), (E.TRAIN_N, E.HELDOUT_N))
        self.assertTrue(all(len(trace.program) in E.PROGRAM_LENGTHS for trace in traces + heldout))
        train_fp = {trace.fingerprint for trace in traces}
        held_fp = {trace.fingerprint for trace in heldout}
        self.assertFalse(train_fp & held_fp)
        self.assertEqual(len({trace.episode_id for trace in traces + heldout}), E.TRAIN_N + E.HELDOUT_N)
        dups = [trace.program for trace in traces]
        self.assertLess(len(set(dups)), len(dups))

    def test_schema_assignment_is_first_frozen_match(self):
        program = ("square", "dec", "square", "inc", "inc")
        schema_id, occurrence = E.find_schema(program)
        self.assertEqual((schema_id, occurrence), ("SDS", 0))

    def test_schema_residual_keeps_episode_identity_not_only_schema_id(self):
        traces = (
            E.make_trace("ep-a", ("inc", "square", "dec", "square")),
            E.make_trace("ep-b", ("dec", "square", "dec", "square")),
        )
        store = E.parent_schema_residual(traces, 0, 0.0)
        identities = [row["residual_identity"] for row in store.live["residuals"]]
        self.assertEqual(len(identities), 2)
        self.assertNotEqual(identities[0], identities[1])
        self.assertTrue(all(identity not in E.SCHEMA_ORDER for identity in identities))
        self.assertEqual(E.reconstruct(store, "ep-a"), traces[0].program)
        self.assertEqual(E.future_split_key(traces[0])[0], "inc")
        self.assertEqual(E.future_split_key(traces[1])[0], "dec")
        self.assertEqual(E.recovered_split_key(store, traces[0]), E.future_split_key(traces[0]))
        self.assertEqual(E.recovered_split_key(store, traces[1]), E.future_split_key(traces[1]))

    def test_fingerprint_dedup_drops_duplicate_episodes(self):
        traces = (
            E.make_trace("ep-a", ("inc", "square", "inc", "inc")),
            E.make_trace("ep-b", ("inc", "square", "inc", "inc")),
        )
        store = E.parent_fingerprint_dedup(traces, 0, 0.0)
        self.assertEqual(len(store.live["traces"]), 1)
        self.assertEqual(E.reconstruct(store, "ep-a"), traces[0].program)
        self.assertIsNone(E.reconstruct(store, "ep-b"))
        future = E.future_revision_ok(store, traces)
        self.assertFalse(future["ok"])

    def test_exceptions_remain_addressable_after_schema_store(self):
        traces = (
            E.make_trace("ep-s", ("square", "dec", "square", "inc")),
            E.make_trace("ep-e", ("inc", "dec", "double", "inc")),
        )
        store = E.parent_schema_residual(traces, 0, 0.0)
        self.assertEqual(traces[1].schema_id, None)
        self.assertEqual(E.exception_lookup(store, "ep-e"), traces[1].program)
        self.assertIsNone(E.exception_lookup(store, "ep-s"))
        self.assertTrue(store.archive_bytes > 0)
        self.assertEqual(store.archive["items"][0]["episode_id"], "ep-s")

    def test_structural_sharing_shares_prefixes_but_has_no_schema_tokens(self):
        traces = (
            E.make_trace("ep-a", ("inc", "inc", "double", "square")),
            E.make_trace("ep-b", ("inc", "inc", "double", "dec")),
        )
        store = E.parent_structural_sharing(traces, 0, 0.0)
        root = store.live["trie"]["children"]["inc"]["children"]["inc"]["children"]["double"]
        self.assertIn("square", root["children"])
        self.assertIn("dec", root["children"])
        heldout = (E.make_trace("ho-0", ("dec", "square", "dec", "square", "inc")),)
        cap = E.heldout_capability(store, heldout, macros=None)
        self.assertEqual(cap["method_use_count"], 0)
        self.assertEqual(cap["stored_hits"], 0)

    def test_schema_search_is_generative_on_unseen_wrapper(self):
        task = E.program_task(("inc", "square", "dec", "square"), "held")
        primitive = E.solve_task(task, E.build_search_index({}))
        schema = E.solve_task(task, E.build_search_index({"SDS": E.SCHEMA_PATTERNS["SDS"]}))
        self.assertIn("SDS", schema["macros_used"])
        self.assertLess(schema["enumeration_attempts"], primitive["enumeration_attempts"])
        self.assertEqual(tuple(schema["program"]), ("inc", "square", "dec", "square"))

    def test_archive_and_cpu_are_charged_on_consolidation(self):
        traces, _heldout = E.frozen_partition()
        stores = E.consolidate(traces)
        schema = stores["schema_residual"]
        self.assertGreater(schema.archive_bytes, 0)
        self.assertGreater(schema.consolidation_ops, 0)
        self.assertGreaterEqual(schema.consolidation_cpu_seconds, 0.0)
        self.assertEqual(
            schema.total_bytes,
            schema.live_bytes + schema.archive_bytes,
        )

    def test_ocm_revocation_drops_schema_keeps_exceptions_and_remaining_schemas(self):
        traces = (
            E.make_trace("ep-s1", ("inc", "square", "dec", "square")),
            E.make_trace("ep-s2", ("dec", "square", "dec", "square")),
            E.make_trace("ep-i1", ("inc", "square", "inc", "inc")),
            E.make_trace("ep-d1", ("inc", "square", "dec", "dec")),
            E.make_trace("ep-e1", ("inc", "dec", "double", "inc")),
        )
        store = E.parent_schema_residual(traces, 0, 0.0)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = E.admit_schema_residual(root / "live", traces, store, ())
            dead = E.admit_schema_residual(root / "dead", traces, store, ("SDS",))
        self.assertEqual(set(live["live_schemas"]), {"SDS", "SII", "SDD"})
        self.assertEqual(set(dead["live_schemas"]), {"SII", "SDD"})
        self.assertEqual(dead["live_exceptions"], {"ep-e1": ("inc", "dec", "double", "inc")})
        self.assertNotIn("SDS", dead["live_schemas"])


if __name__ == "__main__":
    unittest.main()
