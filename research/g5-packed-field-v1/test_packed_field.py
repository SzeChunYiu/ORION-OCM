"""G5.2 packed physical field: semantic parity, COW, indexes, deltas, bitmaps."""
from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SRC = REPO / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from ocm.kso.nogoods import register_constraint_nogood
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile

from packed_space import PackedKnowledgeSpace, python_space_bytes


def _space() -> KnowledgeSpace:
    a = Atom(
        "a",
        "claim",
        WarrantProfile.of({0}).join(WarrantProfile.of({1})),
        Authority.of(commit=1, lab=2),
        Scope.of("lab", "public"),
        epoch=3,
        content_ref="blob:a",
        meta=(("src", "gen"),),
    )
    b = Atom(
        "b",
        "procedure",
        WarrantProfile.of({0}).meet(WarrantProfile.of({1})),
        Authority.of(lab=2),
        Scope.of("lab"),
        epoch=1,
        content_ref="blob:b",
    )
    c = Atom("c", "claim", WarrantProfile.partial([{2}]), quarantined=False)
    d = Atom("d", "claim", WarrantProfile.of({1}), quarantined=True)
    e = Atom("e", "observation", WarrantProfile.one(), epoch=9)
    z = Atom("z", "constraint", WarrantProfile.zero())
    edges = (
        Hyperedge("ab", ("a",), ("b",), "DEPENDENCE", Fraction(2, 1), (Fraction(1, 1),), warrant=WarrantProfile.of({0})),
        Hyperedge("cd", ("c",), ("d",), "CONSTRAINT", warrant=WarrantProfile.one()),
        Hyperedge(
            "aeb",
            ("a", "e"),
            ("b",),
            "SUPPORT",
            Fraction(3, 2),
            warrant=WarrantProfile.certified([{0, 1}]),
            executable_ref="phi:aeb",
        ),
    )
    return KnowledgeSpace((a, b, c, d, e, z), edges)


def _revocations():
    evidence = (0, 1, 2)
    out = [()]
    for r in range(1, 4):
        out.extend(combinations(evidence, r))
    return out


