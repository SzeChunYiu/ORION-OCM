"""Scan set.mm after pssdif; capture official proofs without verifying them."""
import hashlib
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "native-method-serving-v1" / "vendor"
sys.path[:0] = [str(VENDOR), str(Path(__file__).resolve().parent)]
import mmverify as N  # noqa: E402

PREFIX = Path("/tmp/orion-native/CUSTODIAN-PREFIX.mm")
SETMM = Path("/tmp/orion-native/set.mm")
PREFIX_SHA256 = "b12e2bac9f6fe8a6fda972d74dbfb21c2e85cd86040fd447c685c693ae0af1cd"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _silence():
    N.verbosity = 0
    N.logfile = type("L", (), {"write": lambda self, s: None})()


def capture_database(path):
    """Parse a Metamath file with proof verification off; keep each $p proof."""
    _silence()
    last = {}
    proofs = {}
    orig_rp = N.MM.read_p_stmt
    orig_make = N.FrameStack.make_assertion

    def rp(self, toks):
        stmt, proof = orig_rp(self, toks)
        last["stmt"] = stmt
        last["proof"] = proof
        return stmt, proof

    def make(self, stmt):
        result = orig_make(self, stmt)
        dvs, f_hyps, e_hyps, conclusion = result
        last["f_labels"] = [self.lookup_f(v) for _, v in f_hyps]
        last["e_labels"] = [self.lookup_e(s) for s in e_hyps]
        last["n_floating"] = len(f_hyps)
        last["n_essential"] = len(e_hyps)
        last["dvs_all"] = [(x, y) for fr in self for (x, y) in fr.d]
        return result

    class Lab(dict):
        def __setitem__(self, key, value):
            if value and value[0] == "$p":
                proofs[key] = {
                    "label": key,
                    "statement": list(last.get("stmt") or []),
                    "proof": list(last.get("proof") or []),
                    "f_labels": list(last.get("f_labels") or []),
                    "e_labels": list(last.get("e_labels") or []),
                    "n_floating": last.get("n_floating", 0),
                    "n_essential": last.get("n_essential", 0),
                    "dvs_all": list(last.get("dvs_all") or []),
                    "assertion": value[1],
                }
            dict.__setitem__(self, key, value)

    N.MM.read_p_stmt = rp
    N.FrameStack.make_assertion = make
    try:
        mm = N.MM("__never_begin__", None)
        mm.labels = Lab()
        with open(path, encoding="ascii") as handle:
            mm.read(N.Toks(handle))
        return mm, proofs
    finally:
        N.MM.read_p_stmt = orig_rp
        N.FrameStack.make_assertion = orig_make


def index_kinds_arities(mm):
    kinds = {}
    arities = {}
    floating_counts = {}
    semantic = set()
    for label, info in mm.labels.items():
        kind = info[0]
        kinds[label] = kind
        if kind in ("$f", "$e"):
            arities[label] = 0
            continue
        dvs, f_hyps, e_hyps, conclusion = info[1]
        arities[label] = len(f_hyps) + len(e_hyps)
        floating_counts[label] = len(f_hyps)
        if conclusion and conclusion[0] == "|-":
            semantic.add(label)
    return kinds, arities, floating_counts, semantic


def prefix_assertion_labels(proofs_in_order, cut="pssdif"):
    seen = set()
    for label in proofs_in_order:
        seen.add(label)
        if label == cut:
            break
    else:
        raise ValueError("missing pssdif")
    return seen


def used_assertions(row, kinds):
    proof = row["proof"]
    if not proof:
        return []
    if proof[0] == "(":
        idx = proof.index(")")
        names = list(proof[1:idx])
    else:
        names = list(proof)
    return [n for n in names if kinds.get(n) in ("$a", "$p")]


def heldout_rows(proofs, order, prefix_ps, kinds):
    started = False
    rows = []
    for label in order:
        if not started:
            if label == "pssdif":
                started = True
            continue
        row = proofs[label]
        used = used_assertions(row, kinds)
        rows.append({
            "label": label,
            "statement": row["statement"],
            "n_essential": row["n_essential"],
            "used": used,
            "p1_closed": all(n in prefix_ps for n in used),
            "proof": row["proof"],
            "f_labels": row["f_labels"],
            "e_labels": row["e_labels"],
            "dvs_all": row.get("dvs_all") or [],
            "assertion": row.get("assertion"),
        })
    return rows
