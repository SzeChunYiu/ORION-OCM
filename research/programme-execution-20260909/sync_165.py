"""Narrow, idempotent evidence reconciliation for the existing roadmap.

No issue closure, scientific-result rewrite, or blanket checkbox completion.
Public before/after snapshots are retained. A read-before-write drift check is
not advertised as an atomic compare-and-swap against arbitrary concurrent edits.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import urllib.request

REPO = "SzeChunYiu/ORION-OCM"
ROOT = "https://api.github.com/repos/" + REPO
G2 = ["it is admitted before the fresh task;", "the fresh task is not part of acquisition/admission;",
      "the learned object is actually invoked;", "execution trace identifies the object;",
      "the object materially changes a registered cost/capability coordinate;",
      "removal/revocation weakens or removes the effect;", "answer-cache explanation is excluded;",
      "retrieval-only explanation is excluded or becomes `PARENT_SUFFICIENT`."]
G3 = ["Learn method A from family A.", "Learn method B from disjoint family B.",
      "Freeze unseen A+B task family.", "Confirm combined solution absent from training.",
      "Require actual use of both learned method identities.", "Remove A only.", "Remove B only.",
      "Remove both.", "Compare against persistent program/library parent.",
      "Measure composition search/verification cost."]
BLOCK = """<!-- OCM-EVIDENCE-SYNC-20260909:BEGIN -->
## Current evidence disposition and execution order — 9 September 2026

This status is scoped to the cited records. It supersedes older comments calling all
G2.4 or G3.1 unrun; it does not requalify every historical checkbox below.

| Obligation | Disposition | Evidence and strict boundary |
|---|---|---|
| G2.4 | **SUPPORTED AT REGISTERED POLYNOMIAL SCOPE** | #192, run `34280474284`, artifact `10077457805`: `CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8`; 13/64 actual-use wins; ordinary = OCM, revoked = primitive. Runtime reconstruction is reported, not a newly established separate-OS-process claim. |
| G3.1 | **SUPPORTED AT REGISTERED POLYNOMIAL SCOPE** | #193, run `34281240853`, artifact `10077796740`: `METHOD_COMPOSITION_SUPPORTED_AT_SCOPE`; 3/256 both-method witnesses and A/B/both revocation controls. Ordinary library parent ties. |
| G1.2 | **PARTIAL / NEGATIVE SUBTRACTION DISPOSITION** | Open #187 reports both existing vessel interfaces required by current tests; no production deletion or minimum-vessel proof. Compensation, physical costs and general minimality remain unresolved. |
| G4 | **EXACT-PARENT / PRICE-CONDITIONAL DISPOSITION** | #152 / #154 / #167 / #176: current compose reordering has `EXACT_POLICY_SUFFICIENT`; exact stopping/strategy results do not establish a learned residual. #71 remains `LEARNED_ROUTER_NOT_YET_AUTHORIZED`. #192 reports `NO_LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS`; #193 does not establish lifetime payback. |
| Second-domain goal-only reuse | **NOT ESTABLISHED BY FROZEN #203 v1** | Exact source `29c0ec40bb377152e24b5e9cd5ad133daae6fa36`; recorded first allocation has 30/30 `UNKNOWN` at the 8-second grounding bound, before target search/native proof checking. Not unprovability or method uselessness. Any unchanged repeat is post-exposure reproducibility; the separately described join successor cannot overwrite v1. |

