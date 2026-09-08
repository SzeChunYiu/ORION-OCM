# G2/G3 parity maintenance and cost erratum

The additive parity helper rejects empty row populations and unequal lengths.
Seven new authored controls pass; unchanged old helper bodies reproduce ten
expected failing subcases. Historical G2/G3 sources, workflows and results remain
unchanged. No study, retained-task evaluation or native execution was rerun.

[Caller API](API.md) → [cost wording correction](COST-ERRATUM.md)
→ [qualification](QUALIFICATION.md) → [source/helper](row_parity.py).

G3 pins the complete historical G2 file and has its own copy of the defective
zip-based guard. The helper exposes their two existing field schemas separately.
This repair is ready for explicit use by a future versioned caller; it does not
silently alter or requalify either frozen study. [Evidence](EVIDENCE.md).
