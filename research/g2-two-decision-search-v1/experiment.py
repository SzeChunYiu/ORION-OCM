"""G2.4 two-decision / REFACTOR experiment. Not 1-step conclusion matching."""
import json
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
VENDOR = HERE.parent / "native-method-serving-v1" / "vendor"
sys.path[:0] = [str(HERE), str(VENDOR),
                str(HERE.parent / "g2-heldout-lemma-screen-v1" / "successor")]

import dag as D  # noqa: E402
import load_inputs as L  # noqa: E402
import mm_scan as M  # noqa: E402
import mmverify as N  # noqa: E402
import search_arms as S  # noqa: E402

LEMMAS_PATH = HERE.parent / "g2-heldout-lemma-screen-v1" / "records" / "replay-01" / "producer-01" / "LEMMAS.json"
RECORDS = HERE / "records" / "replay-01"
ACQUISITION = {
    "inss", "symdifeq1", "elsymdif", "ssdifim", "ssdifsym", "indif1",
    "indir", "undir", "indifdir", "dif32", "sscon34b",
}


def alpha_key(toks):
    mapping = {}
    out = []
    for tok in toks:
        if tok in S.CLASS_ATOMS or (tok.startswith("V") and tok[1:].isdigit()):
            if tok not in mapping:
                mapping[tok] = "C" + str(len(mapping))
            out.append(mapping[tok])
        else:
            out.append(tok)
    return tuple(out)


def load_lemmas():
    data = json.loads(LEMMAS_PATH.read_text())
    lemmas = data["lemmas"]
    if len(lemmas) != 22:
        raise ValueError("expected 22 compiled cuts")
    for lemma in lemmas:
        lemma["getsteps"] = D.lemma_steps(lemma["proof"])
        lemma["spine"] = list(lemma["semantic_labels"])
        if len(lemma["spine"]) != 2:
            raise ValueError("not a 2-step DAG: " + lemma["label"])
    return lemmas


def native_check(row, prefix_bytes):
    dvs, f_hyps, e_hyps, conclusion = row["assertion"]
    lines = ["${"]
    pairs = row.get("dvs_all") or sorted(dvs)
    for a, b in sorted(set(tuple(p) for p in pairs)):
        lines.append("$d " + a + " " + b + " $.")
    for lab, eh in zip(row["e_labels"], e_hyps):
        lines.append(lab + " $e " + " ".join(eh) + " $.")
    lines.append(row["label"] + " $p " + " ".join(row["statement"])
                 + " $= " + " ".join(row["proof"]) + " $.")
    lines.append("$}")
    raw = prefix_bytes + b"\n" + "\n".join(lines).encode("ascii") + b"\n"
    N.verbosity = 0
    N.logfile = type("L", (), {"write": lambda self, s: None})()
    mm = N.MM(row["label"], None)
    t0 = time.monotonic()
    error = None
    try:
        import tempfile
        with tempfile.NamedTemporaryFile("w+", encoding="ascii", delete=False) as handle:
            handle.write(raw.decode("ascii"))
            handle.flush()
            path = handle.name
        with open(path, encoding="ascii") as stream:
            mm.read(N.Toks(stream))
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)[:300]}
    return {
        "terminal": "NATIVE_VERIFIED" if error is None else "NATIVE_REJECTED",
        "error": error,
        "wall_s": time.monotonic() - t0,
    }


def build_tree(row, kinds, arities, floating_counts):
    proof = row["proof"]
    if not proof:
        raise ValueError("empty proof")
    if proof[0] == "(":
        return D.expand_compressed(
            proof, row["f_labels"], row["e_labels"],
            arities, kinds, floating_counts,
        )
    return D.tree_from_rpn(proof, arities, kinds, floating_counts)