**Ordered work, under the same `(F,O,Π,C)` rather than new cognitive cores:**
A. Synchronize this evidence record. B. Execute/audit frozen #203 unchanged.
C. G3.2 scoped failure memory. D. G3.3/G3.4 causal representation change and
insufficiency diagnosis. E. Strongest library-learning parents, lower acquisition
cost and measured payback. F. Discharge #152/#71 by a scoped exact-policy terminal
or an evidenced real residual, never by assuming a router is useful.
G. Physical denominator only where measured (#70/#115/selected #196 machinery).
H. One persisted field/operator/executive lineage and fixed external constitution
across successive stages. I. G6 learned intervention effects and at least three
real earned transitions. J. Language and formal proof under that same machine.
K. #73 integrated strongest-parent product. L. #38/#144/#49 independent/protected
replication and final proof-of-function. No C–L success is inferred from A or B.

Raw search counts are not elapsed time, RSS, energy, or whole-lifetime cost.
Separate-process execution, production evidence revocation, learning, usefulness,
architectural advantage and independent replication remain distinct claims.
<!-- OCM-EVIDENCE-SYNC-20260909:END -->
"""
NOTES = {
"### G1.2 Minimality / subtraction": "**Scoped disposition:** #187 reports unsuccessful subtraction under current tests; this is partial/negative evidence, not a minimality proof. Its open PR and unlanded attempts remain distinct from production adoption.",
"### G2.4 Fresh-task causal use": "**Scoped support:** #192 supports the registered polynomial mechanism. Checked items below refer only to that scope. Its restart control reconstructs `OCMRuntime`; the separate-OS-process obligation is deliberately not marked complete. No architectural or lifetime-payback result is implied.",
"## G3.1 Method composition": "**Scoped support:** #193 supports the registered polynomial composition mechanism, including separate A/B/both revocation and ordinary-parent parity. Checked cost evidence is search/verification accounting, not complete physical or acquisition payback.",
"## G4.4 Learned-routing unlock": "**Disposition:** retain exact-parent and price-conditional results, including the closed current-compose negative. No existing scoped positive authorizes ML or establishes a programme-wide `LEARNED_ROUTER_NOT_NEEDED` terminal."
}

def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)

def section(body: str, start: str, end: str, items: list[str]) -> str:
    require(body.count(start) == 1 and body.count(end) == 1, "section identity drift")
    i, j = body.index(start), body.index(end)
    require(i < j, "section ordering drift")
    part = body[i:j]
    for item in items:
        old, new = "- [ ] " + item, "- [x] " + item
        require(part.count(old) + part.count(new) == 1, "checkbox identity drift: " + item)
        part = part.replace(old, new)
    return body[:i] + part + body[j:]

def transform(body: str) -> str:
    require(body.startswith("# ORION-OCM Master Roadmap"), "wrong roadmap")
    result = section(body, "### G2.4 Fresh-task causal use", "### G2.5 Strong parent controls", G2)
    result = section(result, "## G3.1 Method composition", "## G3.2 Scoped failure learning", G3)
    # Do not turn runtime reconstruction into separate OS-process evidence.
    process = "- [ ] machine process restarts;"
    require(process in result, "restart checkbox needs human reconciliation")
    for heading, note in NOTES.items():
        require(result.count(heading) == 1, "heading drift")
        if note not in result:
            result = result.replace(heading + "\n", heading + "\n\n" + note + "\n", 1)
    old = "→ G5 Developmental Evolvability\n→ G6 Cross-Domain Persistent Development"
    new = "→ G5 Physical Scalability / Safe Consolidation\n→ G6 Developmental Evolvability (persistent lineage; cross-domain stages)"
    require(result.count(old) + result.count(new) == 1, "gate overview drift")
    result = result.replace(old, new)
    old_bottleneck = "This is the programme's current primary cognitive bottleneck."
    new_bottleneck = "Bounded polynomial reuse is supported by #192; second-domain goal-only reuse, broader acquisition, and full lifetime benefit remain separate obligations."
    require(result.count(old_bottleneck) + result.count(new_bottleneck) == 1, "bottleneck prose drift")
    result = result.replace(old_bottleneck, new_bottleneck)
    begin, end = "<!-- OCM-EVIDENCE-SYNC-20260909:BEGIN -->", "<!-- OCM-EVIDENCE-SYNC-20260909:END -->"
    if begin in result or end in result:
        require(result.count(begin) == result.count(end) == 1, "status-block drift")
        i, j = result.index(begin), result.index(end) + len(end)
        result = result[:i] + BLOCK.rstrip() + result[j:]
    else:
        at = result.index("\n") + 1
        result = result[:at] + "\n" + BLOCK + result[at:]
    return result

def request(path: str, data=None):
    raw = None if data is None else json.dumps(data).encode()
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "ocm-scoped-roadmap-reconciliation"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    if raw is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(ROOT + path, data=raw, headers=headers,
                                 method="GET" if raw is None else "PATCH")
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def main():
    out = Path(os.environ["EVIDENCE_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    snapshots = {}
    for n in (38, 49, 70, 71, 73, 115, 144, 151, 152, 165, 187, 192, 193, 196, 203):
        snapshots[str(n)] = request(f"/issues/{n}")
        comments = request(f"/issues/{n}/comments?per_page=100")
        require(len(comments) < 100, "comments require explicit pagination")
        snapshots[str(n) + "_comments"] = comments
    (out / "issues-before.json").write_text(json.dumps(snapshots, indent=2) + "\n")
    require("CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8" in json.dumps(snapshots["192_comments"]), "G2 source missing")
    require("METHOD_COMPOSITION_SUPPORTED_AT_SCOPE" in json.dumps(snapshots["193_comments"]), "G3 source missing")
    require("EXACT_POLICY_SUFFICIENT" in snapshots["152"]["body"], "exact-parent source missing")
    before = snapshots["165"]
    require(before["state"] == "open", "roadmap state changed")
    after_body = transform(before["body"])
    require(transform(after_body) == after_body, "non-idempotent transformation")
    (out / "issue165-before.md").write_text(before["body"])
    (out / "issue165-after.md").write_text(after_body)
    fresh = request("/issues/165")
    require((fresh["body"], fresh["updated_at"]) == (before["body"], before["updated_at"]), "concurrent issue edit; refuse overwrite")
    if after_body != before["body"]:
        request("/issues/165", {"body": after_body})
    readback = request("/issues/165")
    require(readback["body"] == after_body and readback["state"] == "open", "issue readback mismatch")
    report = {"terminal": "ISSUE165_SCOPED_EVIDENCE_SYNCHRONIZED", "issue": readback["html_url"],
              "updated_at": readback["updated_at"], "changed": after_body != before["body"],
              "before_sha256": hashlib.sha256(before["body"].encode()).hexdigest(),
              "after_sha256": hashlib.sha256(after_body.encode()).hexdigest(),
              "restart_os_process_checked": False, "other_issues_closed": False}
    (out / "SYNC-RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
