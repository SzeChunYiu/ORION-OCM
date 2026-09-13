# Operations and integration map

Use CPython with the declared 3.12 opcode layout and standard library only.

~~~sh
python3 -I -B check_structural_threshold_repair_v1.py
python3 -I -O -B check_structural_threshold_repair_v1.py
python3 -I -B -m unittest discover -s . -p 'test_structural_threshold*_v1.py'
python3 -I -O -B -m unittest discover -s . -p 'test_structural_threshold*_v1.py'
~~~

A compatible native checker emits every field of the frozen portable receipt.
An incompatible opcode layout returns exit2 with UNVERIFIABLE on stderr and
no success payload. No invocation launches the historical whole-grammar search
or an ecology/timing experiment.

For grand integration, copy these files byte-exact:

- structural_threshold_analytic_v1.py
- structural_threshold_costs_v1.py
- structural_threshold_geometry_v1.py
- structural_threshold_countercontrols_v1.py
- test_structural_threshold_analytic_v1.py
- STRUCTURAL_THRESHOLD_ANALYTIC_CORRECTION_V1.md

The existing grand SN checker can become a thin adapter that calls
structural_threshold_analytic_v1.run() and serializes its ENTIRE result.
Register the new complete result under a new grand V2 receipt. Preserve the
original V1 receipt as historical. Bind all helpers and normative proof in
the grand inventory. Keep the source archive unit as a separately bound packet.
No helper reads directory globs, absolute paths, parent receipts or its own hash.

test_structural_threshold_analytic_v1.py contains18 portable scientific tests.
The separate test_structural_threshold_packet_v1.py contains5 standalone
archive, whole-payload and relocation tests; it stays beside the raw packet.

The original five #557 files are byte-exact under raw/. Their source register
and the final manifest bind them without replacing them.
VALIDATION_V1.json identifies the native executions; the portable receipt does
not assert their host, binary, historical timing, or patch identity.
