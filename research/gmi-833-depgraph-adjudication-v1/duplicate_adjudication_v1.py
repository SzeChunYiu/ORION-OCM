#!/usr/bin/env python3
"""GMI #833/#842 — semantic duplicate adjudication v1.

Two frozen populations from the census (source 2fffb144):

  (A) 1,652 candidate_semantic_duplicates groups (7,202 objects; census groups
      by CASE-NORMALIZED statement text, verified here).
  (B) 857 GAP-DUPID gaps (one object id declared in 2+ places).

Verdicts (task taxonomy): DUPLICATE / DISTINCT / UNCERTAIN per group (A) and
per gap (B), each with a typed reason.  Rules are stated, applied mechanically
in fixed order, and every rule's verification act is explicit:

  A-rules (first match wins):
    A1 RESOLVE         members resolved via census; unresolvable ids recorded.
    A2 RAW_VENDORED    byte-identical statements AND >=1 member path contains
                       '/raw/' (the corpus's raw/ trees are frozen parent
                       snapshots) -> DUPLICATE (content copy).  Verification =
                       exact byte comparison of the member statements.
    A3 SAME_FILE       byte-identical AND all members in one file
                       -> DUPLICATE (intra-file repetition).
    A4 VERBATIM_CLAIM  byte-identical, all members claim-class
                       (THEOREM/LAW/CLAIM/COROLLARY/PROPOSITION/LEMMA/AXIOM)
                       -> DUPLICATE (restatement of the same claim text).
    A5 VERBATIM_OTHER  byte-identical, non-claim members (receipt/protocol/
                       heading/code lines) in different packages, no raw/
                       -> DISTINCT: identical BOILERPLATE text with different
                       referents is not one scientific object.
    A6 CASE_ONLY       statements equal after case+whitespace normalisation
                       but not byte-identical -> non-claim: DISTINCT
                       (structural heading/markup, different referents);
                       claim-class: UNCERTAIN (read individually, logged).
    A7 DIFFERENT_TEXT  same census hash but texts differ beyond
                       normalisation -> UNCERTAIN (never guessed).

  B-rules (per DUPID gap, first match wins):
    B1 VERBATIM_REDECLARATION  all declarations byte-identical -> DUPLICATE.
    B2 CANONICAL_REDECLARATION equal after normalisation -> DUPLICATE.
    B3 POINTER                 one declaration's text references the other's
                               file or contains it as a pointer row
                               -> DUPLICATE (registry/pointer vs declaration).
    B4 ID_COLLISION            otherwise -> DISTINCT (two different contents
                               share one id: the census defect; fix = unique
                               ids, recorded as the gap's resolution path).

Content-collapsed counting: a DUPLICATE group contributes ONE content node;
DISTINCT/UNCERTAIN groups contribute their member count.  Both raw and
collapsed totals are reported; no census disposition is modified.
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

SCHEMA = "GMI_833_DUPLICATE_ADJUDICATION_V1"
CLAIM_CLASSES = frozenset({
    "THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM",
})


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def load():
    idx = json.loads((CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8"))
    aud = json.loads((CENSUS_DIR / "AUDIT_V1.json").read_text(encoding="utf-8"))
    gg = json.loads((CENSUS_DIR / "GMI_GAP_GRAPH_V1.json").read_text(encoding="utf-8"))
    byid = defaultdict(list)
    for o in idx["scientific_objects"]:
        byid[o["object_id"]].append(o)
    return idx, aud, gg, byid


# A5c individual reads (2026-09-16): every group in the read-required class
# was read against its member artifacts; verdicts keyed by statement_hash.
# DISTINCT = same text about DIFFERENT artifacts (per-receipt provenance
# notes, standard argparse idioms); DUPLICATE = same declaration/schema/
# copied sentence, one content node.
A5C_OVERRIDES = {
    "47e18a8b02cab3f7c76d7eef892e160fcbd75dc157e44ac2a73f76d059ff9efa": ("DISTINCT", "per-receipt provenance note ('Executed on laptop-billy; ... Reproduced in CI.') - each about its own receipt"),
    "96c6fa764cee2b2166484eade5ecb237b36612dc51e064198f324737418890b5": ("DISTINCT", "standard argparse idiom parser.add_argument('receipt', type=Path)"),
    "a9828c7f731f4fa682d2878e1fd8662bde00398271f143a3060c43c79115de34": ("DISTINCT", "per-witness provenance note ('Derived by a parallel worker...') - each about its own witness"),
    "afba1f7c00cf5ef19e919bf4326c2b34bb3e9c5024e2c24f0397cf8d7bc69185": ("DISTINCT", "per-receipt provenance note ('Executed on laptop-billy; ... across transfer.') - each about its own receipt"),
    "e9ef8a531948ea6fd6db9c24104f213a0bbfebb001ef445113c395a3d346e295": ("DISTINCT", "standard argparse idiom parser.add_argument('--receipt', required=True)"),
    "1d54aabff1d95c472205943a186cd2cbb71d8a6f9c6e8a6b48b5f93310e5db6c": ("DUPLICATE", "same receipt-schema field list copied across the three F2 tranche scripts"),
    "1f715b7e9786f98a5e0dd18be5306989a88b6087cd7bbe12af10897a19d3b946": ("DUPLICATE", "same parent id P-ALGORITHM-DISCOVERY in PARENT_LEDGER V1 and V2"),
    "20d3dea7804ce9bed88d12152b771c8fb7f0d8ce08e7e86ea82b51bbcc91e792": ("DUPLICATE", "copy-pair sentence (grand-unification vs structural-threshold-repair doc copy)"),
    "24562e11dfe256b0f392d648fa8f8b8a76fdf0255eec06e7addd63a51ec52086": ("DUPLICATE", "same parent-concept pair 'proof search + proof checker' in two docs"),
    "4a2c0aeba0d2863c2dda2ced32685d522c08843ea8a677838d210d4e81372834": ("DUPLICATE", "same PH-REV-2 diagnosis note in two parent ledgers"),
    "5592d2d5e2557de478a287adc2324c4c2a8a2c5a2d6ee7effb0e551d9ffe7db7": ("DUPLICATE", "same D_draw definition in script and its receipt"),
    "62a67c0d98b2b2f4e29db2106559b6e0a6c7adca61f3c60d22d394cf8eb613e4": ("DUPLICATE", "B6 correction doc and its evidence/ copy"),
    "659464cfec3517c14936dc1359d347ee0de00e117db0469de432b1787f26c3ef": ("DUPLICATE", "same grid_H rule carried by ten receipts and its source"),
    "6e667e1aff81b1cd4403bef0d6ee767e99a1890160ed66c24f05a085d075dc98": ("DUPLICATE", "same B6 sentence in doc and evidence/ copy"),
    "75f99327c40a8fbf9d646138fd00c815c921b8335760b623fa61c4211bca6b22": ("DUPLICATE", "same receipt_digest helper def copied across four closure packages"),
    "76408b1c0f26797babc0cdf1705153b8c0d6e68656ff2d4c9c883bdb33cd13cc": ("DUPLICATE", "same SCHEMA_V1 field spec in two schema files"),
    "776384fd54c9064a74cb3b511837ecb00ad952a6236402b5521f3cb29bb25c73": ("DUPLICATE", "same write-out line in two verify scripts of one package"),
    "801c792f64f8056b973da97e49f3790954d15cc0f4791b6deb24c0179cf39d81": ("DUPLICATE", "b6_adjudicate line and its evidence/ copy"),
    "80adf5870f00731c695c9d3e17aada323c630bff38b2773914fd566d3fc50d07": ("DUPLICATE", "copy-pair docstring (analytic receipt, opcode contract)"),
    "82c458179d00c2aaf30652b53784f71a3b489f830a1ce52e32093b4fe76f7e06": ("DUPLICATE", "project-specific Certificate isinstance guard copied between packages"),
    "8936fc63cbf3d0b5fca49d2b70ea637c944701d03aa497c3161c034986386f6f": ("DUPLICATE", "shared custody_v1 template docstring in three repair packages"),
    "9a9500fbfc9ebb9440b35644f0c63d70c1b809c9c39d545431c11f8ef98543ee": ("DUPLICATE", "same custody check line in two repair packages"),
    "a8ed04219cfcc89900a7ffedfbf5114fa49f4c3902f4ad262fcc4e91a5e90d42": ("DUPLICATE", "same closure-suite payload helper in four packages"),
    "b9498739eaf150fe27a47211cc196e99337f0a9dcfb963a67cd3b8256b99e9c7": ("DUPLICATE", "same B6 sentence in doc and evidence/ copy"),
    "c1f247a3ecd619c37e6bd90ccedeb303f39a7548d99f2b457638e80c8f4044e5": ("DUPLICATE", "same no-oracle scope contract in F2 ceilings and tranche3"),
    "c4d67151628eed4168bfe7a7936dde27a6dd35086205dd3f781a98074ee9f51f": ("DUPLICATE", "same item39_ceiling field in the copy-pair scripts"),
    "c6d0725e2471d3f687ae1a30e7d447d9202847d4adefad8e375581e6b228ce10": ("DUPLICATE", "same closure-suite digest check in three packages"),
    "ceeee59d491b3448439989baa22a043653b09d810ea69759027c0cab5a4c9214": ("DUPLICATE", "same schema field list across the three F2 tranche scripts"),
    "d0c431e5eefc72baedf9263768d8fd65cd401cce4d8c659284ca2346aeb37791": ("DUPLICATE", "same claim_ceiling field in the copy-pair scripts"),
    "d227868d22517cf9719545610200fac8981e37fed53f839a0eb97767ef825f6a": ("DUPLICATE", "same Codex GMI_CORE_ANSWER note in two parent ledgers"),
    "d9fabf84ef2c569505f3b1bf7942168a79921f2c3c8e37f76e894be74c74dd23": ("DUPLICATE", "same receipt_sha256 carry line in two closure packages"),
    "dce5a7288f373cda960849a99badcc90b2fb72ec36bff16b8e3e66cd862ce1f5": ("DUPLICATE", "b6_adjudicate docstring and its evidence/ copy"),
    "e813020fe3b2eb8249b57afe533a193e909f7a542cb106407cedddebdb16da6a": ("DUPLICATE", "same dated status header in B6 doc and evidence/ copy"),
    "f50d85f15c6bcf08a38b31cbf308bc941bf46a9100c7b79a02ac9eb78cb420e7": ("DUPLICATE", "same pruning-certificate vocabulary tuple in two tranche scripts"),
    "f51217da32458243124edae3ebe6ab3e2fca196ad27ad1fe2657ab0308b80482": ("DUPLICATE", "same freeze-contract line in two packages' freezes"),
    "f933fe373804493badaafcdfc8c8c5b052be92dedaaf0b87547aa52bb04f4a2d": ("DUPLICATE", "same sentence in same-package AUDIT and FREEZE"),
    "fd0e1cd49b44d8e656dc513c08920d70460bebec84057252efb826d4ddd1cce5": ("DUPLICATE", "copy-pair sentence (finite-samples caveat)"),
    "fe05cfd424308130c37d97572b5277817f90bf43a6804e347ea3cce0682ff4a3": ("DUPLICATE", "copy-pair standalone-receipt docstring"),
}


def adjudicate_group(c, byid):
    """Resolve the group exactly as the census formed it.  The census keys
    groups by statement.lower() (sha256 of that key = statement_hash) and
    lists one entry per member object (ids may repeat for DUPID-shared ids).
    Member count = len(object_ids); declarations whose lowercased statement
    hashes to statement_hash supply the text/class/path evidence."""
    import hashlib as _h
    matching = []
    for i in set(c["object_ids"]):
        for d in byid.get(i, []):
            if _h.sha256((d["statement"] or "").lower().encode()).hexdigest() \
                    == c["statement_hash"]:
                matching.append(d)
    member_count = len(c["object_ids"])
    if not matching or member_count < 2:
        return {"verdict": "UNCERTAIN", "reason": "A0_UNRESOLVABLE_MEMBERS",
                "members": matching, "member_count": member_count,
                "unresolved": sorted(set(c["object_ids"]))}
    stmts = [d["statement"] for d in matching]
    byte_identical = len(set(stmts)) == 1
    paths = [d["source_path"] for d in matching]
    claim_all = all(d["object_class"] in CLAIM_CLASSES for d in matching)
    if byte_identical and any("/raw/" in pth for pth in paths):
        verdict, reason = "DUPLICATE", "A2_RAW_VENDORED_COPY"
    elif byte_identical and len(set(paths)) == 1:
        verdict, reason = "DUPLICATE", "A3_SAME_FILE_REPETITION"
    elif byte_identical and claim_all:
        verdict, reason = "DUPLICATE", "A4_VERBATIM_CLAIM_RESTATEMENT"
    elif byte_identical:
        st = stmts[0].strip()
        artifact_lit = re.search(r"\b\w[\w.-]{2,}\.(?:json|jsonl|md|py)\b", st)
        json_decl = re.match(r'^\s*"[a-z_0-9]+"\s*:\s*".{25,}"', st)
        heading = st.startswith("#") or st.startswith("##")
        code_like = bool(re.match(
            r"^(print\(|raise |class |import |from |json\.|out\.|OUT\.|receipt\s*=|\w+\s*=\s*\w+\(|\w+\[|RECEIPT|state=|require\()", st))
        fragment = len(st) < 25
        if artifact_lit or json_decl:
            verdict, reason = "DUPLICATE", "A5a_VERBATIM_SAME_ARTIFACT_OR_DECLARATION"
        elif heading or code_like or fragment:
            verdict, reason = "DISTINCT", "A5b_STRUCTURAL_OR_CODE_IDIOM"
        elif c["statement_hash"] in A5C_OVERRIDES:
            verdict, reason = A5C_OVERRIDES[c["statement_hash"]]
        else:
            verdict, reason = "UNCERTAIN", "A5c_VERBATIM_READ_REQUIRED"
    elif len({norm(st) for st in stmts}) == 1:
        if claim_all:
            verdict, reason = "UNCERTAIN", "A6_CASE_ONLY_CLAIM_READ_REQUIRED"
        else:
            verdict, reason = "DISTINCT", "A6_CASE_ONLY_STRUCTURAL_DIFFERENT_REFERENTS"
    else:
        verdict, reason = "UNCERTAIN", "A7_HASH_TEXT_DIVERGENCE"
    return {"verdict": verdict, "reason": reason, "members": matching,
            "member_count": member_count, "unresolved": None}


def adjudicate_gap(g, byid):
    decls = byid.get(g["claim_id"], [])
    if len(decls) < 2:
        return {"verdict": "UNCERTAIN", "reason": "B0_DECLARATIONS_NOT_FOUND",
                "declarations": decls}
    stmts = [d["statement"] for d in decls]
    paths = [d["source_path"] for d in decls]
    if len(set(stmts)) == 1:
        return {"verdict": "DUPLICATE", "reason": "B1_VERBATIM_REDECLARATION",
                "declarations": decls}
    if len({norm(s) for s in stmts}) == 1:
        return {"verdict": "DUPLICATE", "reason": "B2_CANONICAL_REDECLARATION",
                "declarations": decls}
    # pointer: one decl's text contains another decl's basename or its
    # statement contains a shorter declaration's statement verbatim
    for a in decls:
        for b in decls:
            if a is b:
                continue
            base = b["source_path"].split("/")[-1]
            if base in (a["statement"] or ""):
                return {"verdict": "DUPLICATE", "reason": "B3_POINTER_TO_SAME_CONTENT",
                        "declarations": decls}
    return {"verdict": "DISTINCT", "reason": "B4_ID_COLLISION_CONTENT_DIFFERS",
            "declarations": decls}


def main():
    idx, aud, gg, byid = load()
    groups_out = []
    for c in aud["candidate_semantic_duplicates"]:
        r = adjudicate_group(c, byid)
        r["statement_hash"] = c["statement_hash"]
        r["object_ids"] = c["object_ids"]
        groups_out.append(r)
    gaps_out = []
    for g in gg["gaps"]:
        if not g["id"].startswith("GAP-DUPID"):
            continue
        r = adjudicate_gap(g, byid)
        r["gap_id"] = g["id"]
        r["claim_id"] = g["claim_id"]
        gaps_out.append(r)

    def tally(rows):
        dist = Counter(r["verdict"] for r in rows)
        reasons = Counter(r["reason"] for r in rows)
        return dict(dist), dict(reasons.most_common())

    gdist, greasons = tally(groups_out)
    ddist, dreasons = tally(gaps_out)

    # content-collapsed object count over grouped objects only
    collapsed = 0
    for r in groups_out:
        n = r["member_count"]
        collapsed += 1 if r["verdict"] == "DUPLICATE" else n

    def slim(r):
        mem = r.get("members") or r.get("declarations") or []
        return {
            "verdict": r["verdict"], "reason": r["reason"],
            "statement_hash": r.get("statement_hash"),
            "gap_id": r.get("gap_id"), "claim_id": r.get("claim_id"),
            "object_ids": r.get("object_ids"),
            "member_count": r.get("member_count") or len(mem),
            "member_paths": [m["source_path"] for m in mem][:8],
            "member_classes": [m["object_class"] for m in mem][:8],
            "member_statements": [m["statement"][:120] for m in mem[:4]],
            "first_statement": (mem[0]["statement"][:200] if mem else None),
            "unresolved": r.get("unresolved") or None,
        }

    out = {
        "schema": SCHEMA,
        "census_frozen_source_sha": idx["frozen_source_sha"],
        "rules": (__doc__ or "").strip(),
        "candidate_groups": {
            "count": len(groups_out),
            "verdict_distribution": gdist,
            "reason_distribution": greasons,
            "adjudications": [slim(r) for r in groups_out],
        },
        "dupid_gaps": {
            "count": len(gaps_out),
            "verdict_distribution": ddist,
            "reason_distribution": dreasons,
            "adjudications": [slim(r) for r in gaps_out],
        },
        "content_collapse": {
            "grouped_objects": sum(r["member_count"] for r in groups_out),
            "content_nodes_after_collapse": collapsed,
            "collapsed_away": sum(r["member_count"] for r in groups_out) - collapsed,
            "note": "a DUPLICATE group contributes 1 content node; DISTINCT/UNCERTAIN keep member count; objects in no group are unaffected",
        },
    }
    path = HERE / "DUPLICATE_ADJUDICATION_V1.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=False,
                               ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"candidate groups: {len(groups_out)}  verdicts: {gdist}")
    for k, v in greasons.items():
        print(f"   {v:5d}  {k}")
    print(f"DUPID gaps: {len(gaps_out)}  verdicts: {ddist}")
    for k, v in dreasons.items():
        print(f"   {v:5d}  {k}")
    print(f"content collapse: {out['content_collapse']['grouped_objects']} -> "
          f"{collapsed} nodes ({out['content_collapse']['collapsed_away']} collapsed away)")
    print(f"sha256 {path.name}: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
