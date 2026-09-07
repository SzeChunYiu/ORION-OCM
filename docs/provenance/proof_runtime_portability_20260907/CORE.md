# Proof/runtime portable test repair

The executing engineering interpreter now supplies the lifecycle test binding.
Production lifecycle sources and the archived native result are unchanged.
This is a test portability result, not a new native or scientific qualification.

## Result

| Execution | Result |
|---|---|
| PR #134 hosted job 101593120557 | 7 failures from unavailable laptop Python/stdlib |
| Fresh separate Linux Python, original tests | 5 failed, 91 passed; no skips |
| Same environment, repaired tests | 97 passed; no skips; pytest 19.13 s |

The local reproduction uses a different resolved CPython 3.11.14 installation.
The old laptop interpreter remains present, so this reproduces the path mismatch,
not every aspect of the hosted filesystem. A new hosted head must still pass CI.
The recorded green subprocess wall is 20.210119746 s, including pytest startup.
Environment acquisition/setup costs are not included or presented as lifetime cost.

## Change and controls

Only `research/proof-runtime-v1/test_lifecycle_contract.py` changes executable tests.
Its helper passes `Path(sys.executable)` explicitly without modifying production
`L.PYTHON`, `run` defaults, interpreter equality or source/import checks.
The real cold-status control also checks the executing interpreter's stdlib hash.
A different registered interpreter must refuse before any worker/checker dispatch.
Candidate mismatch, source drift, no-rebind, status purity and cleanup controls remain.

The suite mocks native proposer/kernel boundaries. Its existing real cold reader
restores mocked proof artifacts only; it performs no new native proof or learning.
The 192 production sources bound by the original native freeze still hash exactly.
The changed test bytes receive this additive record; historical 96-test evidence
and test snapshots retain their original identities and are not rebound.

## Evidence

- [Record, exact commands and scope](RECORD.json)
- [Hosted failed-step log](raw/hosted-portable-failed.log)
- [RED process](raw/red-process.json), [log](raw/red-stdout.log), [JUnit](raw/red-junit.xml)
- [GREEN process](raw/green-process.json), [log](raw/green-stdout.log), [JUnit](raw/green-junit.xml)
- [Executing environment](raw/environment.json)
- [Original test bytes](test-source/before.py), [repaired bytes](test-source/after.py)
- [Unchanged native source bindings](raw/native-source-custody.json)
- [Native qualification and its separate scope](../../../research/proof-runtime-v1/QUALIFICATION.md)

[Inventory](INVENTORY.json) hashes every archived file except itself and the seal.
[Seal](SEAL.json) binds that inventory. All copied logs/JUnit retain original bytes.
