#!/usr/bin/env python3
"""Render PARENT_LEDGER_V2.json into (1) LITERATURE_LEDGER_V2.md — the human-readable primary-source
ledger with per-source verification depth — and (2) COLLISION_MATRIX_V1.md — the #377 §24 item-3
collision/subtraction matrix: parent × {D0..D3 owned, B-rungs owned, kill scope, residual}.

Deterministic; no judgement is added here. Everything rendered comes from the worker ledgers
(primary-source reconstruction) or from PARENT_LEDGER_V1.json (Codex, abstract depth)."""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "PARENT_LEDGER_V2.json")
DEPTH_ORDER = ["FULL_TEXT_READ", "PARTIAL_TEXT_READ", "ABSTRACT_ONLY", "NOT_ACCESSIBLE", "FROM_MEMORY_UNVERIFIED"]
FAMILY_TITLES = {
    "P0": "P0 — universal computation / induction / search / limits",
    "P1": "P1 — universal / general-agent theories and bounded rationality",
    "P2": "P2 — incremental / self-improving universal problem solving",
    "P3": "P3 — neural architecture / learning-algorithm discovery",
    "P4": "P4 — meta-learning / learned learning rules / continual learning",
    "P5": "P5 — programmatic / library-learning intelligence",
    "P6": "P6 — probabilistic / generative-program intelligence",
    "P7": "P7 — algebraic / categorical descriptions of learning systems",
    "P8": "P8 — cognitive architectures / symbolic systems",
    "P9A": "P9A — existing cross-morphology equivalence / simulation / compilation results (not in #377 §4)",
    "P9B": "P9B — learnability / evolvability limits that separate learning morphologies (not in #377 §4)",
}


