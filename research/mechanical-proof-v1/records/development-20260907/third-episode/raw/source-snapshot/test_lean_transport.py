"""Transport controls exercise actual rendering; no arbitrary Lean source accepted."""
import unittest
from lean_transport import render_term, audit_axioms

class TransportTests(unittest.TestCase):
    def test_closed_identity_uses_scoped_generated_binders(self):
        term = ["lam", ["sort", 1], ["lam", ["var", 0], ["var", 0]]]
        self.assertEqual(render_term(term), "(fun (v0 : (Sort 1)) => (fun (v1 : v0) => v1))")

    def test_debruijn_reference_does_not_capture_outer_binder(self):
        term = ["lam", ["sort", 1], ["lam", ["sort", 1], ["var", 1]]]
        self.assertTrue(render_term(term).endswith("=> v0))"))

    def test_registered_constants_have_trusted_explicit_names(self):
        self.assertEqual(render_term(["const", 0]), "(@Eq.{1})")
        self.assertIn("@MEFoundation.agreement_sound", render_term(["const", 1]))

    def test_forbidden_code_and_leaked_constant_are_refused(self):
        for bad in [["raw", "by sorry"], ["const", 3], ["const", "OCMProofReplay.refinement_then_sound"],
                    ["var", 0], ["sort", True], ["sort", -1], ["sort", 3],
                    ["app", ["const", 0]], ["lam", ["var", 0], ["var", 0]],
                    {"tag": "const", "id": 0}, ["const", 0, "extra"]]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): render_term(bad)

    def test_resource_bounds_refuse_truncated_candidate(self):
        term = ["lam", ["sort", 1], ["lam", ["var", 0], ["var", 0]]]
        for limits in [{"max_nodes": 2}, {"max_depth": 1}]:
            with self.subTest(limits=limits), self.assertRaises(ValueError): render_term(term, **limits)

    def test_pi_and_application_render_without_free_text(self):
        term = ["lam", ["sort", 1], ["pi", ["var", 0], ["app", ["const", 0], ["var", 1]]]]
        text = render_term(term)
        self.assertIn("forall (v1 : v0)", text)
        self.assertIn("(@Eq.{1} v0)", text)

    def test_axiom_empty_and_permitted_reports(self):
        self.assertEqual(audit_axioms("'M.proof' does not depend on any axioms\n", "M.proof"), [])
        self.assertEqual(audit_axioms("'M.proof' depends on axioms: [propext, Classical.choice]\n", "M.proof"), ["Classical.choice", "propext"])

    def test_axiom_audit_rejects_missing_duplicate_extra_or_injected(self):
        good = "'M.proof' does not depend on any axioms\n"
        for bad in ["", good + good, good + "'Other.proof' does not depend on any axioms\n",
                    "'M.proof' depends on axioms: [sorryAx]\n", "'M.proof' depends on axioms: [custom]\n",
                    "'M.proof' depends on axioms: [propext] trailing\n", "'M.proof' depends on axioms: [propext, propext]\n", "'M.proof' depends on axioms: [, ]\n", "'M.proof' depends on axioms: [propext,,]\n"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): audit_axioms(bad, "M.proof")

if __name__ == "__main__": unittest.main()
