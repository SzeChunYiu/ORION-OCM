# LANGUAGE_KSO_ALPHA_REPORT — Conversational OCM Alpha (M6)

Date 2026-09-05. Terminal claimed: `LANGUAGE_KSO_ALPHA` at the scope below. Authority: a bounded
controlled world (55 facts) with the microworld vocabulary; synthetic scenario suite; no human
rating run yet; no comparator; no novelty or superiority claim.

## 1. What runs

`python -m ocm.chat --demo` on a clean checkout executes the eleven-point demonstration
(normal conversation; follow-up with a pronoun; explanation; consequential ambiguity →
clarification; genuine unknown; a wrong source reported as unverified; teach a word; reuse it;
process restart retaining it; revoke its evidence and watch the capability stop; unrelated
knowledge intact; diagnostic trace tied to ledger events). `python -m ocm.chat --diagnostic`
prints the per-turn trace from actual runtime events.

## 2. Product gates (issue #8 §12) — hard zero gates, measured

| gate | result | where |
|---|---|---|
| protected answer laundering | 0 incidents | `M6_ALPHA_SCENARIO_EVAL_V1.json` hostiles |
| revoked knowledge still asserted as live | 0 | same (teach → revoke → the word stops working) |
| user assertion silently becoming machine truth | 0 / 51 (M4) and 0 here | machine layer empty after every scenario |
| process restart losing epistemic state | 0 / 9 scenarios | restart re-asks the last question |

Graded metrics with denominators: scenario steps expected 42/42; per family all steps; latency
mean 28 ms / max 77 ms per turn; external IO 0; persistence = ledger + workspace + world index +
learned state files.

## 3. Epistemic integrity, by construction

* Verified facts answer "Yes." and cite the verification evidence id.
* Unverified source claims are REPORTED with the source ("A source (rumour:v1) says so, but I
  have not verified it") — the gate refuses an ASSERTED marker for them (`MARKER_MISMATCH`).
* Speaker commitments are REPORTED ("Someone in this conversation said so; I have no
  independent warrant"); ten speakers never promote (M4 receipt).
* Unknowns say what is not known; revoked support says it was revoked.
* Style requests change register only; facts are re-answered identically (scenario `style_shift`).

## 4. Human evaluation protocol (frozen, not yet run)

Blinded raters score each machine turn separately on: understood intent; answer meaning correct;
helpful/relevant; grammatical; natural; appropriately uncertain; coherent with prior turns
(1–5 each; no aggregate "intelligence" score). Arms: OCM Alpha; simple rule/template baseline
(the fact glosses without dialogue state); a frontier chat model as a non-matched external
reference labelled as such; the strongest matched-data parent from the M7 preflight when
available. Prompts = the nine scenario families' scripts; randomisation seed
`OCM-ALPHA-HUMAN-EVAL-20260905`; raters see arms in random order under neutral labels. Thresholds
are frozen relative to the template baseline before any protected run.

## 5. Resource dashboard

From the receipt: 42 turns, mean 28 ms, max 77 ms; ledger events per turn recorded in the
diagnostic trace; state directory sizes are reported by `--diagnostic` (`resources`). No external
IO. Reproducible build: `./scripts/m0_install_dev.sh && python -m ocm.chat --demo --state /tmp/ocm_demo`.

## 6. What Alpha is not

Not open-domain; not fluent realisation (checked variants only); not multilingual; no real
protected conversations rated yet; the 10M-word sample-efficiency experiment is
`CANNOT_CHECK_BABYLM_DATA` (M5). These are M7's protected comparison and the follow-ups in the
obligation registry (KS-T60…T66).
