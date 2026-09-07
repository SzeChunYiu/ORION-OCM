# Current materializer handoff evidence

Current authority is the final 14-control handoff and integrated v4 result:
**425 passed, seven skipped, two deselected; three custody guards passed**.

[INDEX](INDEX.json) binds three lossless archives and the 138 current source files.
[Source bindings](CURRENT-SOURCE.json.gz) are the exact compressed v4 before file;
the original after file and copied sources remain inside integration-v4.tar.gz.

- handoff.tar.gz: all five development generations, including the collection error.
- independent-review.tar.gz: unchanged final source/record review.
- integration-v4.tar.gz: current process/JUnit/source records; cases are omitted.

All 3,036 retained regular members were compared directly with originals.
[Omissions](OMISSIONS.json) distinguish 106 symlinks retained as metadata, external
host inputs and uninspected integrated fixture bodies. Historical packages remain
unchanged; [their identities](OLD-PACKAGES.json.gz) are separately retained.

Read [the source repair](../MATERIALIZE-HANDOFF.md) and
[the integration result](../INTEGRATION-MATERIALIZATION.md).
Safe dangling links still refuse the unchanged execution-profile inventory;
LAYOUT_READY does not authorize execution. No real corpus, learning or semantic
success is established by this engineering qualification.
