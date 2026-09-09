# Evidence layout and preservation

[CORE](CORE.md) states the current result. [CURRENT](review/CURRENT.md) and
[CLOSURE-02](review/CLOSURE-02.json) are the accepted review; original review and
all source/receipt generations remain unchanged.

- [Current code](source/hole_match.py) and [replacement](source/replacement.py),
  exact copied validators and the separate slot-control source are inspectable.
- Original [eight-control receipt](records/original-eight/QUALIFICATION.json)
  and separate [one-control receipt](records/affected-slot/QUALIFICATION.json)
  preserve their actual scopes and process costs.
- [RAW.zip](RAW.zip) holds the complete frozen original and successor records,
  qualification pin inventories/snapshots, full reviews and design documents.
  [RAW-MEMBERS](RAW-MEMBERS.json) binds each original path and digest.
- [COPY-MANIFEST](COPY-MANIFEST.json) binds direct copies;
  [FILES](FILES.json) binds this public capsule. [Readback](READBACK.json) is
  packaging custody only, not a new scientific qualification.

Original qualification prose overclaims two slots; the original review requires
correction, and successor source requests say closure is pending. Those are
historical stage records, superseded in scope by the accepted current closure.
They were not rewritten to look retrospectively correct.

No internal REFACTOR source reading copy, giant upstream tree, or standard-library
source is redistributed. Full pin inventories are raw metadata, not a new runtime
installation. The exact source carries its original path/import assumptions;
this evidence package is not a newly qualified portable runner. Packaging only
reads/copies/hashes retained bytes and performs no tests/native/data execution.
