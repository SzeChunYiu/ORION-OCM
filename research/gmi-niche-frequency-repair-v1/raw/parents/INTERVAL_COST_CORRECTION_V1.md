# Parity-n interval-cost correction

Status: **CONDITIONAL EXACT COST ALGEBRA; NO NEW NATIVE MEASUREMENT.**
The original PR573 file, including its predictions, outcomes and revival, is
preserved byte-exact. This note supplies its current scientific interpretation.

## Parent and cost scope

The mature local parent is
[DCR's cost contracts at 8bd474de](https://github.com/SzeChunYiu/ORION-OCM/blob/8bd474deaf162580c6f47f8e2ef0c75835a18960/research/gmi-delegation-cost-repair-v1/cost_contracts_v1.py).
It distinguishes a definitional Python-opcode projection from a different
resource requiring supplied sound per-label intervals. Its strict comparison
requires the candidate's finite upper bound below the comparator's lower bound.
Absent native bounds are [0,+infinity), not exact zero native work.
These rules are adopted faithfully; no new interval calculus is claimed.

Fix an integer n>=1. **Condition on** the registered per-call Python-event
formulas X_n=3n+2 for the written XOR chain and D_n=6 for the delegating template.
The formula script's n=3 arithmetic check does not certify these compiler
formulas on every n, runtime or arbitrary realization. An algebraic statement
below for all n quantifies over this supplied formula model only.

To combine Python and native charges, independently supply a common additive
resource unit: each counted Python event costs exactly1, and the sum of native
charges on each call is N_n in [l_n,u_n]. Bounds must hold uniformly over the
declared inputs; u_n may be infinite. They are assumptions, not certified by
passing numbers to an interval function. The two total-cost intervals are

    X=[3n+2,3n+2],   D=[6+l_n,6+u_n].

Multiplying both endpoints by the positive sweep size2^n preserves all ordering
statements. The framework here neither proves additivity for a physical device
nor converts a native CPU operation into a Python opcode.

## PNIR-1 — the sound interval certificate

For intervals A=[a-,a+] and B=[b-,b+], a+<b- certifies A cheaper for every
admitted completion; b+<a- certifies the reverse. Two identical singleton
intervals certify an exact tie. Otherwise this simple certificate reports
UNRESOLVED. It does not infer falsehood from an unresolved comparison.

Thus a supplied lower native bound l_n certifies XOR cheaper when

    3n+2 < 6+l_n, equivalently l_n>3n−4.

A finite upper bound u_n<3n−4 certifies delegation cheaper.
A lower bound alone cannot provide that upper certificate.

With l_n=2n+1 and no upper bound, XOR is certified for n<5.
For n>=5 the intervals alone do not settle the ordering.
At n=5 the XOR value17 equals the delegating lower endpoint17, but the latter
interval is [17,+infinity). Native cost11 permits a tie; cost12 makes XOR cheaper.
For n=6, native cost13,14 or15 all satisfy the same lower bound13.
They give delegation cost19,20 or21 against XOR20: cheaper, tied or dearer.
This is the decisive countercontrol to the original lower-bound crossover.

## PNIR-2 — constructive exact-cost revival

Now declare the different, stronger hypothetical model N_n=2n+1 exactly.
Then D_n(total)=2n+7 and

    X_n−D_n(total)=n−5.

Consequently XOR is cheaper below5, the costs tie at5, and delegation is
cheaper above5, within this model. The per-sweep values are:

| n | XOR | exact-model delegation | verdict |
| --- | --- | --- | --- |
| 3 | 88 | 104 | XOR cheaper |
| 4 | 224 | 240 | XOR cheaper |
| 5 | 544 | 544 | exact tie |
| 6 | 1280 | 1216 | delegation cheaper |
| 7 | 2944 | 2688 | delegation cheaper |
| 8 | 6656 | 5888 | delegation cheaper |

These are exact symbolic evaluations, not measurements. The old table's
numbers can be recovered positively after making the missing equality premise
explicit. Its “faithful” label does not prove that premise.

The stated count “n loads, n−1 additions, one return” totals2n, not2n+1.
An additional operation would need to be identified and charged explicitly.
Even a corrected arithmetic count is not a proof of native implementation
work or its commensurability with the declared Python-event unit.
If a different hypothetical exact charge2n is chosen, the tie moves to n=4.
If the exact charge is4n, XOR stays cheaper for every n>=1.
There is therefore no universal crossover over all putatively faithful charges.
Only the Python component of delegation is constant6; with N_n=2n+1 its
priced total grows linearly as2n+7.

## PNIR-3 — template comparison and evidence boundary

Conditional on the written shared-sum template's Python formula11n+6 and
nonnegative native costs, its lower cost exceeds XOR's exact3n+2 for n>=1.
That supports domination of this particular template under this metric.
It is not a completeness theorem or exclusion of every neural realization.

DCR's Python-only projection assigns native events zero **Python opcodes**
by definition. That is a valid restricted metric, not proof of zero physical
work. Changing to a priced-native coordinate changes the cost contract.
Neither projection is an empirical end-to-end resource comparison by itself.

The original source contains prose reporting execution with DCR on
CPython3.12.14 at main@d61a2ec6, as well as numeric outcome/revival tables.
These reports are retained. The three PR573 files do not include the invoked
candidate generator, per-input outputs, full event ledgers, execution receipt,
binary identity or a separately bound premeasurement freeze. Their local
chronology and claimed execution authenticity are therefore unresolved here.
This does not assert that no execution or earlier freeze occurred elsewhere.

The unchanged script imports no modules, calls no candidate and only calculates
and prints formulas, including its original product-order predictions.
Its output is not replay of the appended DCR measurements.
The new tests check only exact interval algebra, constructive completions,
source preservation and declared cost models. They do not compile or execute
parity candidates or reconstruct any campaign.

The remaining empirical obligation is a source/input/runtime-bound cost
contract or measurement for the actual native work, in the chosen resource
unit and full accounting scope. It is independent of the formal capsule.
