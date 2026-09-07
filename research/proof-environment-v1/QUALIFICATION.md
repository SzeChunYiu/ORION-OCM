# Qualification layers

The [native result](RESULT.md) and [retained records](records/RECORDS.md) are the
scientific apparatus authority. Different control layers below are not independent
solved-problem counts and must not be summed into a capability result.

| Layer | Executed scope | Retained evidence |
|---|---|---|
| Native unit controls | 45 controls across six executables | [Development record](NATIVE_DEVELOPMENT.md) and development-history archive |
| Native development process matrix | 29 prepare plus19 check operations | Development-history archive; final v4 handoff |
| Runtime profile | Two traced actual prepare/check operations | Final-profile and runtime-authority archives |
| Final isolated commissioning | 47/47 registered controls;14 kernel passes | Complete final681-file archive and final seal |
| Python driver/recorder/package controls | 53 combined passes, then one added interruption control;54 distinct current controls | Development-history logs: python-integrated-v2 and recorder-interruption-v1 |
| Portable existing selection | 30 passes | Development-history portable-ci-selection-v1 log |
| Portable archive/source guard | 40 passes plus actual full-record no-alarm CLI | [Audit qualification](qualification/AUDIT_QUALIFICATION.json) |

The host-specific package controls use the qualified laptop runtime prerequisites.
Hosted CI selects the30 portable driver/recorder controls plus40 audit controls;
it does not claim to rerun native Lean or validate omitted ELF payloads.
Exact PR-head hosted results must be observed before merge.

## Audit the retained result

From the repository root, with Python3.11:

```sh
python -I -S research/proof-environment-v1/audit_evidence.py
```

The qualified no-alarm run returns `RETAINED_EVIDENCE_AND_SOURCE_BINDINGS_PASS`:
seven archives,3,992 members,681 final files,47 registered controls,14 kernel passes,
47 recorded native process envelopes and36 current source bindings. It checks the
fixed final seal, complete archived membership, registered row causes, raw streams,
issuer/environment links, input copies, invocation/mount records and source bytes.
It reads current repository/archive files only, not the recorded absolute host paths.

Those36 current bindings cover runtime/build/recorder source. Other fixture and
development sources in the archives are historical records; this is not a freeze
of every file in the current repository. Successful auditing does not repeat the
native run, attest present external binaries or establish historical host security.

The audit tests include real-data acceptance and targeted changes to archive
membership, JSON, source bytes, final-seal authority, row identity, expected cause,
issuer, input, raw streams, process cleanup and mount bindings. Initial development
failures and subsequent successful logs remain in `qualification/`.
Root independently reviewed the four audit modules. Native/driver/recorder review
and the preparation-versus-checker scope correction were completed separately.

## Requalification rule

Retain this historical result unchanged. A production change requires a separately
identified successor and appropriate new native controls. A changed audit or test
must receive its own actual qualification; it cannot rewrite the original seal.
Moving the native runtime also requires provisioning and validating its measured
executable/dependencies. The portable evidence audit is not a substitute for that.
