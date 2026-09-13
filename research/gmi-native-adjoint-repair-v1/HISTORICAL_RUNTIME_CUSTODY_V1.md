# Historical runtime selection

The existing test_vm_zoo_deterministic_and_remint_invariant_response tests
the pre-repair R1/R4 source. Its five capability goldens are unchanged:
gradient_net_h4 0.8021, hamming_knn_k3 0.8698, exemplar_table 0.7083,
particles_p4 0.8958, soft_retrieval 0.8542.

The test now explicitly obtains VMRow from gmi_microscope.historical_vm_v1.
The loader verifies the complete parent audit manifest identity and each of
the five archived import sources, then directly compiles those verified bytes
under a fresh disjoint package identity. Adjacent bytecode and prior cached
module objects do not supply executable authority. The old vm.py is byte-equal
to the file at main ef6de91af6f6ce692e0f8bd9725f8ad4f4435e9d and the source
pinned in the preserved PR551 audit. This deliberately retains its known
parameter-adjoint defect for historical receipt reproduction.

A valid stale .pyc that ordinary Python import executes is ignored by this
loader; a poisoned previously loaded VMRow does not survive a fresh load.
Changed manifest/import-source bytes are rejected. These controls concern
exact source selection, not protection against a hostile Python process.

The active-runtime primitive tests separately use the corrected live VM.
They include zero/unit-input learning, shared/tied/bias pullbacks and an
explicit response/charge comparison under three remints of the small native
graph. They assert no replacement zoo capability golden.

The original five-genotype, 16-event historical regression is the existing
bounded regression, not a new campaign or evaluation of corrected zoo
capability. Both historical and corrected-runtime claims must remain distinct.
See [replay](REPLAY_V1.md) and [active binding](ACTIVE_RUNTIME_BINDING_V1.json).

## Complete affected historical-fixture register

The bounded tracked-test import/call audit found seven relevant historical
fixtures. It does not assert that every unpinned fixture would fail numerically.

| Frozen regression | Temporarily selected old alias |
| --- | --- |
| R1/R4 five zoo capability goldens | local VMRow |
| B0 equivalence receipt hash | ecology.VM and lifecycle_vector |
| G8 retained learning witness | size_census.VM |
| R10 first six competition cells | invasion.VM and lifecycle_vector |
| R11 seed11, learned250 summary | b1.VM and VMRow |
| B6 default200 archive digest | b1.VM and VMRow |
| B6 trace200 same archive digest | b1.VM and VMRow |

Pytest monkeypatch restores all imported call aliases after each test. This
changes neither the live runtime default nor a stored capability, charge or
receipt hash. The R11/B6 executions are existing bounded historical regression
contracts; they do not create new search or capability evidence.

The audit also followed R7/R8/R9, degeneracy and intervention tests. R7 checks
mutation fingerprints; the first four R8 retained graphs have no GRAD; R9's
tested sizes3/4 cannot contain the relevant active parameter-gradient path.
The remaining audited microscope receipt tests use handwritten rows rather
than this native VM. These are source-scoped conclusions, not universal
coverage of future tests or external consumers.

Full corrected active fixture/helper copies and their hashes are included for
integration review. The active binding also checks the four unchanged native
import dependencies, so VM source equality includes its five-file closure. Copied historical files exceed the modular length target;
new code and explanatory documents remain small.
