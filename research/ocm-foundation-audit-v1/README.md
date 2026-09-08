# OCM foundation audit v1

Implementation-facing theory and an independent mathematical checker for the frozen #191 G2 utility-tournament receipt. Programme spine: #165. This is an additive qualification, not a new experiment, runtime deployment or declaration of OCM completion.

Start with [FOUNDATION.md](FOUNDATION.md) for six scoped propositions, the invariant-preservation obligation, causal-use and lifetime economics, implementation bindings, primary literature, and the G1-G8 gap disposition.

## Verified outcomes

The retained study remains `UTILITY_TOURNAMENT_SELECTS_NO_METHOD`; all 16 candidates failed its utility gate. The best validation candidate cost 184,965 search slots against the primitive parent's 122,787. No method was deployed. Every 64-task test arm cost 903,871 slots. The fully charged search-slot path cost 4,498,404; no lifetime search-slot payback was observed.

`audit_g2.py` independently reconciles every task identity, complete arm, first solution, stream origin, candidate ranking and search-slot ledger. It closes the qualification gap left by the frozen experiment's prefix-only `zip` comparison, without rewriting historical source or results. It does not certify actual runtime authority, physical custody, cold-process restart, physical-resource cost or generalization.

## Validation

[Local evidence](EVIDENCE.json): 42 authored controls passed normally and with `-O`, plus retained-receipt reconciliation. Local production differential controls were not run without a checkout.

[Hosted evidence](HOSTED_EVIDENCE.json): run `34280879325`, tested commit `55d9c1237ded3485e23fa90ba9e6582dcf3d5b3f`, completed successfully. All **45 controls passed normally and with `-O`**, including three source-pinned production-refinement controls. The exact retained artifact also reconciled. This is independently implemented checking, not independent authorship or a new protected replication.

```sh
# From the repository root:
PYTHONPATH=src:research/ocm-foundation-audit-v1 \
  python -B -m unittest discover -s research/ocm-foundation-audit-v1 -p 'test_*.py' -v
python -B research/ocm-foundation-audit-v1/audit_g2.py /path/to/result.json --out /new/path/audit.json
```

The dedicated workflow preserves the original artifact's archive and result hashes. Expired or unavailable artifacts fail closed; a byte-identical retained copy is required. Tests, audit logs and source custody are uploaded separately from the original study.

The next scientific G2 requirement remains useful learned content that is actually consumed after a fresh process restart, loses its benefit under a nontrivial matched withdrawal, and is compared with a strongest conventional parent at a fully charged cost. No ML router, architecture replacement, or general-learning claim is authorized by this package.