def refactor_heldout(lemmas, held, kinds, arities, floating_counts):
    spines = [(lemma["label"], tuple(lemma["spine"]), lemma["getsteps"]) for lemma in lemmas]
    rows = []
    n_tree_ok = 0
    n_tree_fail = 0
    for theorem in held:
        if not theorem["p1_closed"]:
            continue
        used = set(theorem["used"])
        relevant = [s for s in spines if s[1][0] in used and s[1][1] in used]
        if not relevant:
            continue
        try:
            root = build_tree(theorem, kinds, arities, floating_counts)
            n_tree_ok += 1
        except Exception as exc:
            n_tree_fail += 1
            rows.append({
                "label": theorem["label"],
                "error": type(exc).__name__ + ": " + str(exc)[:160],
                "hits": [],
            })
            continue
        hits = []
        for name, spine, steps in relevant:
            for hit in D.match_semantic_spine(root, list(spine)):
                hit = dict(hit)
                hit["lemma"] = name
                hit["spine"] = list(spine)
                hits.append(hit)
            for hit in D.match_getsteps(root, steps):
                hit = dict(hit)
                hit["lemma"] = name
                hits.append(hit)
        if hits:
            rows.append({
                "label": theorem["label"],
                "statement": theorem["statement"],
                "n_essential": theorem["n_essential"],
                "p1_closed": True,
                "used": theorem["used"],
                "hits": hits,
                "n_proper_spine": sum(1 for h in hits if h.get("kind") == "semantic_spine" and h.get("proper_subtree")),
                "n_whole_spine": sum(1 for h in hits if h.get("kind") == "semantic_spine" and not h.get("proper_subtree")),
                "n_proper_getsteps": sum(1 for h in hits if h.get("kind") == "getsteps" and h.get("proper_subtree")),
            })
    return {
        "n_prefilter_tree_ok": n_tree_ok,
        "n_prefilter_tree_fail": n_tree_fail,
        "theorems": rows,
    }


def is_lemma_identity(statement, lemmas):
    key = alpha_key(statement)
    return any(alpha_key(lemma["statement"]) == key for lemma in lemmas)


def search_targets(held, refactor_rows, lemmas, limit=6):
    targets = []
    seen = set()
    for row in refactor_rows:
        if row.get("n_proper_spine", 0) <= 0:
            continue
        if row["label"] in ACQUISITION or is_lemma_identity(row["statement"], lemmas):
            continue
        seen.add(row["label"])
        targets.append(row["label"])
        if len(targets) >= limit:
            return targets
    for theorem in held:
        if not theorem["p1_closed"] or theorem["label"] in seen:
            continue
        if theorem["label"] in ACQUISITION or is_lemma_identity(theorem["statement"], lemmas):
            continue
        targets.append(theorem["label"])
        if len(targets) >= limit:
            break
    return targets


def run_search(p1, lemma_rows, held_by_label, labels, max_decisions_list):
    matcher = S.extend_class_syntax()
    out = []
    invocations = 0
    for lab in labels:
        theorem = held_by_label[lab]
        goal = list(theorem["statement"])
        bank = S.bank_from(goal, lemma_rows)
        task = {"query": goal, "premises": [list(p) for p in (theorem.get("assertion") or (None, None, [], None))[2]]}
        # Search is on the conclusion; local $e are premises if present.
        dvs_f_e_c = theorem.get("assertion")
        premises = []
        if dvs_f_e_c:
            premises = [list(p) for p in dvs_f_e_c[2]]
        task = {"query": goal, "premises": premises}
        # Premises must be in the bank.
        extra = [p[1:] if p and p[0] == "|-" else p for p in premises]
        bank = S.bank_from(goal, lemma_rows, extra_wffs=extra)
        ordinary = S.ordinary_parent_rows(lemma_rows)
        parents = {
            "P1": p1,
            "P1_lemmas": p1 + ordinary,
            "ordinary_parent": p1 + ordinary,
        }
        for md in max_decisions_list:
            rec = {"label": lab, "max_decisions": md, "bank_n": len(bank["wff"]),
                   "bank_kind": bank["kind"], "matcher": matcher, "arms": {}}
            # Ablation: compile with lemmas (charged) then search P1 only.
            t0 = time.monotonic()
            compile_work = {}
            S.FS.compile_parent(p1 + ordinary, bank, compile_work, limit=50000)
            rec["ablation_compile"] = {
                "primitive_instances": compile_work.get("primitive_instances", 0),
                "wall_s": time.monotonic() - t0,
            }
            for arm_name, parent in parents.items():
                t1 = time.monotonic()
                try:
                    result = S.search_arm(parent, bank, task, max_decisions=md)
                    invocations += 1
                    result["wall_s"] = time.monotonic() - t1
                except Exception as exc:
                    result = {
                        "terminal": "ERROR",
                        "error": type(exc).__name__ + ": " + str(exc)[:200],
                        "wall_s": time.monotonic() - t1,
                    }
                    invocations += 1
                rec["arms"][arm_name] = result
            t2 = time.monotonic()
            try:
                result = S.search_arm(p1, bank, task, max_decisions=md)
                invocations += 1
                result["wall_s"] = time.monotonic() - t2
            except Exception as exc:
                result = {
                    "terminal": "ERROR",
                    "error": type(exc).__name__ + ": " + str(exc)[:200],
                    "wall_s": time.monotonic() - t2,
                }
                invocations += 1
            rec["arms"]["ablation"] = result
            out.append(rec)
    return out, invocations


