# DG-7 — the index audit of every negative terminal in the corpus

**Opened by:** `RV-377-088`. **Governed by:** `GMI-DA11` (domain algebra §16) and protocol rules 37, 38, 39.
**Purpose:** `GMI-DA11` proves that a negative claim is universally quantified over a *region* of `K(A, d, p, F)` and is
entitled to exactly the region actually searched. This document establishes, for every negative terminal on record,
which indices were **swept** and which were **held at an inherited default**.

## 0. What this document is and is not

The classification below starts from a keyword triage over the full text of every ledger record — it is a
**prioritisation tool, not a verdict**. A record scoring `0/5` has not been shown to be wrong; it has been shown not to
*say* what it searched. Every item is confirmed by hand before it is re-run, and the three confirmed so far are marked.
The triage also produces false positives: records whose terminal contains the word `FALSIFIED` because they *did the*
*falsifying* (`RV-377-088`, `RV-377-089b`) are flagged by the regex and are not audit targets.

**Counts.** 38 terminals match the negative pattern. **5 are audited** (`RV-377-009`, `-014`, `-052`, `-082`, `-089`).
**33 are open.** Twelve name no index at all; of those twelve, four are triage false positives and **three are
confirmed high-priority**, below.

## 1. Confirmed high-priority targets

### 1.1 `RV-377-077` — "no unknown form at scope". **The programme's headline negative.**

Terminal: `NO_UNKNOWN_FORM_AT_SCOPE__ALL_7_RECOVERED_MACHINES_ARE_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT`.

The record's own body is honest about its scope — *"no unknown form at 20 000 evaluations on `E_smooth3`"* — but the
terminal says `AT_SCOPE`, and that phrase is carrying an entire quantifier. The index block is:

| index | swept | held at default |
|---|---|---|
| ecology `F` | — | **one**: `E_smooth3` |
| budget | — | **one**: 20 000 evaluations |
| alphabet parameters | — | the zoo's default-parameter rows |
| depth `d`, precision `p` | — | registered |

This matters more than the bookkeeping suggests. `E_smooth3` is one of the **two ceiling ecologies** identified by
`RV-377-089`: three of the eight zoo parents are inadmissible there, **including both gradient nets**, and
`RV-377-089`'s 80-row sweep to `h = 32` confirms no coefficient carrier clears θ there at any setting. So "all seven
recovered machines are developmentally equal to a known parent" is a result from a search that **could not have
produced a coefficient machine in the first place** — the region it quantified over excludes, by construction, the one
carrier class whose absence it is implicitly reporting.

> **This target is already under test.** `RV-377-100`, in flight, runs the unchanged `B1` recovery microscope on
> `E_sym3` — the one registered ecology carrying intervention-robust coefficient witnesses. Those runs are therefore
> simultaneously `G15` step two and the first `DG-7` audit of `B4`'s headline negative. If a recovered machine there
> is *not* developmentally equal to a known parent, `NO_UNKNOWN_FORM_AT_SCOPE` falls on the ecology axis exactly as
> `E_smooth2`'s `NOT_OBSERVABLE` fell on the parameter axis.

### 1.2 `RV-377-016` — a bounded failure declared terminal

Terminal: `SEARCH_REACHABILITY_BOUNDED_FAILURE_AT_SCOPE__EXISTENCE_CERTIFIED__NO_FURTHER_ESCALATION`.

This one is unusual and deserves credit: it *names itself* a bounded failure and it *certifies existence* — so it is
already half-compliant with `GMI-DA11`. What it then does is declare `NO_FURTHER_ESCALATION`, which converts a bounded
search result into a terminal by fiat. Under rule 39 the escalation axes must at least be **named** even when they are
declined: budget, grammar depth (the record mentions depth 2 and depth 3 plateaus), and ecology.

### 1.3 `RV-377-005` — a bare terminal

Terminal: `NOT_OBSERVABLE_AT_SCOPE`, with `fresh_evidence_source: "Stage E' on E_smooth with reference rows (not yet
built)"`. A `NOT_OBSERVABLE` recorded against rows that did not exist yet. This is the earliest record in the corpus to
carry the phrase and it names no index whatever. It is superseded in substance by `RV-377-009`/`-014`/`-088`, which
worked the same `PH-REV` question to a positive, but its terminal was never annotated.

## 2. The open list, by indices named

`A_params` = the parameter family within the alphabet · `F` = ecologies · `d` = structure depth · `p` = precision ·
`interv` = intervention set.

| indices named | records |
|---|---|
| **0 of 5** | `RV-377-005`, `-011`, `-016`, `-023`, `-028`, `-029`, `-058`, `-074`, `-077`, `-081` *(+ `-092`, `-097`: triage false positives, B2 positives)* |
| **1 of 5** | `RV-377-015`, `-031`, `-038`, `-042`, `-046`, `-056`, `-060`, `-063`, `-064`, `-065`, `-067`, `-069`, `-070`, `-075`, `-079`, `-080`, `-083` |
| **2 of 5** | `RV-377-051`, `-076` |
| **audited** | `RV-377-009` ✗overturned · `-014` ✗overturned · `-052` ✓replaced by mechanism form · `-082` ½ceiling upheld, witness superseded · `-089` ✓upheld, then ½corrected by `-089b` |

## 3. Closure criterion

`DG-7` closes when every record in §2 carries an explicit index block — swept range or held default, per index — and
every confirmed high-priority target has either been re-run over the unswept index or has had its terminal narrowed in
wording to the region it actually searched. **Narrowing the wording is a full discharge**; re-running is required only
where the unswept region is cheap and the claim is load-bearing.

## 4. Running score

Four indices re-run so far: **two negatives overturned** (`RV-377-088`, twice over), **one upheld** (`RV-377-089`
confirming `RV-377-082`'s ceiling to `h = 32`), **one overturned against its own author within the hour**
(`RV-377-089b`). A rule that only ever overturns is measuring nothing; the upheld case is what makes the others
informative.
