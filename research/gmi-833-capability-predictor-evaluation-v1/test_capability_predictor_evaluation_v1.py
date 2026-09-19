"""Receipt gates for gmi-833-capability-predictor-evaluation-v1.

Run:  python3 -I -B  test_capability_predictor_evaluation_v1.py -v
      python3 -I -O -B test_capability_predictor_evaluation_v1.py -v
"""

import ast
import hashlib
import itertools
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu          # noqa: E402
import external_evaluator_v1 as ev         # noqa: E402
import heldout_universes_v2 as hv          # noqa: E402
import heldout_universes_v3 as hw          # noqa: E402
import heldout_universes_v4 as hx          # noqa: E402
import oracle_route_b_v1 as rb             # noqa: E402

GIT = "/usr/bin/git"

FORBIDDEN_AT_FREEZE = (
    "external_evaluator_v1.py",
    "oracle_route_b_v1.py",
    "score_heldout_v1.py",
    "real_systems_run_v1.py",
    "test_capability_predictor_evaluation_v1.py",
    "RESULT_V1.json",
    "ROUTE_B_RESULT_V1.json",
    "REAL_RUNS",
)
REQUIRED_AT_FREEZE = (
    "FREEZE_V1.md",
    "SCOPE_V1.md",
    "BLINDNESS_V1.md",
    "heldout_universes_v1.py",
    "freeze_predictions_v1.py",
    "FROZEN_PREDICTIONS_V1.json",
)


def load(name):
    with open(os.path.join(HERE, name)) as handle:
        return json.load(handle)


def repo_root():
    cur = HERE
    while True:
        if os.path.isdir(os.path.join(cur, ".git")) or os.path.isfile(os.path.join(cur, ".git")):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            return None
        cur = nxt


