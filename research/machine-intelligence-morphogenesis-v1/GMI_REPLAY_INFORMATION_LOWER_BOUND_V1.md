# GMI Replay Information Lower Bound v1

Status: **CONTINUAL-DEVELOPMENT NO-FREE-LUNCH / R7**

Date: 2026-09-12.

Consider an old protected task consisting of `N` independent binary obligations with arbitrary label vector
\[
Y\in\{0,1\}^N.
\]

Suppose a future update/development procedure retains only replay labels on subset `S` plus state that is independent of the omitted old labels.

## RI-1 — omitted-obligation collision theorem

If `S` omits any protected obligation `j`, then there exist two legal old tasks `Y,Y'` that:

1. agree on every replayed item in `S`;
2. induce exactly the same retained replay information;
3. differ on omitted item `j`.

Therefore **no update algorithm seeing only that retained information can distribution-free guarantee exact retention on all `N` arbitrary old obligations**.

Exact replay-free retention requires either:

- retaining all independent label bits;
- retaining an equivalent compressed sufficient statistic under an explicit structured-law assumption;
- parameter/module isolation that makes the old mapping invariant;
- or weakening the exact retention constitution.

## RI-2 — information lower bound

For unrestricted independent binary obligations the old target family has size `2^N`, so exact future recoverability requires at least `N` reliable bits of retained old-task information.

This is the continual-learning specialization of the semantic quotient lower bound.

## Exact finite collision microscope

For `N=6`, the runner exhausts all replay subset sizes `m<6` and all 64 labelings. Every proper subset has collisions. In particular, even replaying five of six obligations leaves 192 subset-aggregated indistinguishable label pairs across the six possible omitted coordinates.

## Consequence for replay vs expansion

Replay is not fundamentally required when another mechanism preserves the same sufficient information. But any claim of exact retention with **less than the old-task sufficient information** must identify the structural assumption or protected isolation that makes the compression legal.

## Claim ceiling

This is a distribution-free exact-retention lower bound. Approximate retention, correlated task structure, generative replay and real neural representation drift require separate quantitative laws.
