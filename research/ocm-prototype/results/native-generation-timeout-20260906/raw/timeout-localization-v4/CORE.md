# Timeout localization: read first

**Prepared; the three public tasks have not run.** Root registration and explicit
launch remain required. This adds command-boundary observation to the existing
capture supervisor. It does not change task text, grammar or solver algorithms.

## Launch

Use [LAUNCH.json](LAUNCH.json), bound to [manifest.json](manifest.json).
The source checkout stays at b03b74905a331bf40af16f1531bb5f2b58821ba2.
[PROPOSAL.json](PROPOSAL.json) preserves quoted-v2 requests in this order:
implicit primitive, explicit primitive, full manual macro. The forced control
is outside this diagnostic. Each has native 5 s, GNU timeout 20 s plus 2 s kill
grace, CPU 0 and 4 GiB address space; existing supervisor watchdog is 24 s.

## What the recorder establishes

The new worker records separately flushed parse, command metadata, invoke,
statistics collection and statistics serialization boundaries in a JSONL file.
Returned command text is preserved before statistics. Native diagnostics remain
on stderr and final command-return JSON on stdout. All assigned raw files,
failures and timeouts are sealed by unchanged capture.py.

Added native tags are options-auto, sygus-grammar and sygus-enumerator; the
original sygus-sol-gterm input option remains. Full statistics explicitly include
internal and defaulted entries. Effective getter values are snapshots only.
The output-tag getter is unavailable in pinned cvc5; successful setters are
recorded, and cannot substitute for actual native diagnostic emission.

An unmatched check-synth invoke-begin localizes only an unfinished public API
call. It does not identify enumeration, reconstruction or another internal phase.
Missing markers do not prove a phase never ran. Pre-call statistics are not
timeout statistics; hard-killed calls have no final snapshot. sygus-grammar
prints automatically generated grammars, so absent explicit-grammar output is
not evidence of failed parsing. Logging can alter runtime; no timing comparison
or efficiency, learned-abstraction or cognition claim follows.

## Qualification and preserved failures

[QUALIFICATION.json](QUALIFICATION.json) links every control generation.
The final seven harmless stub cases pass. Actual cvc5 setup completes exactly
set-logic, output tag, and quoted output routing, with three 61-entry statistics
snapshots and clean EOF. There are zero synth-fun, constraint, check-synth,
Z3 or Stitch calls in this qualification.

Two real observer defects were preserved: ungettable output option during
statistics, then a null-command name lookup at EOF. Each received one narrow
correction. Original sources and sealed negatives remain here. No public input
was executed or changed while qualifying these repairs.

Source basis: [registered diagnostic design](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5559798070).
The prior [four-case result](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5559739984)
and its unresolved explicit-primitive invocation remain unchanged.
