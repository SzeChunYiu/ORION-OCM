# Ordinary syntax revival review

The initial prototype requires one bounded API correction before screen wiring:
separate complete grammar support from completed query coverage, and make every
UNKNOWN result carry false query coverage. The checker already routes UNKNOWN
through SyntaxUnknown; this is not an observed false-negative result.

[Initial review](REVIEW-01.json) binds the source, original 17 controls and their
custody limits. [Preconditions](PRECONDITIONS.md) describe the required interface.
[Byte bindings](BINDINGS-01.json) preserve the reviewed snapshot.

The contract compiler, token encoding, ordered witness emission and structural
replay are accepted within their supported domain. Lark is reused unchanged.
The 512-token and 4096-label prototype refusals do not replace registered matcher
or wall bounds. Actual screening remains a separate, unopened integration step.

Root assigned successor-02-coverage. Its source/receipt closure will be recorded
separately here, preserving the original freeze and 17 controls without replay.
