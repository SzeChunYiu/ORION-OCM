# Encoding-only timeout diagnostic successor

**Prepared; public successor tasks have not run.** Use [LAUNCH.json](LAUNCH.json)
only after root registration. [manifest.json](manifest.json) binds the unchanged
three requests, order, solver options, resources, supervisor and source checkout.

The v4 recorder completed its fourth invocation, then failed while serializing
native statistics containing NaN. Primitive routes completed synth-fun; the
macro route completed its helper define-fun. No constraint or check-synth was
dispatched. All three remained CANNOT_CHECK. Its complete capture and original
source are preserved and bound here.

The successor changes only statistics encoding: nonfinite float values become
explicit {"$cvc5_float":"NaN"}, "+Inf" or "-Inf" tags. Every native entry/name,
finite value and existing statistic flag remains. Nothing becomes zero or is
dropped. A reserved tag collision refuses rather than becoming an ambiguous
value. All other serialization errors remain visible errors.

[QUALIFICATION.json](QUALIFICATION.json) links the actual harmless native
constant-definition control and synthetic controls. Full native repr is written
before either serializer. The original strict serializer fails on four NaNs;
the tagged form round-trips native keys, finite values and nonfinite classes.
Synthetic NaN and both infinities, signed zero and ordinary values also pass.
The seven existing boundary controls pass on the successor.

This control uses three setup commands and one harmless constant definition:
zero synth-fun, constraint, check-synth, Z3 or Stitch calls. Its named NaNs are
new control observations; they do not recover v4's unrecorded offending snapshot.

The prospective task inputs remain byte-identical quoted-v2. Each retains 5 s
native timeout, 20 s outer deadline plus 2 s kill grace, CPU 0 and 4 GiB address
space. Diagnostic logging can change runtime. Boundaries identify public calls
only; no efficiency, internal-stage, learned-abstraction or cognition claim.

V4 freeze: https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560004928
Source basis: https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5559798070
The v4 seal remains 115ed5807c06a75f2415ff4b9d9530d320ad09c5efd8e4bf2890cf195f0cacdd.