def git_lines(args):
    """Run git and return stdout lines; None means COULD NOT CHECK."""
    root = repo_root()
    if root is None or not os.path.exists(GIT):
        return None
    try:
        proc = subprocess.Popen([GIT, "-C", root] + args,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _err = proc.communicate()
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return out.decode("utf-8", "replace").splitlines()


class FreezeOrder(unittest.TestCase):
    """The #976 POST_HOC_SUSPECT failure class, checked with a negative control."""

    def setUp(self):
        path = os.path.join(HERE, "FREEZE_COMMIT.txt")
        self.assertTrue(os.path.exists(path), "FREEZE_COMMIT.txt is missing")
        with open(path) as handle:
            self.freeze = handle.read().strip().split()[0]

    def test_freeze_commit_is_an_ancestor_of_head(self):
        lines = git_lines(["rev-list", "HEAD"])
        self.assertIsNotNone(lines, "COULD NOT CHECK: git history unavailable")
        if self.freeze not in lines:
            # Squash-published (91c6d287): the source freeze commit is no
            # longer on HEAD's history. The ordering rests on the shared
            # squash-safe checker run by the workflow; here require the
            # package to have entered history in a single-parent "(#N)"
            # commit whose parent held nothing of the package, and the
            # freeze bytes at HEAD to be the bytes at the pinned commit
            # when it is still reachable.
            first = git_lines(["log", "--reverse", "--format=%H", "--",
                               "research/gmi-833-capability-predictor-evaluation-v1"])
            self.assertTrue(first, "package has no history")
            parents = git_lines(["rev-list", "--parents", "-n", "1", first[0]])
            self.assertIsNotNone(parents)
            self.assertEqual(len(parents[0].split()), 2, "not a single-parent commit")
            subject = git_lines(["log", "-1", "--format=%s", first[0]])
            self.assertRegex(subject[0], r"\(#[0-9]+\)\s*$", "not a squash-publication subject")
            par = parents[0].split()[1]
            at_parent = git_lines(["ls-tree", "-r", "--name-only", par, "--",
                                   "research/gmi-833-capability-predictor-evaluation-v1/"])
            self.assertEqual(at_parent, [], "package already present in the parent")
            at_head = git_lines(["rev-parse", "HEAD:research/gmi-833-capability-predictor-evaluation-v1/FREEZE_V1.md"])
            at_pin = git_lines(["rev-parse", self.freeze + ":research/gmi-833-capability-predictor-evaluation-v1/FREEZE_V1.md"])
            if at_pin is not None:
                self.assertEqual(at_head, at_pin, "freeze bytes differ from the pinned commit")
            self.skipTest("FREEZE_ORDER_NOT_REDERIVABLE: squash-published in %s; "
                          "HEAD-derivable checks passed" % first[0][:8])

    def test_no_implementation_artifact_at_the_freeze_commit(self):
        lines = git_lines(["ls-tree", "-r", "--name-only", self.freeze,
                           "--", "research/gmi-833-capability-predictor-evaluation-v1/"])
        self.assertIsNotNone(lines, "COULD NOT CHECK: git ls-tree unavailable")
        names = set(os.path.basename(p) for p in lines)
        prefixes = set(p.split("/")[3] for p in lines if len(p.split("/")) > 3)
        for bad in FORBIDDEN_AT_FREEZE:
            self.assertNotIn(bad, names,
                             "%s is reachable from the freeze commit" % bad)
            self.assertNotIn(bad, prefixes,
                             "%s/ is reachable from the freeze commit" % bad)
        # negative control: a path typo must not make this vacuously green
        for good in REQUIRED_AT_FREEZE:
            self.assertIn(good, names,
                          "negative control failed: %s absent at the freeze commit" % good)

    def test_implementation_artifacts_were_added_after_the_freeze(self):
        after = git_lines(["rev-list", self.freeze + "..HEAD"])
        self.assertIsNotNone(after, "COULD NOT CHECK: git rev-list unavailable")
        for name in ("score_heldout_v1.py", "external_evaluator_v1.py",
                     "oracle_route_b_v1.py"):
            path = "research/gmi-833-capability-predictor-evaluation-v1/" + name
            intro = git_lines(["log", "--diff-filter=A", "--format=%H", "--", path])
            self.assertIsNotNone(intro, "COULD NOT CHECK: git log unavailable")
            self.assertTrue(intro, "%s has no introducing commit" % name)
            self.assertIn(intro[-1], after,
                          "%s was introduced at or before the freeze" % name)


class ParentIntegrity(unittest.TestCase):
    def test_parent_blob_pin(self):
        self.assertEqual(hu.git_blob_sha(hu.PARENT_FILE), hu.PARENT_BLOB_SHA)

    def test_parent_blob_mutation_is_detected(self):
        with open(hu.PARENT_FILE, "rb") as handle:
            data = handle.read()
        header = ("blob %d\0" % (len(data) + 1)).encode("ascii")
        mutated = hashlib.sha1(header + data + b"#").hexdigest()
        self.assertNotEqual(mutated, hu.PARENT_BLOB_SHA)

    def test_injection_never_changes_F(self):
        parent = hu.load_parent()
        before = hu.code_fingerprint(parent)
        for builder in (hu.sigma_syn, hu.sigma_arch, hu.sigma_real,
                        hv.sigma_real2, hw.sigma_real3,
                        hx.sigma_syn2, hx.sigma_arch2):
            spec = builder()
            clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
            after = hu.install_universe(parent, clean)
            self.assertEqual(before[0], after[0])
        self.assertEqual(before, hu.code_fingerprint(parent))

    def test_registration_surface_is_closed(self):
        parent = hu.load_parent()
        spec = hu.sigma_syn()
        clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
        clean.pop("CAP")
        self.assertRaises(ValueError, hu.install_universe, parent, clean)
        clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
        clean["NOT_REGISTERED"] = 1
        self.assertRaises(ValueError, hu.install_universe, parent, clean)


class Disjointness(unittest.TestCase):
    def test_all_eight_populations_are_pairwise_disjoint(self):
        parent = hu.load_parent()
        base = hu.sigma_1()
        pops = [("SIGMA_1", base), ("SIGMA_SYN", hu.SYN_RAW),
                ("SIGMA_ARCH", hu.ARCH_RAW), ("SIGMA_REAL", hu.REAL_RAW),
                ("SIGMA_REAL2", hv.REAL2_RAW), ("SIGMA_REAL3", hw.REAL3_RAW),
                ("SIGMA_SYN2", hx.SYN2_RAW), ("SIGMA_ARCH2", hx.ARCH2_RAW)]
        sizes = [len(p[1]) for p in pops]
        pairs = 0
        checked = 0
        for i in range(len(pops)):
            for j in range(i + 1, len(pops)):
                cert = hu.disjointness_certificate(pops[i][1], pops[i][0],
                                                   pops[j][1], pops[j][0])
                self.assertTrue(cert["disjoint"], cert)
                self.assertTrue(cert["separator_holds"], cert)
                pairs += cert["pairs_checked"]
                checked += 1
        expected = sum(sizes[i] * sizes[j] for i in range(len(sizes))
                       for j in range(i + 1, len(sizes)))
        self.assertEqual(checked, 28)
        self.assertEqual(pairs, expected)

    def test_the_separator_really_separates(self):
        self.assertEqual(sorted(set(r[4][3] for r in hu.sigma_1())), [0])
        self.assertEqual(sorted(set(r[4][3] for r in hu.SYN_RAW)), [1, 2])
        self.assertEqual(sorted(set(r[4][3] for r in hu.ARCH_RAW)), [3, 4])
        self.assertEqual(sorted(set(r[4][3] for r in hu.REAL_RAW)), [5, 6])
        self.assertEqual(sorted(set(r[4][3] for r in hv.REAL2_RAW)), [7, 8])
        self.assertEqual(sorted(set(r[4][3] for r in hw.REAL3_RAW)), [9, 10])
        self.assertEqual(sorted(set(r[4][3] for r in hx.SYN2_RAW)), [11, 12])
        self.assertEqual(sorted(set(r[4][3] for r in hx.ARCH2_RAW)), [13, 14])


class RegistrationLaw(unittest.TestCase):
    """The closed-form law and brute-force simulation are two routes."""

    def test_syn_law_matches_simulation(self):
        for machine in hu.SYN_MACHINES:
            self.assertEqual(hu.syn_solved_law(machine),
                             ev.measure_solved_bits(hu.syn_machine_answer, machine),
                             machine)

    def test_arch_law_matches_simulation(self):
        for machine in hu.ARCH_MACHINES:
            self.assertEqual(hu.arch_solved_law(machine),
                             ev.measure_solved_bits(hu.arch_machine_answer, machine),
                             machine)

    def test_power_revival_laws_match_simulation(self):
        for machine in hx.SYN2_MACHINES:
            self.assertEqual(hx.syn2_solved_law(machine),
                             ev.measure_solved_bits(hx.syn2_machine_answer, machine),
                             machine)
        for machine in hx.ARCH2_MACHINES:
            self.assertEqual(hx.arch2_solved_law(machine),
                             ev.measure_solved_bits(hx.arch2_machine_answer, machine),
                             machine)
        self.assertEqual(len(hx.SYN2_MACHINES), 128)
        self.assertEqual(len(hx.ARCH2_MACHINES), 176)

    def test_a_planted_wrong_law_is_caught(self):
        def wrong(machine):
            m, w, h = machine
            bits = hu.syn_solved_law(machine)
            if m == 6:
                bits |= 1
            return bits
        bad = [m for m in hu.SYN_MACHINES
               if wrong(m) != ev.measure_solved_bits(hu.syn_machine_answer, m)]
        self.assertTrue(bad, "the planted wrong law was not caught")


class Blindness(unittest.TestCase):
    """The family NAME must not be an input; the mechanism structure may be."""

    FAMILY_NAMES = ("FF", "REC", "CTR", "STK")

    # The structural record the descriptor actually depends on.  The family
    # string is only a key into it, which is what the permutation test proves.
    STRUCT = {
        "FF": {"r0_extra": 0, "r3_extra": 0, "k": 0, "params": (1, 2)},
        "REC": {"r0_extra": 0, "r3_extra": 1, "k": 1, "params": (2, 3)},
        "CTR": {"r0_extra": 1, "r3_extra": 1, "k": 1, "params": (2, 4)},
        "STK": {"r0_extra": 1, "r3_extra": 0, "k": 2, "params": (1, 2)},
    }

    def _refs(self, source, func_names, wanted):
        tree = ast.parse(source)
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in func_names:
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Name) and sub.id in wanted:
                        hits.append((node.name, sub.id))
                    if isinstance(sub, ast.Attribute) and sub.attr in wanted:
                        hits.append((node.name, sub.attr))
        return hits

    def test_no_predictor_path_reads_the_label_list(self):
        with open(os.path.join(HERE, "heldout_universes_v1.py")) as handle:
            source = handle.read()
        wanted = set(("ARCH_LABELS", "labels", "family", "label"))
        self.assertEqual(
            self._refs(source, set(("arch_descriptor", "make_spec", "cap_table",
                                    "install_universe", "_expr_mask", "_res_mask",
                                    "_reach_mask", "_seen_mask", "_obs_mask")), wanted),
            [])

    def test_the_label_reference_audit_flags_a_planted_leak(self):
        planted = (
            "def arch_descriptor(machine):\n"
            "    mech, param, w, h = machine\n"
            "    k = 2 if ARCH_LABELS[0] == 'REC' else 0\n"
            "    return k, (), 0, ()\n")
        self.assertTrue(self._refs(planted, set(("arch_descriptor",)),
                                   set(("ARCH_LABELS",))))

    def test_the_realization_record_carries_no_mechanism_tag(self):
        for rec in hu.ARCH_RAW:
            for field in rec[:3] + (rec[3], rec[5]):
                self.assertNotIsInstance(field, str)
            self.assertFalse(any(isinstance(x, str) for x in rec[4]))
            self.assertFalse(any(isinstance(x, str) for x in rec[6]))

    def test_k_is_not_a_recoding_of_the_family_name(self):
        seen = {}
        for machine in hu.ARCH_MACHINES:
            seen.setdefault(hu.arch_descriptor(machine)[0], set()).add(machine[0])
        collapsed = [k for k, fams in seen.items() if len(fams) > 1]
        self.assertTrue(collapsed, "every k maps to exactly one family")

    def _rebuild(self, names):
        """Rebuild SIGMA_ARCH under a renaming of the four families."""
        rename = dict(zip(Blindness.FAMILY_NAMES, names))
        struct = dict((rename[f], Blindness.STRUCT[f]) for f in Blindness.FAMILY_NAMES)
        raw = []
        for f in Blindness.FAMILY_NAMES:
            name = rename[f]
            info = struct[name]
            for param in info["params"]:
                for w in (0, 1):
                    for h in range(8):
                        rho = [0] * hu.RHO_DIM_HELDOUT
                        rho[0] = param + info["r0_extra"]
                        rho[1] = 1 + w
                        rho[2] = 1 + hu.popcount(h)
                        rho[3] = 3 + info["r3_extra"]
                        dev = param + hu.popcount(h) + w + info["k"]
                        raw.append((param, w, h, info["k"], tuple(rho), dev,
                                    (1 + w, param % 2)))
        return tuple(raw)

    def test_family_renaming_leaves_the_universe_identical(self):
        checked = 0
        for perm in itertools.permutations(Blindness.FAMILY_NAMES):
            self.assertEqual(self._rebuild(perm), hu.ARCH_RAW, perm)
            checked += 1
        self.assertEqual(checked, 24)

    def test_the_structural_record_reproduces_the_shipped_encoder(self):
        self.assertEqual(self._rebuild(Blindness.FAMILY_NAMES), hu.ARCH_RAW)


