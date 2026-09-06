# Historical Codex boundary refusal (preserved)

> This records the initial Codex route only, not current implementation status.
> Read [README.md](README.md) for current qualification and availability evidence.

Owner: #73, comment 5555803159. Checkout base: 00c85dff3e63941856657d886946ebc3466577b2.
Classification: INFRASTRUCTURE / supporting comparator qualification.
No hosted benchmark request, credential inspection, client upgrade or source change under src/ occurred.

## Executed finding

The local loopback capture exercises the real pinned client request construction and returns HTTP 400
without invoking a provider or model. It preserves only the tool payload and request digest publicly.
The first catalogue exposed update_plan, request_user_input, apply_patch and view_image.
A narrow revival added documented include_apply_patch_tool=false and tools.view_image=false,
plus skills.include_instructions=false and suppression of ambient app/environment instructions.
The second real capture still exposed the same four tools. Neither surface satisfies the posted protocol.

Two tests: unexpected-tool refusal PASSED; required empty builtin catalogue FAILED.
This is an unmet acceptance gate, not a successful comparator adapter.
No MCP environment was installed and no namespace workaround was implemented.

Laptop records:
- /home/billy/orion-director-work/20260906/hosted-catalogue-builtin-refusal/
- /home/billy/orion-director-work/20260906/hosted-catalogue-supported-switches-refusal/
- hosted-catalogue-red.log, hosted-catalogue-first.log, hosted-catalogue-supported-switches.log
Second catalogue SHA256: 5aa8e5788ec0058d01737012d20b001d354f675f131dc7df6de32112ceb7dd7c.
Private stderr remains outside the repository.

## Historical prospective revival (not adopted)

This proposal was rejected because credential custody remained unresolved.
No whole-client authentication workaround was built.

The proposal was to allow exactly the four observed builtin names only if the whole client is also inside an enforced
filesystem namespace. Continue to reject every additional tool, missing donor or catalogue mismatch.
Do not describe the four tools as disabled.

The client namespace would contain only an empty actor home/config, read-only pinned executable/runtime
closure, public task files and writable actor memory. Gold, evaluator results, sibling worktrees and
the whole repository stay unmounted. No root/home blanket bind, host /proc, SSH agent, Docker socket,
user D-Bus socket, host /tmp or inherited open file descriptors. Preserve every explicit mount in a manifest.
The separate native MCP namespace remains networkless, with only fixed donor modules, runtime,
public CLIA fixtures, trained model bytes and bounded memory. No OCM or grading code is needed.
Neither namespace may write the input/model/source bindings.
Disable hooks, plugins, shell, browser, extra agents and ambient memories as already tested.

Credential custody is unresolved for that whole-client route. Mounting the existing auth file makes
it reachable by residual file tools within the client namespace; read-only is not credential secrecy.
Do not claim credential isolation merely because the expected task is benign.
Do not transfer tokens through argv, inherited environment, public config, MCP arguments or audit logs.
The generated app-server chatgptAuthTokens login variant explicitly says internal-use-only / do not use;
it is excluded. Standard interactive ChatGPT/device-code login is supported but is a different,
not-yet-authorized authentication operation. No authentication workaround was attempted here.

## Minimum proof before any model benchmark

1. Freeze the changed tool contract and credential-custody choice explicitly.
2. Run the real client against the local stub and verify the exact complete catalogue.
3. Positive: a public task and both fixed native donors work inside their actual namespaces.
4. Negative: synthetic outside sentinel, sibling-path/symlink, gold-like canary, network and write attempts
   are denied at the actual applicable boundary; controls use synthetic data only.
5. Verify the actual residual file-tool handlers cannot access the chosen credential canary boundary,
   rather than relying solely on a shell command that may run in a different sandbox.
6. Record process restart persistence, source/model/input bindings and all costs.
7. Only then run the authorized previous-generation reference. Frontier parity remains CANNOT_CHECK.

Official metadata used:
- https://raw.githubusercontent.com/openai/codex/rust-v0.129.0-alpha.15/codex-rs/core/config.schema.json
- Local generated experimental schema: v2/LoginAccountParams.json.
- https://github.com/modelcontextprotocol/python-sdk (maintained v1 line available; no install yet).
