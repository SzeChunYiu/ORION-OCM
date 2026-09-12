# GMI basin/restart developmental reachability theorem v1

Status: **FORMAL CONDITIONAL REACHABILITY LAW / T1 NARROWING**

Date: 2026-09-12.

Purpose: bridge representational existence and actual development when successful optimization is only guaranteed from a subset of initial states.

## 1. Registered productive basin

Let initialization `theta_0~mu`. Let `G` be a registered productive set with

\[
\mu(G)\ge p>0.
\]

Assume that for every initialization in `G`, the registered update law reaches protected development loss at most `epsilon` within at most `T(epsilon)` charged steps. The inner guarantee may come from convexity, a PL region, a local contraction theorem, or another explicitly proved condition.

## 2. Theorem BR-1 — independent restart law

With `r` independent initializations, probability that at least one run starts in `G` is

\[
1-(1-p)^r.
\]

To make basin-miss probability at most `delta`, it is sufficient and necessary for the registered lower bound `p` that

\[
r\ge \frac{\log\delta}{\log(1-p)}.
\]

For small `p`, this scales as `O(log(1/delta)/p)`.

Expected number of independent starts until first productive initialization is `1/p`.

Thus developmental burden must charge both the inner optimization cost and basin-search/restart cost.

## 3. Theorem BR-2 — validation lower confidence on basin mass

Suppose `m` independent development-only initialization probes classify `g` of them as entering the preregistered productive condition. By Hoeffding, with probability at least `1-delta`,

\[
p\ge p_L=\max\left(0,\frac gm-\sqrt{\frac{\log(1/\delta)}{2m}}\right).
\]

Using `p_L` in BR-1 yields a conservative restart budget without consulting protected outcomes.

## 4. Dead-region negative twin

If productive basin mass is zero under the initialization/update protocol, restarts cannot help. The dead-ReLU microtheorem is an exact example: positive excess loss can coexist with zero gradient over a nonproductive region.

Likewise, if no positive lower bound on `p` can be justified, no finite high-confidence restart budget follows from this theorem.

## 5. GMI consequence

Developmental reachability requires at least:

```text
representation adequacy
productive-basin mass / entry mechanism
within-basin contraction or progress law
initialization / restart price
stochastic update price
protected target epsilon and confidence delta
```

This separates “a solution exists in the architecture” from “the declared development protocol can reach it within budget.”

## Claim ceiling

This is an assumption-indexed basin/restart theorem. It does not predict productive-basin geometry for large neural networks; estimating/causally changing that geometry remains OPEN-BLOCKING.
