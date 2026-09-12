# Stage E — exact frontier / phase diagram: report V1

Receipt `microscopes/results/STAGE_E_FRONTIER_V1.json` (sha256 `620ca65f3ee4617d…`). Cost model: `C = desc + H*exec_q + r*upd_e + r*ver_e + (r/4)*rev_e; per-event costs measured in Stage D`; θ = 0.75; axes H ∈ [1, 2, 4, 8, 16, 32, 64, 128], r ∈ [0, 1, 2, 4, 8, 16, 32].

## PH-REV (frozen before this stage): dense-update rows leave the frontier as revision frequency rises

| column | small size: winners by r at H=8 | dense ever wins | dense loses at high r (PH-REV) | r* (first all-local cell) small → large | held-out within one step |
|---|---|---|---|---|---|
| B0 | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |
| B1 | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |
| B2 | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |
| B3 | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |
| U | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |
| P3 | {'0': ['M1'], '1': ['M1'], '2': ['M1'], '4': ['M1'], '8': ['M1'], '16': ['M1'], '32': ['M1']} | False | **True** | 0 → 0 | True |

Verdict: {"PH_REV_indexed_columns": {"B2_REWRITABLE_TYPED_PROGRAM_GRAPH": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r", "U_UNIFORM_UNIVERSAL": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r", "P3_COMPRESSED_PROGRAM_PARENT": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r"}, "PH_REV_scan_columns": {"B0_LOCAL_ADAPTIVE_TRANSDUCERS": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r", "B1_COMPOSITIONAL_LEARNER": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r", "B3_STOCHASTIC_GENERATIVE_KERNEL": "NOT_OBSERVABLE_AT_SCOPE__LOCAL_ROWS_DOMINATE_AT_EVERY_r"}, "dense_ever_on_frontier": {"B0_LOCAL_ADAPTIVE_TRANSDUCERS": false, "B1_COMPOSITIONAL_LEARNER": false, "B2_REWRITABLE_TYPED_PROGRAM_GRAPH": false, "B3_STOCHASTIC_GENERATIVE_KERNEL": false, "U_UNIFORM_UNIVERSAL": false, "P3_COMPRESSED_PROGRAM_PARENT": false}, "reading": "The binding ecology is discrete, exact and small-data (PH-2 conditions in ECOLOGY_AXES_V2): the axis theory predicts local/store forms there, and they dominate at every (H, r) in every column. The revision-axis handover can only be observed in an ecology where a dense-update form wins at low r \u2014 a smooth-generalization ecology (Stage F, E_smooth). PH-REV is therefore NOT tested here; it is carried to Stage F with the prediction unchanged."}

Reading rules: if a dense-update row never wins at any r (dense_ever_wins = False) the PH-REV *handover* cannot be observed in that column — the local rows dominate everywhere because at this scope they also reach the target in fewer events; that is a frontier fact, not a failed prediction. PH-REV is supported only where a dense row wins at low r and loses at high r. Negative control PH-5: NOT RUN (no parity ecology at this scope).

