# Reproduce the terminal-cost result

Run scientific verification on laptop billy, using exact Python arithmetic:

```sh
python -I -B test_terminal_cost_v1.py -v
python -I -O -B test_terminal_cost_v1.py -v
python -I -B check_terminal_cost_v1.py
python -I -O -B check_terminal_cost_v1.py
```

The checker emits the complete JSON receipt; compare the entire decoded
payload with `TERMINAL_COST_RECEIPT_V1.json`. A terminal `PASS` field alone
is insufficient. The grand integration separately binds every packet file
and isolates imports from ambient bytecode caches.

`terminal_kernel_v1.py` builds the full terminal profile set or its antichain
at every subcube, then keeps actual action-labelled tree witnesses.
`syntax_parent_v1.py` independently enumerates every no-repeat source tree
without adequacy pruning and executes it on every admitted input. Its own
dominance implementation checks the kernel's frontier against that complete
parent. The strongest parent and repaired mechanism use the same input,
adequacy, charge and action interface; the construction does not gain a free
input-conditioned action oracle.

The scalar census spans every two-action relation, including empty rows,
on cubes with n=0,1,2, and every binary input/action terminal cost table. It
uses fixed query charges 1 and 2 where those coordinates exist. Separate
two-resource tests exhaust every binary 2-input/2-action cost tensor, every
relation and all four binary query vectors. Rational, zero-charge and
zero-probability-obligation controls are included separately.

Reported `candidate_tree_executions` counts whole candidate policies assessed
on inputs, including inadequate policies that fail early. It is not native
execution work, syntax generation time or the count of successful policies.
The scalar kernel counters cover subproblem visits, child pairs and generated
profile entries. They omit cost-table acquisition, kernel formation, dominance
comparisons, arithmetic bit complexity, allocation and implementation costs.
The vector census has its own instance count and digest and is not included
in the scalar operation totals. Action-permutation checks are additional
same-interface reconstruction controls, not independent scientific datasets.

Source unit and raw parent bindings are in `MANIFEST.json`. Historical RQR
source is copied unchanged under `raw/` for precise scope comparison. Tests
perform no ecology search, fitted statistical inference or physical timing.