def summarize(lemmas, held, refactor, native_hits, searches, invocations, prefix_sha, walls):
    proper_proofs = [t for t in refactor["theorems"] if t.get("n_proper_spine", 0) > 0]
    whole_only = [t for t in refactor["theorems"]
                  if t.get("n_whole_spine", 0) > 0 and t.get("n_proper_spine", 0) == 0]
    n_proper = len(proper_proofs)
    native_ok = {r["label"] for r in native_hits if r.get("terminal") == "NATIVE_VERIFIED"}
    n_proper_verified = sum(1 for t in proper_proofs if t["label"] in native_ok)
    sav = D.save_value(n_proper_verified, semantic_size=2)
    lemma_used = []
    for rec in searches:
        for arm, result in rec.get("arms", {}).items():
            if result.get("used_cut_lemma") and result.get("terminal") == "PROVED":
                lemma_used.append({
                    "goal": rec["label"],
                    "arm": arm,
                    "max_decisions": rec["max_decisions"],
                    "used": result["used_cut_lemma"],
                    "decision_count": result.get("decision_count"),
                    "mooney_once": result.get("mooney_once"),
                })
    lemma_actions_any = any(
        (result.get("lemma_actions") or 0) > 0
        for rec in searches for result in rec.get("arms", {}).values()
    )
    positive = n_proper_verified > 0
    if lemma_used:
        terminal = "LEMMA_USED_IN_FINITE_SEARCH"
        g24 = "CAN_CHECK_POSITIVE"
    elif positive:
        terminal = "REFACTOR_PROPER_SUBTREE_CONSUMPTION"
        g24 = "CAN_CHECK_POSITIVE_ON_REFACTOR_CONSUMER"
    elif sav["terminal"] == "NO_RECURRENCE":
        terminal = "NO_RECURRENCE"
        g24 = "CANNOT_CHECK_POSITIVE"
    else:
        terminal = sav["terminal"]
        g24 = "CANNOT_CHECK_POSITIVE"
    return {
        "schema": "g2.two-decision-search.summary.v1",
        "terminal": terminal,
        "g2_4": g24,
        "causal_method_reuse_supported": bool(lemma_used),
        "n_compiled_dags": len(lemmas),
        "n_held_out": len(held),
        "n_p1_closed": sum(1 for t in held if t["p1_closed"]),
        "n_refactored_proofs_proper": n_proper,
        "n_refactored_proofs_proper_native": n_proper_verified,
        "n_whole_proof_spine_only": len(whole_only),
        "n_getsteps_proper": sum(t.get("n_proper_getsteps", 0) for t in refactor["theorems"]),
        "save_value": sav,
        "search_invocations": invocations,
        "lemma_used_in_search": lemma_used,
        "lemma_actions_nonzero": lemma_actions_any,
        "native_hit_checks": native_hits,
        "prefix_sha256": prefix_sha,
        "native_22_22": "PR179_GIVEN",
        "parents": [
            "Mooney IJCAI 1989 limited chaining",
            "Kaliszyk Urban JSC 2015 later-theorem with vs without",
            "Zhou et al. ICLR 2024 REFACTOR subroutine ADOPT / neural REJECT",
            "Wernhard 2025/2026 save-value",
        ],
        "walls": walls,
        "one_step_identity_excluded": True,
        "github_g2_4_checked": False,
    }


