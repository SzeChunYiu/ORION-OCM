#!/usr/bin/env python3
"""GMI #833/#842 — OVERSTRONG adjudication of the 283 GAP-FIN2UNIV flags.

Task verdicts: OVERSTRONG / PROPER / UNCERTAIN per flag, by comparing the
object's wording strength against its registered quantifier/proof scope.

Method (two layers, both logged):
  1. Every claim-class object (113) was individually read against its full
     statement and source context (reads logged in READS below; the read
     verdict is authoritative for those objects).
  2. Non-claim rows (receipts/protocols/other, 170) are classified by stated
     mechanical reason rules; residuals are UNCERTAIN, never guessed.

Reason taxonomy (each observed on real data during the read pass):
  NEGATED_UNIVERSAL          the universal is negated/disclaimed ('not a
                             universal family verdict', 'no census is claimed
                             to verify every ...') - census negation window
                             too short for long-span negations.
  FINITE_DOMAIN_DECLARED     the universal is explicitly bounded to an
                             enumerated set ('all four cells', 'all 256
                             representable', 'every node through depth h',
                             'every held support size', 'exhausts all 27
                             vectors').
  ENUMERATED_LAWS_OR_GRID    universal over the registered law set / declared
                             task grid / columns / cells, each executed.
  PROTOCOL_RULE              normative recording rule ('record ... in every
                             receipt'), not a mathematical claim.
  RECEIPT_CARRY_NOTE         note that every committed/historical receipt
                             stands/reproduces - receipt bookkeeping.
  LEDGER_OR_STATUS_ROW       revival/audit/status row (NOT_EARNED,
                             NOT_ESTABLISHED, why-notes, evidence lists).
  PARENT_THEOREM_DESCRIBED   literature parent's genuinely-universal theorem
                             described in a parent ledger (Levin search), or
                             an explicitly-open upward question.
  DEFINITIONAL_UNIVERSAL     universal word inside a definition of an update
                             rule / channel class ('every site', 'for all i'
                             over a finite array).
  OPEN_GAP_LISTING           item in an explicit 'not yet their universal
                             quantitative response laws' gap list.
  ANALYTIC_EVIDENCE_MISLINK  object's evidence mode is analytic/mechanized;
                             the FIN2UNIV premise (bounded computation) does
                             not apply.
  NO_UNIVERSAL_WORDING       statement contains no universal wording at all
                             (flag misfire).
  HEADING_OR_LABEL           the object is a heading/title line, not a claim.

DOWNGRADE LIST: entries with verdict OVERSTRONG.  In this tranche the 283-flag
population yields none (see report); the one corpus-confirmed OVERSTRONG
instance (capability-interactions, GREEN mainline) was adjudicated by the
#939 freeze and is carried there, not re-adjudicated here.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CENSUS_DIR = REPO_ROOT / "research" / "gmi-833-corpus-census-v1"

SCHEMA = "GMI_833_OVERSTRONG_ADJUDICATION_V1"
CLAIM_CLASSES = frozenset({
    "THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM",
})

NEG_RE = re.compile(
    r"(?i)\b(?:not|no|never|neither|nor|without|cannot|must not be read)\b"
    r"[^.|;]{0,120}\b(?:every|all|any|each|universal)\b")
BOUND_RE = re.compile(
    r"(?i)\b(?:every|all|each|any)\b[^.|;]{0,40}?"
    r"(\d+|four|five|six|seven|eight|nine|ten|eleven|twelve|fourteen|fifteen|"
    r"sixteen|256|27 vectors|four state|other support|held|registered|"
    r"declared|committed|historical|member|column|cell|node|site|coordinate|"
    r"receipt|vector|task|world|law|family|depth)")
PROTOCOL_RE = re.compile(
    r"(?i)\b(record|register|charge|must|should|may not|is not checkable)\b"
    r"[^.|;]{0,80}\bevery\b|\bevery\b[^.|;]{0,60}\b(receipt|claim)\b")
CARRY_RE = re.compile(
    r"(?i)\bevery\b[^.|;]{0,40}\b(receipt|historical|committed)\b[^.|;]{0,40}"
    r"\b(stands|reproduces|still|carry)")
LEDGER_RE = re.compile(
    r"(?i)claim_movement|revival_id|NOT_EARNED|NOT_ESTABLISHED|evidence_added|"
    r'"why"|failure_class|status')
PARENT_RE = re.compile(
    r"(?i)what_it_already_explains|levin search|upward_question|OOPS Def|"
    r"parent accounting|literature")
DEFIN_RE = re.compile(
    r"(?i)native law|channel class|for all i|every site|update in which|"
    r"definition|law is a statement about")
OPENGAP_RE = re.compile(
    r"(?i)not yet their universal|gap|open question|pending")
HEADING_RE = re.compile(r"^#{1,6}\s|^[A-Z0-9-]+ [a-z].{0,60}(law|theorem)$")


def mechanical_reason(o):
    st = o.get("statement", "") or ""
    if o["proof_evidence_mode"] in ("ANALYTIC_DEDUCTIVE", "MECHANIZED_PROOF") \
            and o["quantifier_class"] not in ("UNIVERSAL",):
        return "PROPER", "ANALYTIC_EVIDENCE_MISLINK"
    if NEG_RE.search(st):
        return "PROPER", "NEGATED_UNIVERSAL"
    if OPENGAP_RE.search(st) and not BOUND_RE.search(st):
        return "PROPER", "OPEN_GAP_LISTING"
    if HEADING_RE.match(st.strip()):
        return "PROPER", "HEADING_OR_LABEL"
    if PARENT_RE.search(st):
        return "PROPER", "PARENT_THEOREM_DESCRIBED"
    if LEDGER_RE.search(st):
        return "PROPER", "LEDGER_OR_STATUS_ROW"
    if DEFIN_RE.search(st):
        return "PROPER", "DEFINITIONAL_UNIVERSAL"
    if CARRY_RE.search(st):
        return "PROPER", "RECEIPT_CARRY_NOTE"
    if PROTOCOL_RE.search(st) and o["object_class"] not in CLAIM_CLASSES:
        return "PROPER", "PROTOCOL_RULE"
    if BOUND_RE.search(st):
        return "PROPER", "FINITE_DOMAIN_DECLARED"
    if PROTOCOL_RE.search(st):
        return "PROPER", "PROTOCOL_RULE"
    if not re.search(r"(?i)\b(every|all|any|each|universal|never|always)\b", st):
        return "PROPER", "NO_UNIVERSAL_WORDING"
    return None, None


# Individual reads of the 113 claim-class objects (2026-09-16).  Keyed by
# census object_id; (verdict, reason).  These override mechanical rules.
READS = {
    "AUTO-24062EBB70DA76B9621A": ("PROPER", "PROTOCOL_RULE"),
    "P_LAW": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "EA-3": ("PROPER", "HEADING_OR_LABEL"),
    "AUTO-0BC06CF837941B5F8CF5": ("PROPER", "NEGATED_UNIVERSAL"),
    "DG-2": ("PROPER", "NO_UNIVERSAL_WORDING"),
    "AUTO-D8DDF8AC4DEB70E584E4": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-2F5545A23AC7EE3A83C1": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-7F233083C0C5D71B8314": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-86A10FDBAC70E0CC8AA3": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-4F16B93DDE1B0265240C": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-E759A1E842D547E7A2D7": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-AB4BFC913A1A3922B489": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-6FA6ECAF5C0F5DEFE579": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-B09D99835C10CCB79F0F": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-D779E9D7E4360A9B39D0": ("PROPER", "NEGATED_UNIVERSAL"),
    "RV-377-113": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "AUTO-F4E7F6B566C24ADF4381": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-7F2C8460CD7C6D92C15B": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-3FDB3A8068C894FD4183": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-098EFF6320CEED1E470A": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-0EEA314FA06D46C93FC9": ("PROPER", "NEGATED_UNIVERSAL"),
    "NOT_EARNED": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "STAGE_D_MATRIX_V1": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "GMI-T8": ("PROPER", "NEGATED_UNIVERSAL"),
    "GMI-DA7": ("PROPER", "NEGATED_UNIVERSAL"),
    "RV-377-052": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "RV-025": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "G-T01": ("PROPER", "OPEN_GAP_LISTING"),
    "CLAIM_LADDER_V3": ("PROPER", "NEGATED_UNIVERSAL"),
    "GMI-T10-B": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "RV-041": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "AUTO-3CD65573EDBA6BDD69A9": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "X-TMT12": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-E2384AE56E507E55FEFE": ("PROPER", "PROTOCOL_RULE"),
    "RV-377-056": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-0D81FE9D154A92D16582": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-DE2F6813E53463941AC0": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-DFAA76AAEF1D2A51340A": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-CBDEE35CF440EBA52432": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-44E1CC189B07009F43BD": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-DE567C3F82F671202D32": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-7833C8FECA4C072EF23F": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "AUTO-5881FEDA60E158C4ACF8": ("PROPER", "PARENT_THEOREM_DESCRIBED"),
    "T10-A": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "NO_WITNESS": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-013": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "GMI-T10-A": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-066": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "GMI-DA9": ("PROPER", "NEGATED_UNIVERSAL"),
    "RV-377-094": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-096": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-097": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-098": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "RV-377-076": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "AUTO-6D65D6B92A340BEEBC0C": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-AB1785D7E8826CED74FC": ("PROPER", "DEFINITIONAL_UNIVERSAL"),
    "AUTO-024865DF3D15BE34E9B4": ("PROPER", "DEFINITIONAL_UNIVERSAL"),
    "AUTO-C5A07067284E138AC3F1": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-C9EA5B999D2DD2F6D3F8": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-C05F6BEA9DD359A57883": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-006E8B7DFC14A6BDB4D6": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-25DF8608BD6BC5B33DBA": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-A6958401189A17148823": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-077659D3651D5EA65A74": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-3BF63E717D0005419D1A": ("PROPER", "DEFINITIONAL_UNIVERSAL"),
    "AUTO-7768E504D571C66D5DAA": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-76D4C8FF80C33876E9E7": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-7712B32CB37EB7205F5B": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-85BCE598A2130C0EA0AA": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-E0728F27A5AA5D2AF68C": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-F2EC519040299FC7EAB5": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-AA44A2A0C64AEE24B3EE": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-1229702C588AA74FAA4A": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-E6077A32FB61A00C4447": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-C6087213571F2AC8951E": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-4BAC1E90D253FA7ECF60": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-A576203B1A73A50CF5BC": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-D10808363B66C7A4A894": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-46D5B799D4A71C07D286": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-BFDE73B8AB0B9C6E7D03": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-D8DDF5193467B07633AE6": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-D1F174FD400E94BDCC8B": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-7AC5FE084E2AD041757A": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-4DCFC9E52D9998EC3504": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-EB82EBAFDAB7364210D6": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-E956F17127895C414338": ("PROPER", "PROTOCOL_RULE"),
    "TF-002": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),
    "AUTO-6FA3BAA362C334905099": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-16C081543F805D7B3DE6": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-7C009F5079287989ABA7": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-3F9B4A7026F4F22136AB": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-F6169A054AC50D8F81BA": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-2C88E1574FA7E34C86E5": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-2E5ACBC1A158E655C81D": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-76D9EEA4C57677A8AF77": ("PROPER", "DEFINITIONAL_UNIVERSAL"),
    "AUTO-E694C82E7F39CB5C71BD": ("PROPER", "PROTOCOL_RULE"),
    "AUTO-60387C77936240B3CDCD": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-89107D09160ACC697278": ("PROPER", "NEGATED_UNIVERSAL"),
    "AUTO-02D23CA7F818E5673AB0": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-29C6BDA03D8BBE2ED30A": ("PROPER", "DEFINITIONAL_UNIVERSAL"),
    "AUTO-6271D6225F0264815393": ("PROPER", "FINITE_DOMAIN_DECLARED"),
    "AUTO-3C735054A67F905BDDDC": ("PROPER", "NEGATED_UNIVERSAL"),
    "B0_LOCAL_ADAPTIVE_TRANSDUCERS": ("PROPER", "LEDGER_OR_STATUS_ROW"),
    "AUTO-4D7AB2FF0C669D488EA3": ("PROPER", "NEGATED_UNIVERSAL"),
}


# Residual-class individual reads (2026-09-16): receipt/protocol rows the
# mechanical rules left open; each read against its full statement.
RESIDUAL_READS = {
    "AUTO-02978E36B226911B4902": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # one shared reuse grid from the crossovers of every (receipt) context
    "AUTO-05A77328E2F5E022E5E0": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # structural induction enumerates every legal token (duplicate declaration)
    "AUTO-07FCF8F3C461E73CB1F8": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # 'all enumerated and the best chosen' (KV-sharing carrier subsets)
    "AUTO-08B6778104E342B614BA": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # checking every inequality of a finite rational linear system
    "AUTO-0BA179224072687C8F78": ("PROPER", "PROTOCOL_RULE"),  # re-adjudication instruction for every certificate with a compiled parent
    "AUTO-1BA91CD89AC760FE730A": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # single grid maximum honest for all enumerated contexts
    "AUTO-1E23CD8CDA994FE9B77F": ("PROPER", "PROTOCOL_RULE"),  # falsifier instruction: exhibit a control world where holding every decision fails
    "AUTO-233C3DEF5EF16DB20509": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # 'every class is enumerated in full' (MLP transform classes)
    "AUTO-23549941D2BEE3040649": ("PROPER", "RECEIPT_CARRY_NOTE"),  # every numerical comparison in the 10 passing tests uses exact rational arithmetic
    "AUTO-235FFE97ED5EBF3ED8DB": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # enumerate-test against stored examples on every (enumerated) counterexample
    "AUTO-377C96562724DC272BA6": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # exactly one receipt for every enumerated index
    "AUTO-3DB3E45D33C11FFB01AB": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # enumerate-test against stored examples on every counterexample (copy)
    "AUTO-46ED0D10714C535ECE0F": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # dominance scan over every enumerated A/C pair (raw copy)
    "AUTO-50626E1CDA0BE558CE2A": ("PROPER", "NEGATED_UNIVERSAL"),  # 'one geometry consequence rather than a universal invariant'
    "AUTO-5956359EA572D34469E5": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # recompute cell for cell over the receipt's enumerated cost coordinates
    "AUTO-6136E214FB7BB816AE43": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # forecaster serving at every declared cell of the E_ambig receipt
    "AUTO-666554AAC3D4AEEA6846": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),  # coverage audit rule over the registered microscopes
    "AUTO-6732648E9D8DAF5DE1DC": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # SAME computation for every enumerated instrument
    "AUTO-85EE3B98ABA5FC42615E": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # dominance scan over every enumerated A/C pair
    "AUTO-8B7DB278F45EABFEBAD1": ("PROPER", "NEGATED_UNIVERSAL"),  # 'universal quantification over it supplies no robust family'
    "AUTO-8C0E6C809036B0A82AEA": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),  # every (registered) microscope fully enumerable with certificate
    "AUTO-8DFBDB92BF7C354EDB27": ("PROPER", "PROTOCOL_RULE"),  # coverage rule: every positive microscope paired with a minimal negative
    "AUTO-A0F13A09E81FCEBABFE9": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # shared by every candidate of this one complete enumeration
    "AUTO-A19B033D1E74A3D85B35": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # enumerate-test on every counterexample (copy)
    "AUTO-A4E6B61F425D4DAF53B4": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # each witness computes f on all (finite truth-table) inputs
    "AUTO-BABA90779AF92C774993": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # dominance scan over every enumerated A/C pair (raw copy)
    "AUTO-C09C42F6A3CCEDB1A2E7": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # executable deterministically emits every candidate row
    "AUTO-C4E59B0E358235BD83E8": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # structural induction enumerates every legal token of the rule order
    "AUTO-CD4754BCA3B5EA2DE9F9": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # seeds derived from every relevant (enumerated) freeze hash
    "AUTO-D30841CFC6DF50FCAA3D": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # dominance scan over every enumerated A/C pair (raw copy)
    "AUTO-F03F7DFD28A4500548BB": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # per-target receipt available for every verified (enumerated) target
    "AUTO-FBC0B8B629C1879D5DF5": ("PROPER", "ENUMERATED_LAWS_OR_GRID"),  # every other registered lane/unit of the receipt set
    "FULL_RETAINED_AUDIT_RECEIPT_V1": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # receipt contains each exact-runtime entry
    "T602-23": ("PROPER", "FINITE_DOMAIN_DECLARED"),  # 'for every closure rung r ... finite required gate set Gates(r)' - rung-indexed finite gate sets
}


def main():
    gg = json.loads((CENSUS_DIR / "GMI_GAP_GRAPH_V1.json").read_text(encoding="utf-8"))
    idx = json.loads((CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8"))
    byid = defaultdict(list)
    for o in idx["scientific_objects"]:
        byid[o["object_id"]].append(o)

    rows, downgrade_list = [], []
    for g in gg["gaps"]:
        if not g["id"].startswith("GAP-FIN2UNIV"):
            continue
        o = byid.get(g["claim_id"], [None])[0]
        if o is None:
            rows.append({"gap_id": g["id"], "claim_id": g["claim_id"],
                         "verdict": "UNCERTAIN", "reason": "OBJECT_NOT_FOUND"})
            continue
        if o["object_id"] in READS:
            verdict, reason = READS[o["object_id"]]
            source = "individual_read"
        elif o["object_id"] in RESIDUAL_READS:
            verdict, reason = RESIDUAL_READS[o["object_id"]]
            source = "individual_read"
        else:
            verdict, reason = mechanical_reason(o)
            source = "mechanical_rule"
            if verdict is None:
                verdict, reason = "UNCERTAIN", "RESIDUAL_READ_REQUIRED"
        row = {
            "gap_id": g["id"], "claim_id": g["claim_id"],
            "object_id": o["object_id"], "object_class": o["object_class"],
            "id_kind": o["id_kind"],
            "quantifier_class": o["quantifier_class"],
            "evidence_mode": o["proof_evidence_mode"],
            "source": f"{o['source_path']}:{o['source_locator']}",
            "statement": o["statement"][:400],
            "verdict": verdict, "reason": reason, "basis": source,
        }
        rows.append(row)
        if verdict == "OVERSTRONG":
            downgrade_list.append({
                "claim_id": o["object_id"],
                "current_wording": o["statement"][:400],
                "defect": reason,
                "proposed_downgraded_wording": None,  # filled per-entry
                "source": row["source"],
            })

    dist = Counter(r["verdict"] for r in rows)
    reasons = Counter(r["reason"] for r in rows)
    basis = Counter(r["basis"] for r in rows)
    out = {
        "schema": SCHEMA,
        "census_frozen_source_sha": idx["frozen_source_sha"],
        "population": len(rows),
        "verdict_distribution": dict(dist),
        "reason_distribution": dict(reasons.most_common()),
        "basis_distribution": dict(basis),
        "method": __doc__.strip(),
        "adjudications": rows,
        "downgrade_list": downgrade_list,
        "cross_population_note": (
            "The one corpus-confirmed OVERSTRONG instance "
            "(CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1, GREEN mainline) was "
            "adjudicated by the #939 freeze (research/gmi-833-corpus-audit-close-v1 "
            "verdicts_v1.py) and is not part of this RED FIN2UNIV population; this "
            "tranche adds no new OVERSTRONG verdicts from the 283 flags."),
    }
    path = HERE / "OVERSTRONG_ADJUDICATION_V1.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=False,
                               ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"flags adjudicated: {len(rows)}")
    print(f"verdicts: {dict(dist)}")
    for k, v in reasons.most_common():
        print(f"   {v:4d}  {k}")
    print(f"basis: {dict(basis)}")
    print(f"downgrade list entries: {len(downgrade_list)}")
    print(f"sha256 {path.name}: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
