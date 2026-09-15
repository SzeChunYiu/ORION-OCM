# Four-family cross-grammar neutral recovery v1

## Protocol

Grammar A directly enumerates finite transition/output tables, feature/address
tables, read-address policies, and weighted/row representations.  Grammar B
instead enumerates Boolean register expressions, reusable local expressions,
branch-address programs, and Boolean-expression/leaf-tree programs.  Their
candidate spaces are not in one-to-one correspondence and their interpreters
share no evaluator.  Serialized candidates contain no architecture/family
names.  Search sees exact task output and explicit description cost only;
phenotype labels are assigned after selecting a raw winner.

Four positive ecologies and matched twins are exhaustive at their stated
finite scopes:

1. even-length unary sequences versus a constant-output twin;
2. one shared ring law versus alternating site laws;
3. varying input-supplied read address versus fixed address zero;
4. an unstructured three-bit key map versus a single-coordinate rule.

## Executed result

Both grammars recover the same four positive phenotypes:

- `RECURRENT_STATE`;
- `SHARED_LOCAL_UPDATE`;
- `INPUT_INDEXED_ROUTING`;
- `KEYED_STORAGE`.

In every matched twin both grammars select a cheaper phenotype with a different
post-run classification.  This rules out a classifier that returns the same
family regardless of ecology.  The checker also rejects family-name tokens in
the raw candidate serializations and requires all eight positive/twin flips.

## Claim ceiling

This is P2 finite-exact recovery across two independently structured grammars.
It is not a real learning-scale result, cross-author replication, universal
search invariance, or evidence that these four families are novel.