class TestRoundTripIdentity(unittest.TestCase):
    def test_digest_and_as_dict_round_trip(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        back = packed.to_reference()
        self.assertEqual(back.digest(), ks.digest())
        self.assertEqual([a.as_dict() for a in back.atoms], [a.as_dict() for a in ks.atoms])
        self.assertEqual([e.as_dict() for e in back.hyperedges], [e.as_dict() for e in ks.hyperedges])
        self.assertEqual(packed.digest(), ks.digest())
        again = PackedKnowledgeSpace.from_reference(back)
        self.assertEqual(again.incremental_identity(), packed.incremental_identity())

    def test_stable_integer_handles(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        ha = packed.handle_of("a")
        hb = packed.handle_of("b")
        self.assertIsInstance(ha, int)
        self.assertNotEqual(ha, hb)
        patched = packed.replace_atom(Atom("a", "claim", WarrantProfile.of({0}), epoch=4))
        self.assertEqual(patched.handle_of("a"), ha)
        self.assertIs(patched.intern, packed.intern)

    def test_incident_and_outgoing_match_reference(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        for atom in ks.ids:
            self.assertEqual(
                [e.edge_id for e in packed.incident_edges(atom)],
                [e.edge_id for e in ks.incident_edges(atom)],
            )
            self.assertEqual(
                [e.edge_id for e in packed.outgoing_edges(atom)],
                [e.edge_id for e in ks.outgoing_edges(atom)],
            )

    def test_edits_match_reference(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        extra = Atom("f", "claim", WarrantProfile.of({2}), content_ref="blob:f")
        edge = Hyperedge("bf", ("b",), ("f",), "DEPENDENCE")
        ks2 = ks.with_atoms(extra).with_edges(edge)
        p2 = packed.with_atoms(extra).with_edges(edge)
        self.assertEqual(p2.to_reference().digest(), ks2.digest())
        replaced = Atom("b", "procedure", WarrantProfile.zero(), epoch=7)
        self.assertEqual(p2.replace_atom(replaced).digest(), ks2.replace_atom(replaced).digest())
        self.assertEqual(p2.without(("d",), ()).digest(), ks2.without(("d",), ()).digest())


class TestCOWSharing(unittest.TestCase):
    def test_replace_shares_intern_and_base_columns(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        patched = packed.replace_atom(Atom("c", "claim", WarrantProfile.of({2}), epoch=5, content_ref="blob:c"))
        self.assertIs(patched.intern, packed.intern)
        self.assertIs(patched.intern.types, packed.intern.types)
        self.assertIs(patched.intern.relations, packed.intern.relations)
        self.assertIs(patched.intern.payloads, packed.intern.payloads)
        self.assertIs(patched.atom_type_ids, packed.atom_type_ids)
        self.assertIs(patched.edge_relation_ids, packed.edge_relation_ids)
        self.assertIs(patched.tail_idx, packed.tail_idx)
        self.assertIn(patched.slot_of("c"), patched.atom_deltas)
        self.assertNotEqual(id(patched.atom_deltas), id(packed.atom_deltas))
        self.assertEqual(patched.version, packed.version + 1)
        self.assertEqual(patched.atom("c").epoch, 5)
        self.assertEqual(packed.atom("c").epoch, 0)

    def test_append_clones_dirty_atom_columns_shares_edges_and_intern(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        extra = Atom("g", "model", WarrantProfile.one())
        grown = packed.with_atoms(extra)
        self.assertIs(grown.intern, packed.intern)
        self.assertIsNot(grown.atom_type_ids, packed.atom_type_ids)
        self.assertIs(grown.edge_relation_ids, packed.edge_relation_ids)
        self.assertIs(grown.tail_idx, packed.tail_idx)
        self.assertEqual(grown.n_atoms, packed.n_atoms + 1)


class TestVersionIndexes(unittest.TestCase):
    def test_indexes_bound_to_version_and_incremental_identity(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        idx0 = packed.indexes()
        self.assertEqual(idx0.version, packed.version)
        self.assertTrue(idx0.usable_for(packed.version, packed.n_atoms, packed.n_edges))
        patched = packed.replace_atom(Atom("a", "observation", WarrantProfile.of({0})))
        idx1 = patched.indexes()
        self.assertEqual(idx1.version, patched.version)
        self.assertTrue(idx1.patched)
        self.assertFalse(idx0.usable_for(patched.version, patched.n_atoms, patched.n_edges))
        rebuilt = PackedKnowledgeSpace.from_reference(patched.to_reference())
        self.assertEqual(patched.incremental_identity(), rebuilt.incremental_identity())
        self.assertNotEqual(packed.incremental_identity(), patched.incremental_identity())
        bitmap = patched.atoms_of_type("observation", method="bitmap")
        self.assertIn("a", bitmap.atom_ids)
        self.assertEqual(
            set(patched.atoms_of_type("observation", method="linear").atom_ids),
            set(bitmap.atom_ids),
        )


class TestRevocationParity(unittest.TestCase):
    def test_liveness_join_meet_partial_vs_reference(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        checks = 0
        for revoked in _revocations():
            self.assertEqual(packed.live_atoms(revoked), ks.live_atoms(revoked), revoked)
            self.assertEqual(packed.dead_atoms(revoked), ks.dead_atoms(revoked), revoked)
            self.assertEqual(packed.unknown_atoms(revoked), ks.unknown_atoms(revoked), revoked)
            for edge in ks.hyperedges:
                self.assertEqual(
                    packed.edge_enabled_liveness(edge, revoked),
                    ks.edge_enabled_liveness(edge, revoked),
                    (edge.edge_id, revoked),
                )
            checks += 1
        self.assertEqual(checks, 8)
        self.assertEqual(packed.evidence_universe(), ks.evidence_universe())

    def test_constraint_nogoods_match_reference_filter(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        left = ks.atom("c").warrant
        right = ks.atom("d").warrant
        ng_ref = register_constraint_nogood(left, right)
        ng_packed = packed.constraint_nogoods()
        self.assertTrue(set(ng_ref.nogoods) <= set(ng_packed.nogoods))
        for revoked in _revocations():
            for atom_id in ks.ids:
                self.assertEqual(
                    packed.filtered_liveness(atom_id, revoked, ng_ref),
                    ng_ref.liveness(ks.atom(atom_id).warrant, revoked),
                    (atom_id, revoked),
                )


class TestBitmapVsLinear(unittest.TestCase):
    def test_type_scan_both_costs_counted(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        bitmap = packed.atoms_of_type("claim", method="bitmap")
        linear = packed.atoms_of_type("claim", method="linear")
        self.assertEqual(set(bitmap.atom_ids), set(linear.atom_ids))
        self.assertEqual(set(bitmap.atom_ids), {"a", "c", "d"})
        self.assertGreater(linear.units_touched, 0)
        self.assertGreater(bitmap.units_touched, 0)
        self.assertEqual(linear.units_touched, packed.n_atoms)
        self.assertEqual(linear.hits, bitmap.hits)
        self.assertLessEqual(bitmap.units_touched, linear.units_touched)


class TestLocalDelta(unittest.TestCase):
    def test_single_atom_patch_smaller_than_snapshot(self) -> None:
        packed = PackedKnowledgeSpace.from_reference(_space())
        snapshot = packed.snapshot_bytes()
        patched = packed.replace_atom(Atom("e", "observation", WarrantProfile.of({2}), content_ref="blob:e2"))
        self.assertGreater(patched.delta_bytes(), 0)
        self.assertLess(patched.delta_bytes(), patched.snapshot_bytes())
        self.assertLess(patched.delta_bytes(), snapshot)
        self.assertIs(patched.atom_type_ids, packed.atom_type_ids)
        self.assertEqual(patched.to_reference().atom("e").content_ref, "blob:e2")
        self.assertEqual(packed.to_reference().atom("e").content_ref, None)

    def test_python_object_bytes_are_counted(self) -> None:
        ks = _space()
        packed = PackedKnowledgeSpace.from_reference(ks)
        py_bytes = python_space_bytes(ks)
        self.assertGreater(py_bytes, 0)
        self.assertGreater(packed.column_bytes(), 0)
        self.assertGreater(packed.intern.payload_blob_bytes(), 0)


if __name__ == "__main__":
    unittest.main()
