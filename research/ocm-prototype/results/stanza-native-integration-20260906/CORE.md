# Stanza integration

119 N1/G1 tests passed, including all 23 new offline Stanza controls; no failures,
errors or skips. The selected suite matches current n1-packed-chart.yml and excludes
archival results plus hosted route tests. This run used qualified laptop Python
3.13.12; the hosted CI Python 3.11 run is a separate result.

The reviewed Stanza source and packet were committed at 9e235d8 and then merged
normally with main 7ff8d1ec803e78d04f95e3d966e92ed48b29ff81.
Tests executed integrated source 07d5907cdfe1f326759f28cedff3977434371ea5.

The main src, tools, tests and docs/provenance subtrees are exactly unchanged.
The selected current-engineering pointer, all 68 packet artifact bindings and five
reviewed Stanza source bindings were reverified. No protected evaluation, scientific
promotion, Stanza prediction or hosted model request occurred during integration.

- [Command and runtime](command-completed.json)
- [Actual test log](n1-g1.log) and [JUnit](n1-g1.xml)
- [Custody checks](verification.json)
- [Donor result and explicit CPU correction](../stanza-native-qualification-20260906/CORE.md)

Owner #43 / #73; classification INFRASTRUCTURE.
