# #1068 constructive synthesis: start here

This successor synthesizes executable expressions from the grammar
`x | y | NAND(t,t)`, rather than selecting from supplied family templates.
It obtains all 16 binary Boolean functions and certifies minimum expression
size over the infinite expression grammar. A stack compiler preserves results
and counts one target instruction per expression node.

These are scoped synthesis and translation results, not derivations of every
machine-intelligence family. Grammar, Boolean inputs, exact truth-table
semantics, equality checking, search order and unit node costs are supplied.
The exploratory result was known before the successor protocol was frozen;
[the freeze](FREEZE_V6.md) discloses that chronology.

## Read core, then detail, then evidence

- [Theory and proof boundaries](THEORY_V6.md): certificate induction,
  compilation, operational simulation and the broader coverage contract.
- [Parent attribution](PARENTS_V6.json): established Boolean construction and
  compiler-correctness methods; this work does not claim their invention.
- [Search implementation](synthesis_v6.py) and [stack machine](machine_v6.py).
- [Independent oracle](independent_oracle_v6.py) and
  [hostile tests](test_synthesis_v6.py).
- [Replay driver](check_synthesis_v6.py) and [receipt](RESULT_V6.json).

The compiler guarantee is preservation of the *entire* existing stack plus
one result. Python stacks are bottom-first; the Lean presentation uses the
reverse list, with the same top element. This representation difference
does not reverse source operand evaluation.

## Reproduce on laptop billy

Use Python 3.12. Run from the repository root on laptop billy:

```sh
P=research/gmi-1068-synthesis-v6
/home/billy/.local/bin/python3.12 -I -B "$P/check_synthesis_v6.py"
/home/billy/.local/bin/python3.12 -I -O -B "$P/check_synthesis_v6.py"
```

The driver loads reviewed sibling modules explicitly. Direct isolated execution
of the test module need not resolve those imports. Lean 4.19.0 checking is a
separate workflow step; Python replay does not certify Lean.

## Scope of costs and search

The default search reports actual relaxation rounds, pair evaluations, inserted
semantic classes and strict witness improvements. These are implementation
operation counts, not measured wall-clock, acquisition, validation, memory or
lifetime efficiency. Source node count counts repeated subexpressions twice;
it is a formula-tree cost, not minimum shared-circuit size.

Search with a reduced terminal set or disabled NAND changes the grammar.
Saturation in such a grammar does not establish all-function completeness.
The full certificate rejects missing functions, incorrect witnesses,
wrong costs and failed composition inequalities.

The process and costing assumptions remain explicit. All 222 programme
requirements retain their registered identities and conservative status;
a local constructive result does not make the complete R0–R17 theory earned.
