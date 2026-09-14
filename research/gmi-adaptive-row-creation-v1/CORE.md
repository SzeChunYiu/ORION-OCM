# Adaptive row creation

Extends ARC-1–6 to dynamically created rows. An agent may create new rows
based on observed data, and the simultaneous confidence event remains valid
over every row at every visit, including rows born after the process starts.

- [Formal theorem](ADAPTIVE_ROW_CREATION_THEOREM_V1.md)
- [Small-world witness](row_creation_witness.py)
- [15 controls](test_row_creation.py)

Parents: [ARC-1–4](../gmi-adaptive-row-confidence-v1/ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1.md),
[ARC-6](../gmi-countable-row-corrigendum-v1/FORMALIZATION_V1.md).
Issue #592 item 32. G2 scoped mathematical mechanism, not G6 capability.
