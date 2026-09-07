# Authored acquisition and Lake qualification

Read first: this package preserves engineering qualification. It does not report
real corpus acquisition, semantic coverage, hidden-region reconstruction or learning.
Actual material episodes, including the initial missing-helper failure, have separate
root-owned records and must not be inferred from these authored controls.

## Current results and history

| Evidence | Observed result | Authority scope |
|---|---|---|
| Git worker, final | 25 passed; zero failures/skips | Fixed lock, isolated Git invocation, byte custody and authored local transports |
| Phase04, historical | 29 passed; zero failures/skips | Six-source predecessor, before the frozen-helper readiness repair |
| Phase05, repaired | 31 passed; zero failures/skips | Ten-source successor including missing-helper and actual-helper preflight controls |
| Frozen helper smoke | FROZEN_ACQUISITION_HELPER_SMOKE_PASS | Actual protected controller setup and clean authored child exit; no fetch |
| Lake fixture, final | 14 passed; zero failures/skips | Local fixture/presence/refusal mechanics |
| Lake actual run06 | AUTHORED_LAKE_BUILD_PASS | Two authored packages built offline to .olean and emitted C source |

These are different checks, not an additive score for scientific competence.
The worker's private local-fixture transport does not enable file URLs in production.
The actual fixed 3,158-byte corpus lock independently validated all nine resolved rows.

Phase04 and phase05 snapshots are distinct. Both source sets are retained under
source-generations/ inside the archive and indexed in
[SOURCE-GENERATIONS.json](acquisition-qualification-records/SOURCE-GENERATIONS.json).
The qualified production worker/helper remain SHA256 81e13646…/ce7c0b52…;
the phase orchestrator changes from e8758c5a… to 10164b74… for helper inclusion.

## Compact artifact

Start with [CORE.md](acquisition-qualification-records/CORE.md) and
[INDEX.json](acquisition-qualification-records/INDEX.json).

| Artifact | Size / identity |
|---|---|
| [qualification.tar.gz](acquisition-qualification-records/qualification.tar.gz) | 2,962,776 bytes |
| Archive SHA256 | 678a991fdd6fc077f4d8a987a49a2bbb1542801a90e03c11df3080f2e90c485e |
| Archived regular files | 1,339 members; 11,468,546 raw bytes |
| [Member map](acquisition-qualification-records/qualification.members.json) | 255,508 bytes |
| Member-map SHA256 | 61a08902bdc9f3f0d7dc4011b63d69db112d03f8c82ee9e7b96b363bf4bda686 |

The archive retains all regular files from worker, phase, helper-smoke, Lake,
independent Lake review and lock-input qualification roots, plus the prior exact
runtime manifest and explicit phase source snapshots. No original file was changed.
[ORIGINS.json](acquisition-qualification-records/ORIGINS.json) maps every member to
its original path. [VERIFY.json](acquisition-qualification-records/VERIFY.json)
records stream readback equality and a final original-source/file-set comparison.

The deterministic gzip/tar uses sorted regular members, normalized 0644 metadata and
zero timestamps. It is an evidence container; its contents are not executed.
The common archive recipe and full JSON SHA256/byte map are retained. No new general
auditor framework or experiment was introduced.

## Raw record map

| Prefix inside archive | Main records |
|---|---|
| worker/ | final.json/xml, final-source/, authored-fixtures/, pinned-lock-no-alarm.json; RED and intermediate logs |
| phase/ | phase.02–05 process/stdout/stderr/XML records; fixture-error/intermediate history retained |
| phase-initial/ | earliest contract-control record |
| source-generations/ | Exact historical phase04 and repaired phase05 file sets |
| helper-smoke/ | SOURCE-FREEZE.json, sources/, actual run resource receipt/raw streams, RESULT.json |
| lake/ | Original schema refusal, diagnosis, corrected profile, actual run06 and assessment, 14-test controls, custody/costs |
| lake-review/ | Independent read-only review and reviewer-only canonical-JSON correction note |
| lock-input/ | Exact corpus lock and its metadata extraction receipt |
| external-bindings/ | Prior runtime-manifest.json with complete installed-file/archive identities |

## Explicit omissions and cost boundaries

[OMISSIONS.json](acquisition-qualification-records/OMISSIONS.json) names 45 externally
bound files whose bodies are not copied or revalidated by this packaging step,
including installed tools/libraries, CA material and a prior profile reference.
It retains every available exact hash/size binding. Seven pytest symlink aliases and
one authored FIFO refusal fixture are inventoried but neither followed nor read.

The installed Lean distribution remains external: 18,129 inventory entries,
17,493 regular files /3,037,354,159 bytes. Its existing 570,405,234-byte archive is
bound by SHA256 890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235.
This packet retains the exact manifest; it does not requalify that installation.

The worker final outer process took 0.678348723s; phase04 took 0.571538936s and
phase05 took 0.627555873s. These are independent authored test processes.
Helper smoke reports 0.153570365s. Lake's successful host process took 7.295236720s;
its 7.259615958s profile and 0.713115788s controlled workload are nested, not additive.
Lake memory high-water was 205,385,728 cgroup bytes; RSS was unavailable.
Preparation/refusal/correction history remains in the raw records; this is not a
complete lifetime cost or a speedup result.

The supplied reflexivity theorem, value and imported application were authored
fixtures. Native linking, generated plugins, real corpus configuration closure,
proof-region reconstruction and learned transfer remain separate gates.