class Receipts(unittest.TestCase):
    def setUp(self):
        self.result = load("RESULT_V1.json")
        self.routeb = load("ROUTE_B_RESULT_V1.json")
        self.frozen = load("FROZEN_PREDICTIONS_V1.json")
        for extra in ("FROZEN_PREDICTIONS_V2.json", "FROZEN_PREDICTIONS_V3.json",
                      "FROZEN_PREDICTIONS_V4.json"):
            self.frozen["universes"] = (list(self.frozen["universes"])
                                        + list(load(extra)["universes"]))

    def test_prediction_replay_matches_the_freeze(self):
        for row in self.result["prediction_replay"]:
            self.assertTrue(row["matches_freeze"], row)

    def test_route_b_reproduces_the_frozen_stream_sha256(self):
        frozen = dict((u["universe"], u["predictions_sha256"])
                      for u in self.frozen["universes"])
        checked = 0
        for row in self.routeb["universes"]:
            if row.get("status") == "OUTCOMES_UNAVAILABLE":
                continue
            self.assertEqual(row["predictions_sha256"], frozen[row["universe"]],
                             row["universe"])
            checked += 1
        self.assertEqual(checked, 7,
                         "route B must cover all seven held-out universes")

    def test_no_soundness_violation_on_any_scored_universe(self):
        scored = 0
        for row in self.result["universes"]:
            if row.get("status") != "SCORED":
                continue
            scored += 1
            # the unconditional claim: F is never wrong about a world whose
            # registration is truthful (KP-1B carried to the held-out universe)
            self.assertEqual(
                row["point_scoring"]["soundness_violations_on_truthfully_registered_worlds"],
                0, row["universe"])
            self.assertGreater(row["point_scoring"]["truthfully_registered_world_pairs"], 0,
                               "vacuous: no truthfully registered pair was scored")
            if row["universe"] in ("SIGMA_SYN2", "SIGMA_ARCH2"):
                # the power revival: the soundness census must not rest on
                # degenerate points alone
                self.assertGreater(row["point_scoring"]["nondegenerate_point_emissions"], 0,
                                   row["universe"])
            if row["registration"]["truthful"]:
                self.assertEqual(row["point_scoring"]["soundness_violations"], 0,
                                 row["universe"])
            self.assertGreater(row["point_scoring"]["point_world_pairs"], 0,
                               "vacuous: no point emission was scored")
        self.assertGreaterEqual(scored, 2)

    def test_coverage_is_exact_where_registration_is_truthful(self):
        for row in self.result["universes"]:
            if row.get("status") != "SCORED":
                continue
            if not row["registration"]["truthful"]:
                continue
            self.assertTrue(row["coverage"]["exact"], row["universe"])
            self.assertGreater(row["coverage"]["pairs"], 0)

    def test_calibration_is_non_vacuous_and_unviolated(self):
        buckets = 0
        for row in self.result["universes"]:
            if row.get("status") != "SCORED":
                continue
            if not row["registration"]["truthful"]:
                continue
            for key, bucket in sorted(row["calibration"].items()):
                self.assertGreater(bucket["emissions"], 0, key)
                self.assertEqual(bucket["violations_below_nominal"], 0, (row["universe"], key))
                self.assertTrue(Fraction(bucket["min_empirical_coverage"])
                                >= Fraction(bucket["nominal_lower_bound"]))
                # the sharp gate: point emissions, where miscalibration would show
                self.assertGreater(bucket["point_emissions"], 0, key)
                self.assertEqual(bucket["point_violations_below_nominal"], 0,
                                 (row["universe"], key))
                self.assertTrue(Fraction(bucket["min_point_coverage"])
                                >= Fraction(bucket["nominal_lower_bound"]))
                self.assertIn("abstention_rate", bucket)
                buckets += 1
        self.assertGreaterEqual(buckets, 4)

    def test_hostiles_are_detected(self):
        applicable = 0
        for block in self.result["controls"]:
            if block.get("status") == "OUTCOMES_UNAVAILABLE":
                continue
            self.assertEqual(block["BASELINE"], 0, block["universe"])
            if block["HE1_applicable"]:
                self.assertGreater(block["HE1_complemented_capability_law"], 0,
                                   block["universe"])
                applicable += 1
            self.assertGreater(block["HE2_no_unsatisfied_branch"], 0, block["universe"])
            self.assertGreater(block["HE3_resource_pruned_predictor_violations"], 0,
                               block["universe"])
            self.assertGreater(block["HE6_truncated_identified_set_coverage_failures"], 0,
                               block["universe"])
            self.assertTrue(block["all_hostiles_detected"], block["universe"])
        self.assertGreaterEqual(applicable, 2,
                                "HE1 was vacuous on every universe: no non-degenerate "
                                "point emission was scored anywhere")

    def test_null_control_is_beaten(self):
        for block in self.result["controls"]:
            if block.get("status") == "OUTCOMES_UNAVAILABLE":
                continue
            self.assertGreater(block["NULL_MODAL_head_to_head_pairs"], 0)
            self.assertGreater(block["NULL_MODAL_head_to_head_violations"], 0)
            self.assertEqual(block["F_head_to_head_violations"], 0)

    def test_inflated_fault_law_breaks_calibration(self):
        self.assertTrue(self.result["HE5_inflated_fault_law"]["detected"])

    def test_curves_agree_point_by_point(self):
        truthful = set(u["universe"] for u in self.result["universes"]
                       if u.get("status") == "SCORED" and u["registration"]["truthful"])
        checked = 0
        for row in self.result["curves"]:
            if row.get("status") != "SCORED":
                continue
            # the freeze-vs-replay identity holds on EVERY universe
            self.assertEqual(row["replay_mismatches"], 0, row["universe"])
            if row["universe"] not in truthful:
                # an untruthfully-registered universe may disagree; that is a
                # bridge failure (KP-1D), reported, not gated
                continue
            self.assertGreater(row["identified_points"], 0, "vacuous curve census")
            self.assertEqual(row["identified_points"],
                             row["identified_points_exact_agreement"], row["universe"])
            checked += 1
        self.assertGreaterEqual(checked, 4, "too few truthful curve censuses")

    def test_ood_strata_are_reported_separately(self):
        ood = self.result["ood"]
        self.assertGreater(ood["ood_population"], 0)
        self.assertGreater(ood["input_ood_world_pairs"], 0)
        self.assertIn("out_of_universe_wrong_points", ood)
        self.assertIn("KP-1D", ood["attribution"])
        self.assertEqual(ood["in_universe_stratum"]["soundness_violations"], 0)
        self.assertGreater(ood["in_universe_stratum"]["input_world_pairs"], 0)
        self.assertGreater(ood["out_of_universe_stratum"]["input_world_pairs"], 0)

    def test_qualitative_modes_are_stratified_by_order_class(self):
        for row in self.result["universes"]:
            if row.get("status") != "SCORED":
                continue
            strata = row["qualitative_modes"]["by_order_stratum"]
            for key in ("ORDER_FREE", "CONJUNCTIVE", "NO_CROSSING"):
                self.assertIn(key, strata)
            self.assertGreater(strata["ORDER_FREE"]["agree"]
                               + strata["ORDER_FREE"]["disagree"], 0)

    def test_claim_ceiling_and_forbidden_promotions_are_pinned(self):
        self.assertTrue(self.result["claim_ceiling"].startswith("GMI_833_HELDOUT"))
        self.assertIn("NO_REWRITE_OF_PARENT_ROWS_KP1_KP2_KP3",
                      self.result["forbidden_promotions"])
        self.assertTrue(self.result["parent_blob_pin_ok"])
        self.assertTrue(self.result["freeze"]["parent_blob_matches_freeze"])


