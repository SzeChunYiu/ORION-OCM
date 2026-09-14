# CRR1 — sharp necessity bounds with constructive attainment

This is a constructive implementation of the inherited Tian–Pearl (2000)
[equation 25](https://ftp.cs.ucla.edu/pub/stat_ser/r271-A.pdf), not a new
causal-identification theorem.

## Interface

X,Y are binary **endogenous** variables. A finite hidden root U specifies
the response type (X,Y0,Y1) in {0,1}^3. Write its eight nonnegative masses
w(x,y0,y1), summing to one. Equations X=f(U), Y=Y_X(U) form an acyclic SCM;
one shared finite root is a product law with one coordinate. Hidden roots
are not observed or intervenable in this interface. All interventions below
are surgical replacements of endogenous equations, with unchanged root law.

Declare exact population evidence a=P(0,0), b=P(0,1), c=P(1,0), d=P(1,1),
q0=P(Y0=1), q1=P(Y1=1). Observational probabilities are nonnegative and
sum to one. There is a compatible response model iff
b ≤ q0 ≤ 1-a and d ≤ q1 ≤ 1-c. These are constraints on common-population
evidence, not permission to combine unrelated observational and trial cohorts.

PN=P(Y0=0 | X=1,Y=1) is defined only when d>0. For every compatible model,

    max(0,(b+d-q0)/d) ≤ PN ≤ min(1,(1-q0-a)/d).

Every point in this closed interval is attained. Thus equality of its endpoints
is necessary and sufficient for population point identification in this full
response-type class. An empty class and an undefined conditional are separate
invalid inputs; neither is an identified value or a zero estimate.

## Direct attainment proof

Set t=d·PN and r=q0-b-d+t. Within X=1, the four masses in order
(Y0,Y1)=(0,0),(0,1),(1,0),(1,1) are

    c-r, t, r, d-t.

Nonnegativity is exactly max(0,d-q0+b)≤t≤min(d,1-q0-a).
They have factual Y1 margin d and counterfactual Y0 margin q0-b.

Within X=0 set v=q1-d and k=max(0,b+v-a-b). The corresponding masses are

    a-v+k, v-k, b-k, k.

Their nonnegativity follows from 0≤v≤a+b and 0≤b≤a+b. They have factual
Y0 margin b and counterfactual Y1 margin v. Combining the two tables gives
eight valid masses and reconstructs every supplied observational and
interventional probability. This proves compatibility sufficiency and
attainment simultaneously. Necessity follows from the same row margins.

The executable interface takes exact rationals. The algebra applies to real
probabilities as well; the finite executable census is a check of the proof,
not the premise that extends it to arbitrary real-valued evidence.

## All endogenous intervention laws

There are nine assignments in {no replacement,0,1}² for (X,Y). The
observational law and q0,q1 determine all nine joint laws: intervening on X
fixes X and uses qx; intervening on Y fixes Y and preserves observed X's
marginal; intervening on both yields a point mass. Every archived W5 equality
is checked on this complete interface, including interventions on Y and both.

No root intervention, cross-world joint observation, policy side channel,
unbounded graph class or finite-sample estimator is included in that statement.
