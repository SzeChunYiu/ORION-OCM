# Read-only implementation review

Reviewed draft source on laptop at ocm-clia-reuse, base 4436348; this is a review
snapshot, not a source freeze or test execution. No panel or model inference ran.
After the owner's corrections, no remaining blocker was found in this bounded
mechanism review. Final source/test bindings and capture qualification remain gates.

## Confirmed mechanism

- clia_reuse_vessel.py:31–43 adopts a live admitted G1 program, expands derived
  warrants to actual assumption support, performs a universal recheck and stores
  a data-only descriptor. It does not invent an acquisition algorithm.
- :47–57 binds the descriptor to the existing operator registry; :69–87 wraps that
  registered backend in the actual SV catalogue, and :102 executes runtime.solve.
  The persisted registry supplies metadata only; restart requires explicit host bind.
- :103–114 rechecks the selected output before a support-governed proof admission.
  clia_reuse_apply.check_value binds exact arguments, descriptor/program IDs and
  actual integer value, reparsing canonical program data independently of the cache.
- clia_reuse_descriptor.create performs a real grammar/universal check; imports
  reverify through verify_import. The cached descriptor is not just a trusted PASS
  string. Its source/checker/program/support identities are bound.
- NativeLibrary shares descriptor creation, compiled evaluator, pointwise checker,
  persistent results and support liveness/revocation. It may dispatch directly and
  retain its ordinary-library cost advantage; no OCM machinery is imposed on it.
- V.audit and NativeLibrary.audit expose descriptors, current liveness, history
  IDs, bound-callable status and prior application answers without re-registration.
- Ground execution and pointwise checking share Z3. Independent public-spec
  arithmetic grading is therefore still required; no independent-engine correctness
  claim follows from the internal pointwise recheck alone.

## Confirmed issue and checked correction

The inspected descriptor snapshot 774607453dec5cf46ce32c3ff781e42cbf5adac6c01dfcc99735282c3038c84b
checked history overlap against upper support only (:64–65 and :89).
A valid lower=[[h]], upper=[[]] profile with history_only=[h] then changes LIVE
to UNKNOWN when h is withdrawn. Vessel adoption already rejects overlap in both
bounds, so the native and vessel contracts differed. Owner confirmed and corrected
both create/validate to inspect all lower/upper terms; corrected descriptor SHA256
861d0bc62c7698eff7fe21e2ae7fc1cc136f446bcc350436afb4fc97691fc1ff.
The added test covers rejection at creation and validation, plus a clean separate
history record that preserves LIVE. I reread the code/test; I did not execute it.

## Scope corrections agreed with owner

The inspected V catalogue supplied all slots only for application requests; the
ordinary G1 query used two slots, and application callbacks assumed program_id.
The corrected G1.query:81–94 selects an optional catalogue builder and :127 reports
actual supplied IDs. V.query:138–147 delegates to the existing G1 admission;
per-application callbacks use request.get, so syntax/synthesis remain inapplicable.
Default/expanded CLIA and syntax controls check unchanged admission, full actual
catalogue reporting, no spurious applications and correct dispatch counts.

Native synthesis_calls initialized to zero was not full-lifetime measurement.
The corrected native field is synthesis_calls_in_library with explicit scope.
The capture must retain actual cvc5 acquisition invocation receipts and meter any
post-acquisition synth dispatch; library counters alone cannot establish the claim.

The original 19 new plus 27 existing passing controls were reported by the owner.
Their synthetic programs/model placeholders and archived-program compilation are
unit evidence, not the prospective real acquisition/new-input/syntax panel.
Final corrected test receipts remain to be bound before root authorizes execution.