class RouteBIndependence(unittest.TestCase):
    def test_route_b_imports_nothing_from_this_package(self):
        with open(os.path.join(HERE, "oracle_route_b_v1.py")) as handle:
            tree = ast.parse(handle.read())
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.append(node.module or "")
        for name in names:
            self.assertNotIn("heldout_universes", name)
            self.assertNotIn("capability_predictor", name)
            self.assertNotIn("external_evaluator", name)
            self.assertNotIn("score_heldout", name)
            self.assertNotIn("freeze_predictions", name)

    def test_route_b_power_revival_simulators_agree(self):
        for machine in hx.SYN2_MACHINES:
            self.assertEqual(rb.solved_by_simulation(rb.sim_syn2, machine),
                             ev.measure_solved_bits(hx.syn2_machine_answer, machine))

    def test_route_b_simulators_agree_with_route_a(self):
        for machine in hu.SYN_MACHINES:
            self.assertEqual(rb.solved_by_simulation(rb.sim_syn, machine),
                             ev.measure_solved_bits(hu.syn_machine_answer, machine))
        for machine in hu.ARCH_MACHINES:
            self.assertEqual(rb.solved_by_simulation(rb.sim_arch, machine),
                             ev.measure_solved_bits(hu.arch_machine_answer, machine))


if __name__ == "__main__":
    unittest.main(verbosity=2)