def fam_of(pid):
    return pid.split(".")[0]


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def main():
    L = json.load(open(LEDGER))
    recs = sorted(L["records"], key=lambda r: (fam_of(r["parent_id"]), r["parent_id"]))
    by_fam = defaultdict(list)
    for r in recs:
        by_fam[fam_of(r["parent_id"])].append(r)

    # ---------------- LITERATURE_LEDGER_V2.md
    out = []
    out.append("# Track-B Literature Ledger V2 — primary-source depth pass (issue #377 GMI-D0)\n")
    out.append(f"Coverage terminal (computed by `build_parent_ledger_v2.py`, never asserted): `{L['status']}`\n")
    out.append("Depth histogram over entries (best source per entry): " + json.dumps(L["verification_depth_histogram"]) + "\n")
    out.append("Rule: `FULL_TEXT_READ` means the worker read the full text and every quote is verbatim from it; "
               "`PARTIAL_TEXT_READ` means sections were read; `ABSTRACT_ONLY`/`NOT_ACCESSIBLE`/`FROM_MEMORY_UNVERIFIED` "
               "entries carry no load-bearing claim in Track B until upgraded. V1 (Codex) abstract-depth records are preserved "
               "in `PARENT_LEDGER_V2.json:v1_records` and are not re-rendered here.\n")
    out.append("| #377 family | entries | full-text entries |\n|---|---|---|")
    for k, v in L["coverage_by_377_family"].items():
        out.append(f"| {k} | {v['entries']} | {v['full_text']} |")
    out.append("")
    for fam in sorted(by_fam, key=lambda f: (len(f), f)):
        out.append(f"\n## {FAMILY_TITLES.get(fam, fam)}\n")
        for r in by_fam[fam]:
            out.append(f"### {r['parent_id']} — {md_escape(r['name'])}\n")
            out.append(f"Disposition: `{r.get('disposition')}` · best verification: `{r.get('best_verification_status')}`\n")
            out.append("Sources:\n")
            for i, s in enumerate(r.get("primary_sources", [])):
                out.append(f"- [{i}] {md_escape(s.get('title'))} — {md_escape(s.get('authors'))} ({s.get('year')}), {md_escape(s.get('venue'))}. "
                           f"{md_escape(s.get('url_or_doi'))}{' arXiv:' + str(s.get('arxiv_id_if_any')) if s.get('arxiv_id_if_any') else ''} — `{s.get('verification_status')}`")
            out.append("")
            out.append(f"**What it already explains.** {md_escape(r.get('what_it_already_explains'))}\n")
            out.append(f"**Formal object.** {md_escape(r.get('formal_object'))}\n")
            out.append(f"**Strongest result.** {md_escape(r.get('strongest_theorem_or_result'))}\n")
            out.append(f"**Assumptions.** {md_escape('; '.join(r.get('assumptions', [])) if isinstance(r.get('assumptions'), list) else r.get('assumptions'))}\n")
            out.append(f"**Resource model.** {md_escape(r.get('resource_model'))}\n")
            out.append(f"**Failure boundary.** {md_escape(r.get('failure_boundary'))}\n")
            out.append(f"**Implementation.** {md_escape(r.get('implementation'))}\n")
            out.append(f"**Track-B residual.** {md_escape(r.get('track_b_residual'))}\n")
            out.append(f"**Upward question.** {md_escape(r.get('upward_question'))}\n")
            qs = r.get("load_bearing_quotes", [])
            if qs:
                out.append("Load-bearing quotes (verbatim from sources actually read):\n")
                for q in qs:
                    out.append(f"> \"{md_escape(q.get('quote'))}\" — [{q.get('source_index')}] {md_escape(q.get('location'))}")
                out.append("")
            out.append(f"Verification notes: {md_escape(r.get('notes_on_verification'))}\n")
    if L.get("corrections_to_v1"):
        out.append("\n## Corrections to the V1 (Codex) ledger reported by the depth pass\n")
        out.append("| family | prior entry | defect | correction | evidence |\n|---|---|---|---|---|")
        for c in L["corrections_to_v1"]:
            out.append(f"| {c.get('family_id')} | {md_escape(c.get('prior_entry'))} | {md_escape(c.get('defect'))} | {md_escape(c.get('correction'))} | {md_escape(c.get('evidence'))} |")
    if L.get("missing_parents_reported"):
        out.append("\n## Missing parents reported (must be absorbed before any saturation claim)\n")
        for m in L["missing_parents_reported"]:
            out.append(f"- ({m.get('family_id')}) {md_escape(m.get('parent') or m)}")
    open(os.path.join(HERE, "LITERATURE_LEDGER_V2.md"), "w").write("\n".join(out) + "\n")

    # ---------------- COLLISION_MATRIX_V1.md
    cm = []
    cm.append("# Collision / subtraction matrix V1 (issue #377 §24 item 3)\n")
    cm.append("Rows: parents reconstructed at primary-source depth. Columns: which Track-B derivation levels (D0..D3) and "
              "claim rungs (B0..B8) the parent already OWNS, what naive Track-B claim it KILLS, and the residual it leaves. "
              "Generated from `PARENT_LEDGER_V2.json`; a parent with no full-text source is marked ⚠ and its row is advisory.\n")
    cm.append("| parent | depth | D0 | D1 | D2 | D3 | rungs owned | kills | residual (Track B) |\n|---|---|---|---|---|---|---|---|---|")
    for r in recs:
        dl = r.get("derivation_levels_owned", {}) or {}
        rungs = ", ".join(sorted((r.get("claim_rungs_owned", {}) or {}).keys()))
        warn = "" if r.get("best_verification_status") in ("FULL_TEXT_READ", "PARTIAL_TEXT_READ") else "⚠ "
        cells = ["✔" if d in dl else "" for d in ("D0", "D1", "D2", "D3")]
        cm.append(f"| {warn}{r['parent_id']} | {r.get('best_verification_status')} | " + " | ".join(cells) +
                  f" | {md_escape(rungs)} | {md_escape(r.get('kill_scope'))} | {md_escape(r.get('track_b_residual'))} |")
    # theorem hooks
    cm.append("\n## Theorem hooks reported by families (GMI-T id → constraint)\n")
    for k in sorted(L.get("theorem_hooks", {}), key=lambda s: (len(s), s)):
        for h in L["theorem_hooks"][k]:
            cm.append(f"- **{k}** ({h['family_id']}): {md_escape(h['constraint'])}")
    # family syntheses summary
    cm.append("\n## Derivation-level ownership summary\n")
    cnt = defaultdict(int)
    for r in recs:
        for d in (r.get("derivation_levels_owned") or {}):
            cnt[d] += 1
    cm.append("| level | parents owning it (count) |\n|---|---|")
    for d in ("D0", "D1", "D2", "D3"):
        cm.append(f"| {d} | {cnt[d]} |")
    cm.append("\nReading: D0 is owned by nearly every family (representability is never Track-B content); D1 is owned at the "
              "execution coordinate by the simulation/compilation parents (P9A) and at the algebraic level by P7; D2 is "
              "owned within single substrates (P3/P4) and bounded by P9B limits; D3 (prospective, cross-paradigm) has no "
              "owner in the ledger — that is the residual, subject to the parent-product null GMI-V4-15.\n")
    open(os.path.join(HERE, "COLLISION_MATRIX_V1.md"), "w").write("\n".join(cm) + "\n")
    print("rendered", len(recs), "records into LITERATURE_LEDGER_V2.md and COLLISION_MATRIX_V1.md")


if __name__ == "__main__":
    main()
