# V19 analytic controls and attribution boundaries

These are complete finite countermodels or deductions. Executable and kernel
replay outcomes are recorded separately; the descriptions do not claim a run.

## S4.1 — coherence cannot be omitted

On {e,a}, define ee=e, ea=ae=a, and leave aa undefined.
Element e is a unit and supplies both local units. Every associativity triple
with at most one a reduces to a unit law. With two or three a's both bracketings
are undefined. Thus strong partial associativity holds. But a*e and e*a exist,
while (a*e)*a does not: coherence fails. A category with the derived single
object would require a*a. This is Cranch–Doherty–Struth Lemma 6.4(1).

## S4.2 — associativity and its sharp total-unital size bound

On {e,a,b}, let e be a two-sided identity and define aa=b, ab=ba=e, bb=b.
The table is total, so coherence holds, and e supplies local units.
Yet (aa)b=bb=b whereas a(ab)=ae=a. Hence associativity fails.
Every total unital magma with at most two elements associates: a triple
containing the unit reduces by its identity laws. Otherwise all entries are
the same possible nonunit a. If aa=e both bracketings equal a; if aa=a
both equal a. There is no other output. Three is therefore the sharp smallest
carrier for this particular total-unital associativity falsifier.

## S4.3 — weak associativity does not repair definedness

On {e,f,x}, the defined products are

    ee=e, ff=f, ex=x, fx=x, xe=x, xx=x.

Products ef,fe,xf are undefined. Both e and f are units as defined in S1.1;
x has left unit e (also f) and right unit e. Local units therefore exist.
If both triple bracketings exist and the triple contains x, both outputs
are x. Without x, a successful bracketing requires three identical units,
so weak equality on jointly defined bracketings holds.
Coherence also holds. If the last entry is e, every possible intermediate
output has a defined product with e. If it is x, every arrow multiplies x.
If it is f, the second entry must be f, and then the first must be f;
the resulting product ff exists. These exhaust the consecutive-product cases.
Nevertheless (ef)x is none and e(fx)=x. Strong definedness agreement fails,
and the two distinct left units of x show the reconstruction obstruction.
This realizes the preregistered weak-law control without changing its scope.

## S4.4 — definedness and composite values are separate information

The discrete category on two objects has only ee=e and aa=a defined.
Filling every undefined entry with the existing arrow a yields the total
monoid ee=e, ea=ae=aa=a. The derived object set changes from {e,a} to {e}.
Thus this particular untagged filling is not faithful: different source tables
can have the same filled output. A fresh bottom symbol with a retained tag
is different; one can recover none versus every original arrow exactly.

C4 addition modulo 4 and V4 bitwise XOR on labels {0,1,2,3} are both total,
with the same identity 0, but 1*1 is respectively 2 and 0. Endpoints and
composability therefore do not determine composite values. The V16 evidence
already supplies the associated all-word context comparison; this control
uses only the displayed product difference and does not re-close an atom.

## S4.5 — multiplicativity alone does not preserve identity

Let the source be the one-element monoid and the target {e,a} with e a unit
and aa=a. Mapping the sole source arrow to a preserves every product because
aa=a. It does not preserve identity, since a≠e. This is the standard
idempotent obstruction; Riccardi CAT_6:28 explicitly distinguishes these laws.
The V19 roundtrip avoids it by using inverse maps reflecting the full operation.

## S4.6 — one-sided parent reading

On a two-element carrier the total right projection xy=y is strongly
associative and coherent. Every element is left-neutral, while no element
is right-neutral: choose x different from the candidate right unit e, giving
xe=e≠x. The left projection gives the dual example.

Cranch–Doherty–Struth v1 Section 2 calls a unit left OR right neutral;
Definition 3.2 requires units e,e' with D(e,x),D(x,e'). Taken literally,
right projection satisfies these displayed clauses, since all products exist.
It contradicts the intended uniqueness/right-identity conclusion under that
reading. Both HTML and PDF were inspected: PDF page 1 gives the disjunction,
and page 2 gives Definition 3.2. This is a precise premise-mapping obstruction,
not a claim about every possible strengthened interpretation of that paper.
V19 uses both-sided U and actual local identity equations, so excludes it.
The side-specific equivalence proof in S1.5 maps V19 instead to Riccardi's
left/right identity formulation, without relying on the weaker reading.

## Boundary controls

Empty carriers, singleton identities, nontrivial endomorphisms, multiple objects
and permutations must be admitted when lawful. Invalid dimensions, Boolean
integer aliases and malformed raw words must fail validation. In particular a
malformed later symbol must not become accepted merely because an earlier
product already failed. Actual finite tests and independent review determine
whether the executable API meets these requirements.
