# Mechanical proof environments

This package reconstructs a permitted Lean environment from native kernel data and
checks a supplied proof expression against an independently registered target.
It supports the next masked-proof reconstruction experiment. The authored fixtures
are engineering controls; they are not evidence of proof search, learning or FLT.

The cognitive restriction is explicit: no neural model, neural proposer or neural
teacher in a scored OCM episode. Future learning must persist executable facts,
relations, methods, operators, representations or search policies.

## Read first

- [Qualified result](RESULT.md): 47 registered controls, measured scope and next gate.
- [Qualification layers](QUALIFICATION.md): native controls and portable evidence audit.
- [Contract](CONTRACT.md): what authorizes the goal, primitives and result.
- [Protocol](PROTOCOL.md): operations, isolation, qualification and cost scope.
- [Design](../../docs/plans/2026-09-07-proof-environment-design.md): mechanism choice.
- [Implementation plan](../../docs/plans/2026-09-07-proof-environment.md): acceptance work.

## Mechanism

1. Export the evaluator's source environment using the pinned native exporter.
2. Independently register a declaration-free target packet, its expression root
   and ordered universe parameters, allowed roots, excluded declarations and axioms.
3. Prepare a dependency-closed permitted packet. Compare primitive identities,
   reject excluded dependencies, and reconstruct checked declarations from empty
   kernel state. Rebuild tables so unreachable private expressions are omitted.
4. Start a separate checker with only permitted data, the independent target,
   registration, primitive packet and candidate expression packet.
5. Insert a checker-owned theorem with the registered type through the kernel's
   checked declaration API. Only actual kernel success can yield `KERNEL_PASS`.

The checker receives explicit typed expressions. It runs no source elaboration,
notation expansion, tactics, instance search or arbitrary candidate declarations.
It is not an unrestricted Lean source execution service.

## Qualified launch

Use the independently registered Python executable and `-I -S`. All builds and
execution belong on laptop billy. The Mac is for source/document edits and metadata.

```sh
python -I -S environment.py prepare \
  --freeze /absolute/prepare-freeze.json --freeze-sha256 <authorized-sha256> \
  --runtime /absolute/runtime.json --runtime-sha256 <authorized-sha256> \
  --output /absolute/new-prepare-attempt

python -I -S environment.py check \
  --freeze /absolute/check-freeze.json --freeze-sha256 <authorized-sha256> \
  --runtime /absolute/runtime.json --runtime-sha256 <authorized-sha256> \
  --output /absolute/new-check-attempt
```

Inspection uses the first command with an `inspect` freeze. Existing output
directories are never reused. Digests must come from the evaluator's approved
registration, not be accepted from a candidate as their own authority.

`PREPARED` and `INSPECTED` are preparation/inspection results. `REJECTED` is an
explicit native refusal. `CANNOT_CHECK` includes incomplete native support, invalid
custody, infrastructure and incomplete evidence; inspect its stage and reason.
No refusal caused by broken execution counts as a semantic negative control.

## Scientific use

After native qualification, measure real-corpus semantic coverage, then register
masked-proof episodes with complete withholding and independently checked targets.
Compare fresh-task performance before/after explicit method acquisition, including
equally informed and equally adaptive symbolic parents. Charge acquisition,
compilation, retrieval, revision, search, checking and retained storage.

Native packet support is not novelty. This implementation absorbs lean4export and
Lean's checked replay, with comparator mechanisms where applicable. The potential
OCM result must come from measured persistent acquisition and future-task benefit.
