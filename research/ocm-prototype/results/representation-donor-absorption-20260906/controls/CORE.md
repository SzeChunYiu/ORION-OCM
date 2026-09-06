# Preserved control generations

Raw logs retain earlier outcomes and are not rebound to final source.

| Prefix | Outcome |
|---|---|
| baseline | 11 original SV controls passed |
| red | 16 missing-implementation failures |
| first | 13 passed; 3 original withdrawal errors |
| mutable-binding-red | 3 failed before detached registration fix |
| qualified-v1 | 17 failures from legitimate infinite Scope epochs in new serialization |
| qualified-v2 | 30 passed after tagged nonfinite serialization |
| capture-red | missing capture implementation failed |
| capture-first | actual create-only capture/seal/grading control passed |
| grading-red | 2 failures before mismatch/error and arm-binding fixes |
| final-tests | 33 passed, 0 skipped/errors/failures |

First implementation source is retained under ../history/first-source/. Final source/test hashes are in ../raw/functional-v1/SOURCE.json.

intentionally-altered-final-fixtures contains two actual final unit captures AFTER negative mutations. One changes a result without its seal; one changes arm identity and reseals. They are expected refusals, not successful studies. The second fixture's stored grade belongs to pre-mutation bytes.

The real failed-consumer wrong-vector/request controls preserve mismatch detection despite ERROR. The complete unmodified 57-record capture is the publication no-alarm case. No unit control counts as a protected study.
