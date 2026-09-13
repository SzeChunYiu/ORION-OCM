# Validation at the declared static scope

CPython 3.12.13 on billy-laptop passed **22 tests normally and 22 with -O**,
with no failures, errors or skips. The actual binary and tested Python source
hashes are recorded in [VALIDATION_V1.json](VALIDATION_V1.json).

The tests include 437 independent graph-role/ancestry comparisons against
real retained data, the original probe's actual AFFINE false negative, data
versus parameter ports, EDGE routing, off-OUTPUT-ancestry scope, GRAD parameter
updates without incoming DENSE edges, missing-source abstention, false source
fingerprints, altered original-witness identity, invalid primitives/ports,
source/archive mutations and unsafe archive members.

A copy of this complete unit in a temporary directory with no Git repository
reproduces the full frozen receipt in both modes. Added unbound files and
modified receipts fail complete membership/hash verification. The standalone
replay uses a new isolated process and private bytecode prefix. It retains the
exact initial manifest and expected receipt across the worker. A mocked worker
that edits CORE and rehashes its manifest row is rejected even while returning
the unchanged full receipt; this countercontrol performs no census calls.

The science/code was independently reviewed by the unmerged-audit peer,
including the native evaluator, cohort selection and chosen-source limits.
A green result is static custody/classification evidence. No search, ecology,
training, priming or timing experiment was performed by this unit.
