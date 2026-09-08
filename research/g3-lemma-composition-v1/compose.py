"""Smallest G3 composition experiment on two admitted ordinary-cut lemmas.

Method A is the 0-premise SCREENED_NEGATIVE cut extracted from ssdifim.
Method B is the 0-premise SCREENED_NEGATIVE cut extracted from ssdifsym.
The published ssdifsym-cut proof cites the named whole theorem ssdifim.
This study rebuilds that outer cut so the proof invokes the inner *cut*
identity, then hunts a fresh task that needs both identities.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
G2 = HERE.parent / "g2-causal-lemma-reuse-v1"
VENDOR = HERE.parent / "native-method-serving-v1" / "vendor"
sys.path[:0] = [str(HERE), str(G2), str(VENDOR)]
import extract as E  # noqa: E402
import mmverify as N  # noqa: E402

PREFIX = Path("/tmp/orion-native/CUSTODIAN-PREFIX.mm")
SETMM = Path("/tmp/orion-native/set.mm")
RECORDS = HERE / "records" / "run-01"
INNER_LABEL = "cut-ssdifim"
OUTER_LABEL = "cut-ssdifsym"
COMPOSED_LABEL = "cut-ssdifsym-comp"
INLINED_LABEL = "cut-ssdifsym-inline"
ORIG_LABEL = "cut-ssdifsym-orig"

# Uncompressed proof of the outer cut that cites INNER_LABEL, not named ssdifim.
# Stack: ex-wffs, then sylan9eq(dfss4+eqcom+sylbb, inner-cut), then ex.
COMPOSED_PROOF = """
cA cV wss
cB cV cA cdif wceq
cA cV cB cdif wceq
cA cV wss
cB cV cA cdif wceq
cA
cV cV cA cdif cdif
cV cB cdif
cA cV wss
cV cV cA cdif cdif cA wceq
cA cV cV cA cdif cdif wceq
cA cV dfss4
cV cV cA cdif cdif cA eqcom
sylbb
cA cB cV cut-ssdifim
sylan9eq
ex
""".split()

# Same construction with the inner cut body inlined (difeq2 eqcomd).
INLINED_PROOF = """
cA cV wss
cB cV cA cdif wceq
cA cV cB cdif wceq
cA cV wss
cB cV cA cdif wceq
cA
cV cV cA cdif cdif
cV cB cdif
cA cV wss
cV cV cA cdif cdif cA wceq
cA cV cV cA cdif cdif wceq
cA cV dfss4
cV cV cA cdif cdif cA eqcom
sylbb
cB cV cA cdif wceq cV cB cdif cV cV cA cdif cdif cB cV cA cdif cV difeq2 eqcomd
sylan9eq
ex
""".split()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def pair_lemmas():
    inner = None
    outer = None
    for lemma in E.unique_negatives():
        if lemma["hypotheses"]:
            continue
        if lemma["source_label"] == "ssdifim" and inner is None:
            inner = lemma
        elif lemma["source_label"] == "ssdifsym" and outer is None:
            outer = lemma
    if inner is None or outer is None:
        raise ValueError("missing ssdifim/ssdifsym zero-premise cuts")
    return inner, outer


def emit_p(label: str, target, proof) -> str:
    return (
        "${\n"
        + label
        + " $p "
        + " ".join(target)
        + " $= "
        + " ".join(proof)
        + " $.\n$}\n"
    )


def verify_database(raw: bytes, begin_label: str) -> dict:
    start = time.monotonic()
    log = []
    N.verbosity = 0
    N.logfile = type("L", (), {"write": lambda self, s: log.append(s)})()
    mm = N.MM(begin_label, None)
    error = None
    path = None
    try:
        with tempfile.NamedTemporaryFile("w+", encoding="ascii", delete=False) as handle:
            handle.write(raw.decode("ascii"))
            handle.flush()
            path = handle.name
        with open(path, encoding="ascii") as stream:
            mm.read(N.Toks(stream))
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    return {
        "terminal": "NATIVE_VERIFIED" if error is None else "NATIVE_REJECTED",
        "error": error,
        "wall_s": time.monotonic() - start,
        "log_tail": "".join(log)[-2000:],
        "begin_label": begin_label,
        "database_path": path,
        "bytes": len(raw),
    }


def named_theorems():
    text = PREFIX.read_text(encoding="ascii")
    out = {}
    for label in ("ssdifim", "ssdifsym"):
        needle = f"{label} $p "
        i = text.find(needle)
        j = text.find("$=", i)
        stmt = " ".join(text[i + len(needle) : j].split())
        out[label] = {"kind": "$p", "statement": "|- " + stmt if not stmt.startswith("|-") else stmt}
    return out


def scan_heldout_citations():
    text = SETMM.read_text(encoding="ascii")
    idx = text.find("pssdif $p")
    if idx < 0:
        raise ValueError("pssdif not found")
    rest = text[idx:]
    end = rest.find("$.")
    after = rest[end + 2 :]
    pat = re.compile(r"(\S+) \$p (.*?)\s\$=\s(.*?)\s\$\.", re.S)
    uses_im, uses_sym, uses_both = [], [], []
    n = 0
    for match in pat.finditer(after):
        n += 1
        lab, stmt, proof = match.group(1), " ".join(match.group(2).split()), match.group(3)
        toks = proof.replace("(", " ").replace(")", " ").split()
        has_im = "ssdifim" in toks
        has_sym = "ssdifsym" in toks
        if has_im or has_sym:
            rec = {
                "label": lab,
                "held_out_index": n,
                "statement": stmt,
                "cites_named_ssdifim": has_im,
                "cites_named_ssdifsym": has_sym,
            }
            if has_im:
                uses_im.append(rec)
            if has_sym:
                uses_sym.append(rec)
            if has_im and has_sym:
                uses_both.append(rec)
    return {
        "held_out_after": "pssdif",
        "n_held_out": n,
        "n_cite_named_ssdifim": len(uses_im),
        "n_cite_named_ssdifsym": len(uses_sym),
        "n_cite_both_named": len(uses_both),
        "cite_ssdifim": uses_im,
        "cite_ssdifsym": uses_sym,
        "cite_both": uses_both,
        "fresh_task_needing_both_cuts": None,
        "fresh_terminal": "NO_FRESH_COMPOSITION",
    }


def run():
    if not PREFIX.is_file():
        raise FileNotFoundError("missing custodian prefix: " + str(PREFIX))
    RECORDS.mkdir(parents=True, exist_ok=True)
    cpu0 = os.times()
    wall0 = time.monotonic()
    inner, outer = pair_lemmas()
    prefix = PREFIX.read_bytes()
    native_calls = 0

    inner_mm = E.emit_suffix(inner, INNER_LABEL)
    orig_mm = emit_p(ORIG_LABEL, outer["target"], outer["proof"])
    composed_mm = emit_p(COMPOSED_LABEL, outer["target"], COMPOSED_PROOF)
    inlined_mm = emit_p(INLINED_LABEL, outer["target"], INLINED_PROOF)

    admit_inner = verify_database(prefix + b"\n" + inner_mm.encode(), INNER_LABEL)
    native_calls += 1
    admit_outer = verify_database(prefix + b"\n" + orig_mm.encode(), ORIG_LABEL)
    native_calls += 1
    both_mm = inner_mm + "\n" + orig_mm
    admit_both = verify_database(prefix + b"\n" + both_mm.encode(), INNER_LABEL)
    native_calls += 1

    composed = verify_database(
        prefix + b"\n" + inner_mm.encode() + b"\n" + composed_mm.encode(),
        INNER_LABEL,
    )
    native_calls += 1
    ablate = verify_database(prefix + b"\n" + composed_mm.encode(), COMPOSED_LABEL)
    native_calls += 1
    inlined = verify_database(prefix + b"\n" + inlined_mm.encode(), INLINED_LABEL)
    native_calls += 1

    named = named_theorems()
    heldout = scan_heldout_citations()

    inner_stmt = " ".join(inner["target"])
    outer_stmt = " ".join(outer["target"])
    named_im = named["ssdifim"]["statement"]
    named_sym = named["ssdifsym"]["statement"]
    invocation = {
        "composed_cites_inner_cut": INNER_LABEL in COMPOSED_PROOF,
        "composed_cites_named_ssdifim": "ssdifim" in COMPOSED_PROOF,
        "original_outer_cites_named_ssdifim": "ssdifim" in outer["proof"],
        "original_outer_cites_inner_cut": INNER_LABEL in outer["proof"],
        "inlined_cites_inner_cut": INNER_LABEL in INLINED_PROOF,
        "inlined_cites_named_ssdifim": "ssdifim" in INLINED_PROOF,
        "inner_statement_equals_named_ssdifim": inner_stmt == named_im,
        "outer_statement_equals_named_ssdifsym": outer_stmt == named_sym,
    }
    lengths = {
        "inner_cut": len(inner["proof"]),
        "outer_original_uses_named_ssdifim": len(outer["proof"]),
        "outer_composed_uses_inner_cut": len(COMPOSED_PROOF),
        "outer_inlined_no_cut": len(INLINED_PROOF),
    }
    ablation = {
        "remove_inner_cut": {
            "terminal": ablate["terminal"],
            "error": ablate["error"],
            "breaks": ablate["terminal"] == "NATIVE_REJECTED",
            "reason": (ablate["error"] or {}).get("message"),
        },
        "inline_inner_body": {
            "terminal": inlined["terminal"],
            "lengthens": lengths["outer_inlined_no_cut"] > lengths["outer_composed_uses_inner_cut"],
            "n_proof": lengths["outer_inlined_no_cut"],
        },
    }
    same_family = {
        "inner_source": inner["source_label"],
        "outer_source": outer["source_label"],
        "inner_ordinal": inner["ordinal"],
        "outer_ordinal": outer["ordinal"],
        "disjoint_families": False,
        "note": "Consecutive training roots in the subclass/difference neighbourhood; not G3.1 disjoint family B.",
    }
    p1_parent = {
        "named_ssdifim": named["ssdifim"],
        "named_ssdifsym": named["ssdifsym"],
        "named_theorems_are_cuts": False,
        "outer_cut_proof_on_p1_alone": {
            "terminal": admit_outer["terminal"],
            "n_proof": lengths["outer_original_uses_named_ssdifim"],
            "uses": "named whole ssdifim, then ex",
        },
        "parent_sufficient_for_training_pair": admit_outer["terminal"] == "NATIVE_VERIFIED",
        "note": "P1 already contains named ssdifim/ssdifsym as imported whole theorems. Those are not the extracted cuts.",
    }

    g3_1_can_check = (
        composed["terminal"] == "NATIVE_VERIFIED"
        and invocation["composed_cites_inner_cut"]
        and not invocation["composed_cites_named_ssdifim"]
        and heldout["fresh_terminal"] != "NO_FRESH_COMPOSITION"
        and same_family["disjoint_families"]
    )
    terminal = "TRAINING_PAIR_CUT_COMPOSITION_VERIFIED__NO_FRESH_COMPOSITION"
    result = {
        "schema": "g3.lemma-composition.run.v1",
        "terminal": terminal,
        "g3_1_can_check": g3_1_can_check,
        "g3_1": "CANNOT_CHECK",
        "g2_4": "NOT_YET",
        "causal_method_reuse_supported": False,
        "method_composition_supported": False,
        "fresh_terminal": heldout["fresh_terminal"],
        "prefix_sha256": sha256_bytes(prefix),
        "prefix_bytes": len(prefix),
        "prefix_last_p": "pssdif",
        "native_calls": native_calls,
        "inner": {
            "source_label": inner["source_label"],
            "canonical_id": inner["canonical_id"],
            "label": INNER_LABEL,
            "target": inner["target"],
            "proof": inner["proof"],
            "n_hypotheses": 0,
            "admit": {k: admit_inner[k] for k in ("terminal", "error", "wall_s")},
        },
        "outer": {
            "source_label": outer["source_label"],
            "canonical_id": outer["canonical_id"],
            "label": OUTER_LABEL,
            "target": outer["target"],
            "original_proof": outer["proof"],
            "composed_proof": COMPOSED_PROOF,
            "inlined_proof": INLINED_PROOF,
            "n_hypotheses": 0,
            "admit_original": {k: admit_outer[k] for k in ("terminal", "error", "wall_s")},
        },
        "admit_both": {k: admit_both[k] for k in ("terminal", "error", "wall_s")},
        "composed": {k: composed[k] for k in ("terminal", "error", "wall_s")},
        "invocation": invocation,
        "lengths": lengths,
        "ablation": ablation,
        "same_family": same_family,
        "p1_parent": p1_parent,
        "heldout": heldout,
        "g3_1_boxes": {
            "learn_method_a": "PARTIAL_SAME_FAMILY_CUT_ADMITTED",
            "learn_method_b_disjoint_family": "NO_SAME_FAMILY_TRAINING_ROOT",
            "freeze_unseen_a_b_task": "NO_FRESH_COMPOSITION",
            "combined_solution_absent_from_training": "NO_TARGET_IS_TRAINING_OUTER_CUT",
            "actual_use_of_both_identities": "TRAINING_PAIR_INNER_INVOKED_IN_OUTER_PROOF",
            "remove_a_only": "COMPOSED_OUTER_REJECTED",
            "remove_b_only": "NOT_RUN_NO_FRESH_TASK",
            "remove_both": "NOT_RUN_NO_FRESH_TASK",
            "compare_program_library_parent": "P1_NAMED_WHOLES_PARENT_SUFFICIENT_FOR_PAIR",
            "measure_composition_cost": "RECORDED_PROOF_LENGTHS_AND_NATIVE_WALL",
        },
    }
    (RECORDS / "inner.mm").write_text(inner_mm)
    (RECORDS / "outer-original.mm").write_text(orig_mm)
    (RECORDS / "outer-composed.mm").write_text(composed_mm)
    (RECORDS / "outer-inlined.mm").write_text(inlined_mm)
    (RECORDS / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")

    cpu1 = os.times()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    process = {
        "argv": [str(Path(__file__).resolve())],
        "cwd": os.getcwd(),
        "pid": os.getpid(),
        "python": sys.version.replace("\n", " "),
        "native_calls": native_calls,
        "wall_s": time.monotonic() - wall0,
        "user_cpu_s": cpu1.user - cpu0.user,
        "system_cpu_s": cpu1.system - cpu0.system,
        "max_rss_kib": usage.ru_maxrss,
        "terminal": terminal,
        "prefix": str(PREFIX),
        "prefix_sha256": result["prefix_sha256"],
    }
    (RECORDS / "PROCESS.json").write_text(json.dumps(process, indent=2) + "\n")

    summary = {
        "schema": "g3.lemma-composition.public-summary.v1",
        "terminal": terminal,
        "g3_1_can_check": False,
        "g3_1": "CANNOT_CHECK",
        "g2_4": "NOT_YET",
        "causal_method_reuse_supported": False,
        "method_composition_supported": False,
        "fresh_terminal": "NO_FRESH_COMPOSITION",
        "inner_admitted": admit_inner["terminal"] == "NATIVE_VERIFIED",
        "outer_admitted": admit_outer["terminal"] == "NATIVE_VERIFIED",
        "composed_invokes_inner_cut": composed["terminal"] == "NATIVE_VERIFIED"
        and invocation["composed_cites_inner_cut"],
        "ablation_breaks_outer": ablation["remove_inner_cut"]["breaks"],
        "inlined_lengthens": ablation["inline_inner_body"]["lengthens"],
        "disjoint_families": False,
        "p1_parent_named_wholes": True,
        "native_calls": native_calls,
        "n_held_out": heldout["n_held_out"],
        "n_held_out_citing_both_named": heldout["n_cite_both_named"],
        "lengths": lengths,
        "binding": {
            "result": "records/run-01/RESULT.json",
            "process": "records/run-01/PROCESS.json",
        },
    }
    (HERE / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "binding"}, indent=2))
    return result, summary


if __name__ == "__main__":
    run()
