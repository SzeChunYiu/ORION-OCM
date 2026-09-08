# PR150 — independent bounded mathematical check

The three qualifications in DECISION.md are fair against PR head
b051177e0670c71e2da657df8779eb60671dd385. They clarify missing assumptions rather
than reject the three proposed research axes or the correctly conditioned Fano bound.

1. **Marginal information is insufficient.** For independent fair Z and R,
   Y1=R and Y2=Z XOR R each have zero marginal information about Z; together they
   determine it. The retained four rows and script implement that example correctly.
   A fixed-horizon n·b bound follows when action choice adds no information about Z
   beyond recorded history and every conditional observation increment is bounded
   by b. Random stopping/expected-cost claims need additional reasoning. The stated
   30-cause, error .05 arithmetic and 44-probe ceiling are consistent with the formula
   in its informative-error regime.

2. **Full identification is not necessary for every repair.** One admissible repair
   that works for all 30 causes defeats a universal full-cause identification charge.
   A lower bound on repair needs a reduction to the relevant decision/identification
   task. Phase costs may be added only without counting shared diagnostic, search or
   verification work twice. The theory labels its decomposition schematic, so this
   is an appropriate qualification rather than a claim that every conditional version
   is false.

3. **Proposal entropy does not guarantee success.** A point mass on a wrong repair
   has zero entropy and can have zero success probability. The theory explicitly
   permits proposal weights, so asking for calibration, rank and evaluation-cost
   evidence is necessary.

One strengthening is useful: calibrated posterior entropy also need not bound expected
optimal guess cost. Let N=2^m repairs each have probability 1/(mN), and one leading
repair have probability 1−1/m, for integers m≥2. Then

    H = h2(1/m) + 1 ≤ 2, hence χ = 2^H ≤ 4,
    E[optimal guess rank] = 1 + (N+1)/(2m), which grows without bound.

The descending-probability order gives the leading repair rank 1; the other N repairs
have mean rank (N+3)/2. This proves the displayed expectation directly. Thus χ can
remain an effective-diversity/perplexity statistic; even a calibrated posterior needs
separate successful-repair rank, tail mass and evaluation-cost analysis before a
performance guarantee. This is an analytic observation, not a new experiment.

Read scope: DECISION.md, COUNTEREXAMPLES.json and its complete 2886-byte script;
the pinned theory lines 113–225; FETCHED.json identities. I did not independently
read the cited external papers, the full theory, registry or synthetic study, and did
not execute the script, OCM, native checking, corpus work or a new study. Exact file
identities and these line bounds are in PR150-MATH-REVIEW.json.
