# Grand Unified GMI V2 — R8 civilization-blind neural-family back-test freeze

Issue #1068; R8. Stacked parent: exact R7 head 1c11d778b6a5ef0eab233146594cecab17cebed2.

Freeze precedes R8 outcome implementation.

## Causal blindness contract

The generator/selector is forbidden from using neural/network/layer/activation/ReLU/backprop/attention/convolution or any family label. Candidates are represented only by generic arithmetic/order/process constructions and exact external behavior/resource cost.

Post-hoc classification runs only after a winner/frontier is selected.

## Frozen ecology family

Input domain is every integer x in [-32,32].
Each world is a continuous piecewise-affine scalar map with fixed external knots -8 and 8, slopes
s0,s1,s2 in {-2,-1,0,1,2}, and value f(0) in {-1,0,1}.
All 5^3 * 3 = 375 worlds are included; no outcome-based filtering.

The family therefore contains:
- 15 globally affine worlds (zero slope jumps);
- 120 worlds with one nonzero adjacent slope jump;
- 240 worlds with two nonzero adjacent slope jumps.

## Two source-separated derivation presentations

A. slope-jump arithmetic normal form, with hinge derived from generic order/arithmetic;
B. explicit piecewise branch/segment normal form.

Both must reproduce every world exactly on all 65 registered points.

A second semantic remint implements positive-part via absolute value:
positive_part(z) = (z + |z|)/2.
The causal code may call this only generic arithmetic/ABS; neural terminology is post-hoc.

## Frozen competing realization costs

Horizon H=16.

Build costs:
AFFINE=3;
BRANCH=8;
HINGE(k)=2+2k;
TABLE=65.

Substrate S_ARITH:
affine per-use=2;
branch per-use=18;
hinge per-use=2+7k;
table lookup per-use=15.

Substrate S_BRANCH:
affine per-use=4;
branch per-use=6;
hinge per-use=4+15k;
table lookup per-use=4.

Selection scalar for this registered comparison only:
C = build + H * per_use.
Raw representation/cost records remain committed.

Frozen qualitative predictions:
- globally affine worlds select the affine construction in both substrates;
- non-affine worlds select hinge/arithmetic composition under S_ARITH;
- non-affine worlds select branch/rule construction under S_BRANCH;
- table should not be the winner under these frozen prices;
- only after selection may HINGE be mapped post-hoc to a shallow rectified weighted-sum network form.

## Blindness limitation

This emulates a civilization-level causal information barrier but was designed by researchers who historically know neural networks. It may earn CAUSALLY_ARCHITECTURE_BLIND_RECOVERY, not literal proof of human historical ignorance.

## Claim ceiling

GRAND_GMI_V2_R8_CAUSALLY_ARCHITECTURE_BLIND_NEURAL_LIKE_RECOVERY_WITH_SUBSTRATE_INVERSION_AT_REGISTERED_CPWL_SCOPE

Forbidden: LITERAL_CIVILIZATION_HISTORICAL_IGNORANCE_PROVED, NEURAL_UNIQUENESS, NEURAL_INEVITABILITY, REAL_SCALE_NEURAL_OPTIMALITY, FULL_GMI.
