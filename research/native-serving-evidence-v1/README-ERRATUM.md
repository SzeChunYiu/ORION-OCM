# Additive README precision correction

The frozen candidate 02 README says only the checker opens PREFIX.mm. That wording is
too strong: the apparatus custody layer also reads its bytes to verify the frozen hash.
Only the independent native checker interprets the prefix as mathematics. The serving
search receives parent/bank contracts and sealed method payloads, not prefix content.
Both custody reads and checker reads remain included in the measured cost boundary.

Candidate 02 bytes and their engineering/source-review receipts remain unchanged.
Before later source/CI integration, replace the README sentence with this distinction,
then record the successor source binding. This is a documentation correction, not a
changed experiment or reason to rerun settled controls.
