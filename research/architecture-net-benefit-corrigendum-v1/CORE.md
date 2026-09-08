# Architecture net benefit: wording corrigendum v1

This note clarifies two statements in the source observed on canonical main `453daf3c332c44c8f6f5e2a048ce63a810b896e0`. Both files were byte-identical to their reviewed PR161 versions. Their source and historical run receipts remain unchanged; this note adds no theorem, execution or architecture-benefit result.

**Reachable directed cycles.** The [maximum-rate corollary, lines 85–89](https://github.com/SzeChunYiu/ORION-OCM/blob/453daf3c332c44c8f6f5e2a048ce63a810b896e0/research/architecture-net-benefit-v1/THEORY.md#L85) must use the reachable subgraph throughout:

Provided every reachable zero-demand directed cycle has nonnegative gain, the maximum feasible rate is

`inf_{reachable directed cycles z: sum d(e)>0} sum g_w(e) / sum d(e)`.

For a finite graph with a reachable positive-progress directed cycle, this infimum is attained on a reachable simple directed cycle. Decomposition into simple directed cycles gives a demand-weighted average over positive-demand components, plus nonnegative zero-demand gain. With unit demand, this is the minimum cycle mean on the reachable subgraph. If no reachable positive-demand directed cycle exists, report no sustained-rate conclusion. The implementation checks a supplied rate; it does not implement Karp's optimization algorithm.

**Variable resource dimension.** The [verify docstring, line 127](https://github.com/SzeChunYiu/ORION-OCM/blob/453daf3c332c44c8f6f5e2a048ce63a810b896e0/research/architecture-net-benefit-v1/benefit_certificate.py#L127) should read `O(V+E*k)` arithmetic operations after reachability, where `k` is the number of resource coordinates. For fixed `k`, the shorter `O(V+E)` expression applies. The existing exclusions for reachability computation, integer bit complexity and source validation remain.

[Exact bindings](BINDINGS.json) retain the canonical head/tree and both source identities. The [minimal patch](optional/documentation.patch) is an optional, unapplied record of the same clarification. It changes only three theory prose lines and one Python docstring line; executable source is unchanged.

This corrigendum does not requalify historical controls, native runs or empirical claims. Conditional finite-model certificates still require the stated semantic and cost correspondence before supporting a claim about software.
