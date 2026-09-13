# Native parameter attribution and its evidence boundary

The [frozen NAR correction](../gmi-native-adjoint-repair-v1/PARAMETER_ADJOINT_CORRECTION_V1.md)
repairs one misplaced weight-parameter marker using the established
multiplication chain rule. The marker belongs on the weight leaf, so the
registered reverse path multiplies the product adjoint by its input.
This is an application of reverse AD to the stated ordered, rounded/clamped
pullback convention; it does not differentiate the discontinuous quantized VM.

At zero input the old native control incorrectly writes weight8→9.
The corrected B0/B1 controls keep8, while the nonzero no-alarm case keeps8→7.
GRAD updates cells despite having no outgoing dataflow edge. An outgoing-edge
scanner therefore cannot diagnose gradient inactivity. The old and corrected
full tapes, ledgers, source snapshots and outputs are retained together.

The unchanged ledger rule gives different realized zero-update charges:
B0 changes13→10 and B1 changes9→8 because the existing zero-gradient branch
skips a multiply/write. These are authored charges, not measured host work.

## Live source and historical records

The capsule binds the complete64-file NAR unit and all nine live files in its
[active mapping](../gmi-native-adjoint-repair-v1/ACTIVE_RUNTIME_BINDING_V1.json).
Each live file must also equal its frozen corrected-source copy byte-for-byte.
Every inventory load checks the live source hashes and both complete new units;
the wrapper repeats exact mapping equality before and after original replay.
A later checker cannot alter an earlier live dependency without rejection.
The complete original NAR JSON remains inside the outer receipt; its status
cannot replace any source, finite case, historical control or scope field.

The source-sensitive historical regressions now explicitly use the original
VM through its bound loader. Their old goldens and all historical result files
remain unchanged. Such replay verifies historical behavior, not a corrected
runtime campaign. The [historical validation record](../gmi-native-adjoint-repair-v1/HISTORICAL_REGRESSION_VALIDATION_V1.json)
records the exact accepted normal/optimized commands and source context.

## Scientific scope

The primitive correction does not identify causes of four failed learner
configurations, demonstrate acquisition/transfer, or recover a family
capability. Q6 retains those causal, coverage and full-cost obligations.
The [later PR551 delta](PR551_FAMILY_CEILING_CORRECTION_08821A0A_V1.md)
has no source-code change and cannot claim to have evaluated this corrected VM.
No frozen campaign, earlier B6 census or source audit is overwritten.
