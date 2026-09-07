# Exact corpus dependency acquisition

This entry implements the source acquisition phase of the existing
[four-row registration](REGISTRATION.md). It does not build a proof, select a
different example, learn a method or establish transfer into language.

## Inputs and execution

Run on billy-laptop using the registered CPython 3.11.14 binary:

```text
<python> -I -S acquisition_run.py <original-registration> <pinned-lock> <new-episode>
```

The lock is already exposed corpus metadata at commit
`aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`, not a new dependency download.
Its exact SHA256 is
`435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf`.
The entry verifies the original registration seal and its files, consumes the
same checked assignment/policy bytes, declares all seven stages for the existing
four rows, and snapshots its actual source bytes before dispatch.

The production worker accepts only the nine resolved Git revisions in that lock.
It creates new bare stores, fetches one exact commit at a time, and retains every
command request, raw stdout/stderr, observed exit and partial store. No checkout,
Lake, package setup, source tactic or acquired executable runs during acquisition.
It does not follow `inputRev`, recurse into submodules, use a partial-clone cache,
retry a failed fetch or substitute a different dependency.

## Acquisition policy and enforcement

Trusted system Git 2.25.1 executes fixed argument arrays with a cleared environment,
empty owned HOME/template/hooks directories, disabled inherited Git configuration,
no credential helper, explicit TLS verification and refused HTTP redirects.
Only a fetch command is given the HTTPS transport; local verification disables
Git protocols. Exact commit and root-tree hashes, strict object checks, and
retained material inventories qualify the returned source snapshot.

This is an acquisition policy enforced by the trusted worker and Git configuration.
It is not a kernel endpoint firewall or the offline evaluator sandbox. DNS/TLS
and ordinary Git runtime dependencies remain trusted host services. The existing
offline `build_profile` and its root helper remain unchanged; a material receipt
does not authorize any acquired code to run there.

One existing `resource_runner` invocation contains the worker and all its Git
descendants. It enforces the registered aggregate CPU, memory, process and per-file
bounds and samples owned disk usage. The disk guard is not a hard volume quota.
The supervisor, registration/source validation and final custody are measured
separately from child controller usage. Command timers are nested, not additive.
Retained object/file bytes are measured; network wire bytes are not measured.

## Clock and outcomes

`STARTED.json` binds the host boot identity, monotonic start, one 3,600-second
acquisition deadline and the original 43,200-second whole episode deadline.
Validation, source copying, transfer and custody consume those clocks. Cleanup
and final records remain visible after a dispatch deadline stops new work.
Use a separately retained outer process measurement to include final receipt
writes; the phase's own wall measurement explicitly ends before those writes.

`MATERIAL_READY` requires all nine exact materials, a clean completed child,
confirmed process cleanup, intact source/input/phase bindings and post-dispatch
material validation. It is a phase result with zero semantic checks. Each row
points to one shared acquisition cost; it is not charged four times.

An acquisition or setup failure preserves the reached stage, actual cause and
partial artifacts. Dependent stages are `NOT_RUN`. The original registration,
population, assignments and cursor are never modified. Existing destinations
are refused, including output paths overlapping an input or the source package.

On material readiness the episode remains open. Before any registered wrapper
build, qualify and bind the offline evaluator, declaration association and export
closure. Preparation and waiting consume the same remaining whole deadline.
Every later entry must verify the boot identity and original monotonic deadline;
it may not restart the clock. If the episode ends without a qualified evaluator,
record `CANNOT_CHECK` at BUILD with the concrete BUILD_POLICY cause for all four
rows and retain downstream `NOT_RUN` stages. A revival uses a new linked record
and retains the earlier failure and costs.

The first downstream scientific questions remain masked proof reconstruction
and causal method reuse on fresh mathematical and controlled-language meanings.
Neither reference-source acquisition nor reference replay answers those questions.
