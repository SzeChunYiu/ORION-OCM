# TTAC-D5 — External Cognitive Input / Autonomy Ledger

Owner issue: #277 §4. Artifact: `EXTERNAL_COGNITIVE_INPUT_LEDGER.jsonl` (JSONL, append-only).
Opened 2026-09-10. Frozen schema: `READINESS_SCHEMA_V1.json`, `TAXONOMY_FREEZE_V1.md`.

## What this artifact is for

#277 §4 forbids any self-development or self-evolution claim without an audit that separates
**externally supplied cognition** from **inherited or internally discovered** cognition. This
ledger is that audit. It is deliberately hostile to the programme's own most attractive claim.

## Structure

Line 1 is `LEDGER_META`, the last line is `LEDGER_VERDICT`, and the rows between are entries.
Each entry carries the #277 §4 fields: time, round, source identity and class, a content hash or
bounded description, the target atom, whether the system could access the input, whether it changed
`F`/`O`/`Π` or only research infrastructure, the claimed causal role, and a re-checkable anchor.

Two vocabulary decisions are worth stating explicitly:

- **`system_could_access`** asks whether the OCM under study (`M_t = (F_t, O_t, Π_t, C)`) could itself
  read the input. `false` means the input entered the research programme *around* the OCM. This is the
  distinction that decides whether an entry bears on the OCM's autonomy or only on the programme's.
- **`changed: EVALUATION_INSTRUMENT`** is separated from `RESEARCH_INFRASTRUCTURE_ONLY`. A measurement
  fix applied inside a scoring window is a construct-validity event, not a search result, and collapsing
  the two would hide exactly the kind of thing §3's hostile programme exists to catch.

## Coverage boundary — read this before citing the ledger

The audited window is **2026-09-09T12:28:15Z to 2026-09-10T10:20:00Z**. Everything before it is
`UNKNOWN` and is carried as an explicit placeholder row (`ECI-0012`) rather than left blank.

> Absence of an entry before the window is **not** evidence that no external cognitive input occurred.

Historical reconstruction was not performed because it requires auditing prior session transcripts and
the full issue history. Per the D5 rule, entries are reconstructed only where direct evidence exists;
nothing here is inferred from memory or plausibility. Every entry has a durable anchor: a transcript
line plus the sha256 of the exact directive text, or a merged PR and commit.

## Verdict in the audited window

Twelve entries. **Zero changed the OCM's own `F`, `O` or `Π`.** Ten changed research infrastructure,
one changed an evaluation instrument, one is the historical `UNKNOWN` placeholder.

The three inputs that matter most are all human-authored and all external:

| Entry | What was externally supplied |
|---|---|
| `ECI-0003` | The optimization target itself — the system did not choose the objective it is graded against. |
| `ECI-0004` | The entire grading machinery of #277: the readiness vector, the ladder, the classes, the terminals. Every downstream readiness score inherits it. |
| `ECI-0005` | The parent set under first refusal, enumerated by name. The parent search was seeded externally. |

`ECI-0007` records that this ledger is itself AI-authored, so the auditor is not left unaudited.

### Consequence for the `A` coordinate

The frozen rule is *autonomy unaudited ⇒ no self-development/self-evolution claim*. The audited window
contains no system-originated change to `F`/`O`/`Π`, so **`A` cannot be lifted by this ledger** for any
`DEVELOPMENTAL_LINEAGE` or `SELF_EVOLUTION` atom. `A` stays gated.

This is a negative governance result and is retained as one. It is not a defect in the ledger and must
not be engineered away; it is the ledger working.

### What would lift it

A `SYSTEM_SELF_DISCOVERY`, `SYSTEM_SELF_DIAGNOSIS` or `SYSTEM_SELF_PROPOSAL` entry whose target is a
change to `F`/`O`/`Π`, produced *without* an upstream `HUMAN_*` or `AI_THEORY_INPUT` entry supplying the
same content, and bound to a prospectively frozen protocol.

## Claim ceiling

This ledger supports statements about the **research programme's** autonomy only. It does not measure,
and must not be cited to support, any claim about the OCM's self-development.

## Non-final

Append-only. Amendments may lower a claimed causal role or add entries; they may not retroactively
convert a `RESEARCH_INFRASTRUCTURE_ONLY` entry into a system-originated one without new evidence.