def main():
    RECORDS.mkdir(parents=True, exist_ok=True)
    walls = {}
    t0 = time.monotonic()
    prefix_sha = M.sha256(M.PREFIX)
    if prefix_sha != M.PREFIX_SHA256:
        raise ValueError("PREFIX pin mismatch: " + prefix_sha)
    lemmas = load_lemmas()
    p1 = [row for row in L.load_p1() if row.get("statement", [""])[0] == "|-"]
    lemma_rows = S.lemma_contracts(lemmas)
    walls["load"] = time.monotonic() - t0

    t1 = time.monotonic()
    print("parsing set.mm (verify off)", flush=True)
    mm_p, proofs_p = M.capture_database(M.PREFIX)
    prefix_ps = set(proofs_p) | {lab for lab, info in mm_p.labels.items() if info[0] == "$a"}
    mm, proofs = M.capture_database(M.SETMM)
    kinds, arities, floating_counts, _semantic = M.index_kinds_arities(mm)
    order = list(proofs)
    held = M.heldout_rows(proofs, order, prefix_ps, kinds)
    walls["scan"] = time.monotonic() - t1
    print("held-out", len(held), "p1-closed", sum(1 for t in held if t["p1_closed"]), flush=True)

    t2 = time.monotonic()
    refactor = refactor_heldout(lemmas, held, kinds, arities, floating_counts)
    walls["refactor"] = time.monotonic() - t2
    print("refactor theorems with any hit", len(refactor["theorems"]),
          "tree_ok", refactor["n_prefilter_tree_ok"], flush=True)

    prefix_bytes = M.PREFIX.read_bytes()
    native_hits = []
    held_by_label = {t["label"]: t for t in held}
    for row in refactor["theorems"]:
        if row.get("n_proper_spine", 0) <= 0 and row.get("n_whole_spine", 0) <= 0:
            continue
        full = held_by_label[row["label"]]
        native_hits.append({"label": row["label"], **native_check(full, prefix_bytes)})
        print("native", row["label"], native_hits[-1]["terminal"], flush=True)
        if len(native_hits) >= 12:
            break

    t3 = time.monotonic()
    targets = search_targets(held, refactor["theorems"], lemmas)
    print("search targets", targets, flush=True)
    searches, invocations = run_search(p1, lemma_rows, held_by_label, targets, [2, 3])
    walls["search"] = time.monotonic() - t3
    walls["total"] = time.monotonic() - t0

    summary = summarize(lemmas, held, refactor, native_hits, searches, invocations, prefix_sha, walls)
    payload = {
        "summary": summary,
        "lemmas": [{"label": x["label"], "source": x["source_label"],
                    "spine": x["spine"], "getsteps": x["getsteps"],
                    "zero_premise": not x["essential"]} for x in lemmas],
        "heldout_head": [t["label"] for t in held[:12]],
        "refactor": {
            "n_theorems_with_hit": len(refactor["theorems"]),
            "n_prefilter_tree_ok": refactor["n_prefilter_tree_ok"],
            "n_prefilter_tree_fail": refactor["n_prefilter_tree_fail"],
            "theorems": refactor["theorems"][:80],
        },
        "native_hits": native_hits,
        "searches": searches,
        "targets": targets,
    }
    (RECORDS / "RESULT.json").write_text(json.dumps(payload, indent=2) + "\n")
    (HERE / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in (
        "terminal", "g2_4", "n_held_out", "n_p1_closed",
        "n_refactored_proofs_proper", "n_refactored_proofs_proper_native",
        "search_invocations",
        "lemma_used_in_search", "lemma_actions_nonzero",
        "save_value")}, indent=2), flush=True)
    return summary


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
