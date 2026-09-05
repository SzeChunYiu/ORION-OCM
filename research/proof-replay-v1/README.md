# Fixed proof reconstruction and runtime support replay

This package advances the proof-route prerequisite in OCM #38. It binds an
actual Lean kernel and standard library, rechecks eight existing V2 logical
bridge theorems, and checks one authored theorem that composes two of them.
The required CI job produces a fresh receipt. Missing Lean is CANNOT_CHECK;
historical receipts cannot substitute for executing the kernel.

`Foundation.lean` and `verify_lean.py` are exact V2 sources at
`b15abb41e1f9219ea793a15c5e641ac6579adb35`. The manifest records source Git
blobs and SHA256 digests. `Composition.lean` reconstructs refinement followed
by agreement soundness. Its explicit hypotheses remain part of the theorem;
neither the hypotheses nor an informal interpretation are certified by
checking its proof. The import closure is the pinned Lean standard library
plus the included Foundation source. No mathlib or third-party module is used.

The release archive's SHA256 is
`6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe`,
previously observed in [the original V2 kernel job](https://github.com/SzeChunYiu/ORION-V2/actions/runs/33963996388/job/101300713864).
Replay checks that digest and the archive size before extraction into a new
temporary directory. It clears Lean/Lake/Elan/Python search overrides, uses
the extracted binary, compiles the Foundation dependency from pinned source,
and records each theorem's axiom report and generated dependency digest.
This is a fixed trusted proof package, not an arbitrary-code evaluation API.

The original verifier includes false-statement, injected-axiom and admitted-proof
controls. Local Python tests additionally reject changed/missing sources,
changed runtime code, changed toolchain archives and receipt overwrites.
These Python tests alone cannot establish a successful Lean replay.

Seven cells exercise the exact existing OCM warrant implementation: admission
using a kernel-run evidence root, revocation, alternate independently supplied
run evidence, all-support revocation, restoration, and separately revocable
correspondence. The fixture evidence identifiers are authored inputs, not
authenticated external reviews. Revoking reliance on a run does not make an
immutable mathematical theorem false. This finite support check does not
prove arbitrary Lean-to-OCM semantic correspondence.
Missing correspondence remains UNKNOWN: a kernel run supplies neither
correspondence evidence nor an exhaustive certificate that no such evidence exists.

```sh
python research/proof-replay-v1/test_replay.py
python research/proof-replay-v1/replay.py \
  --archive /path/to/lean-4.19.0-linux.tar.zst --out /new/path/proof-replay.json
```

The nine named proofs are known authored fixtures. Unseen composition, learning
reusable proof methods, strongest-parent comparison, broader libraries,
open-target selection, independent statement correspondence and novelty
review remain unearned. OCM #38 and the grand programme remain open. This
package grants no runtime adoption and changes no historical M0–M12 receipt.
