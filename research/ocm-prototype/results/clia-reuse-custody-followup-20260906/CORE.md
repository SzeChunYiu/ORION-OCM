# Deterministic syntax-record custody control

One test passed in 0.05 seconds against runner/grader source committed at 53c8e60.
Two actual native Actor.query calls with the same fixed output and no timing fields persist one identical record.
Both external selected-record lookups succeed. The fixture substitutes the donor output and does not run model inference.

Only the test file changes; the qualified runner/grader source and previous 189-test evidence remain unchanged.
The zipped raw fixture includes an explicitly labelled 20-byte placeholder, not a trained model.
