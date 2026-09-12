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

## 3a. Discharged so far

| record | discharge | the index that was missing |
|---|---|---|
| `RV-377-005` | narrowed | everything — a bare `NOT_OBSERVABLE_AT_SCOPE` against rows "not yet built" |
| `RV-377-016` | narrowed | budget, ecology, intervention set — declined by fiat as `NO_FURTHER_ESCALATION` |
| `RV-377-023` | narrowed | ecology, interventions, **both null controls** (neither existed yet) |
| `RV-377-030` | narrowed | ecology, interventions, null controls — the *positive* half inherits the same qualification |
| `RV-377-058` | narrowed | its two ecologies are now known to carry **no** intervention-robust coefficient witness (`RV-377-089`), which explains its silence about `D1` without invoking search |
| `RV-377-069` | narrowed | **size, capped at 7** |

**`RV-377-069` is the sharpest instance in the corpus.** An exhaustive census is exhaustive only up to its bound, and
that bound **excluded the answer**: `RV-377-102`'s intervention-robust coefficient witness is **11 nodes**, wholly
outside a census that stopped at seven. Its four exact lower bounds stand precisely as measured — they are theorems
about sizes 1–7. What is withdrawn is the implicature that a census stopping at 7 says anything about the carriers
that turned out to matter. The word *exhaustive* had been carrying a completeness the measurement never had.

## 4. Running score

Four indices re-run so far: **two negatives overturned** (`RV-377-088`, twice over), **one upheld** (`RV-377-089`
confirming `RV-377-082`'s ceiling to `h = 32`), **one overturned against its own author within the hour**
(`RV-377-089b`). A rule that only ever overturns is measuring nothing; the upheld case is what makes the others
informative.

---

## 5. The four kingdom-axis negatives, indexed — and the joint region nobody searched

`GMI-DA7` concludes that a kingdom can be gained on exactly four axes — the alphabet `A`, the structure-depth bound
`d`, the arithmetic instrument `p`, the ecology family `F` — and the programme's central negative is that **none of the
four yields one**. That conclusion is a conjunction of four executed sweeps. Here is what each actually searched.

| axis | record | receipt | **swept** | **held at default** |
|---|---|---|---|---|
| `A` alphabet | `GMI-DA8` | `STAGE_AXIS_A_V2_REPAIRED.json` | 7 rows × 3 obligation modes (`ACC`, `PARITY`, `MAXV`) × 6 columns, θ = 0.85 | `d`, `p` (registered 8-bit), `F`, intervention set (**standard only** — predates rule 36) |
| `d` depth | `RV-377-065` | `STAGE_DK_V1_DEPTH_GATED.json` | **48 cells, depths `d1`–`d6`**, two code families (`PERM`, `XOR`), 6 rows, `D64`/`D128`, seeds 7/13/23 | **depth > 6**, `p`, `F`, intervention set |
| `p` precision | `RV-377-076` | `STAGE_DK_V5_PRECISION_RESIDUAL_V1.json` | **7 instruments `fx8`…`wide`**, 13 rows, 5 event sequences, θ = 17/20 | **2 ecologies only**, `A` parameters, `d`, intervention set |
| `F` family | `RV-377-070` | `STAGE_F_AXIS_REFINEMENT_V1.json` | **14 certified pairs × 7 deciding demands**; 10 split, 4 survive | `A` parameters, `d`, `p` |

Each is strong **on its own axis** and sits at an inherited default on the other three. So:

> **The four axes were swept one at a time. No cell off the diagonal of `A × d × p × F` has ever been searched.**
> `GMI-DA7`'s monotonicity says refining any axis can only *split* classes — it says nothing about whether a kingdom
> lives at a *combination*, e.g. an extended alphabet **at** depth 5 **at** 12 bits **under** a refined family. Four
> one-axis negatives do not compose into a negative over the product.

### 5.1 This is not a hypothetical gap — it has already cost one witness

`RV-377-089b` is exactly a two-axis miss. The six intervention-robust coefficient witnesses live at the combination

* **`A`-parameter** `h = 3` (not the zoo default `h ∈ {2, 4}`), **and**
* **ecology** `E_sym3` (not among the three `RV-377-082` measured).

Neither one-axis sweep could see them. The parameter sweep (`RV-377-089`) ran the right parameters on the **wrong three
ecologies** and concluded "no witness anywhere". The ecology enumeration (`RV-377-085`, `GMI-DA9`) ran all five
ecologies at the **zoo's default parameters** and concluded the gradient net was "lost" on `E_sym3`. Both were correct
on their own axis and both missed the point that was there. It took the product of the two to find it.

**One executed instance of an off-diagonal witness is enough to make the joint region a real gap rather than a
scruple.**

### 5.2 What this does and does not do to `GMI-DA7`

It does **not** touch `GMI-DA7`'s theorem, which is a monotonicity result about `K(A, d, p, F)` and is proved, not
measured. It narrows the **empirical conclusion drawn under it**. The honest statement is:

> No kingdom is gained by refining **any single axis while the other three are held at their registered defaults**.
> The joint region is unsearched, and the one place a product of two axes has been searched, it contained something
> neither axis found alone.

Recorded as gap **DG-8**. Closure is not an exhaustive product sweep — that is the full cross-product of four axes and
is not affordable. Closure is: **a declared low-discrepancy sample of the off-diagonal region, sized so that a
kingdom-bearing cell of a stated minimum measure would be hit with a stated probability**, executed once, with the
sample and the probability registered before the run.
