# Parity-3 hostile candidate expansion V3

Status: **FROZEN DESIGN; PROTECTED TIMING NOT YET EXECUTED**.

The V2 result established a deployment comparison between two implementations.
V3 attacks its candidate boundary by retaining both original functions byte-for-
byte at the AST level and adding a smaller exact threshold network and an exact
lookup table. All eight protected inputs remain unchanged. The V1/V2 packets,
sources and registrations retain their original identities and outcomes.

## Construction before measurement

Let `s=a+b+c`. The new neural candidate has hidden activations
`h_k=1[s>=k]` for `k=1,2,3`, and output `1[h_1-h_2+h_3>=1]`.
For `s=0,1,2,3`, the affine output score is respectively `0,1,0,1`.
Thus the network computes exact parity. Its input weights are `(1,1,1)`,
hidden thresholds are `1,2,3`, and output weights are `(1,-1,1)` with threshold
`1`. Reusing the shared input sum is an explicit implementation optimization;
the candidate still evaluates all three hidden thresholds and the output
threshold. This reduces the original four hidden units to three. No theorem
of minimal architecture, global implementation optimality or independent
external optimization is asserted. This is a separately derived algebraic
competitor, constructed without timing-guided search.

The lookup implementation indexes `(0,1,1,0,1,0,0,1)` with the binary word
`(a<<2)|(b<<1)|c`. This enumerates precisely the same complete truth table.
It uses no neural threshold layer. Family labels refer to these registered
implementations; they do not claim a function can belong to only one family.

## Measurement and decision contract

The new JSON registration fixes all four function AST hashes, the three V2
resource coordinates, exact capability and null gates, and CPython 3.12 on a
GitHub hosted Linux runner. Complete prearmed opcode witnesses must match in
forward and reverse candidate order before any timed block.

Each candidate receives 5,000 warm-up sweeps, then 32 timed blocks of 20,000
eight-input sweeps. Each block contains all four candidates. Rotate the
registered order by the block index modulo four; reverse its base order on odd
groups of four. Across 32 blocks, each candidate occupies each position eight
times. This predetermined balance motivates the change from 31 to 32 blocks.
No V2 timing is pooled with V3 and no cross-run speedup is inferred.

Remove a candidate only when another candidate's upper endpoint is at most its
lower endpoint in every resource coordinate, strictly so in at least one.
Report all survivors, their families and every domination edge. One surviving
family licenses only that family at this scope; several survivors in one family
do not license a unique candidate winner. If both families survive, abstain.
Synthetic controls include ties, crossed intervals, an improved neural winner,
a mixed-family reopening and malformed or missing evidence.

The registered expectation is that the frontier contains only non-neural
candidates. It is informed by V1/V2 and is **not independent prospective
replication**. Any surviving neural candidate falsifies this expectation;
instrument or capability failure invalidates the packet. Every first-run
outcome is retained. The main-push workflow cannot time on a PR, and the harness
rejects later run attempts. Source, schedule and decision rules cannot be changed
after reading results within this version. A new scientific question or repair
requires a new registration.

## Claim boundary

The expansion discharges the concrete addition-and-comparison obligation for
these two new constructions only after validated execution. It does not prove
coverage of all optimized neural implementations. The requirement for independent
external candidate optimization, further tasks/substrates and prospective
replication remains open. Development and authoring costs remain excluded from
selection. Timing intervals are observed envelopes of this execution, not
population confidence bounds. Static proofs and deterministic instrument checks
are permitted before freeze; no protected timing was used to choose candidates.
