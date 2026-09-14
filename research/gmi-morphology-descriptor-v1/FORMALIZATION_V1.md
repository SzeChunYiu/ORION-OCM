# Architecture-name-free morphology descriptor v1

Scope: the first prerequisite row of issue #602 F4 only. Evidence classes P1/P2. Claim ceiling **G1**. This artifact freezes what a future capability predictor is allowed to see; it does not fit that predictor or claim G6.

## Descriptor factorization

A specimen record is split as

`D = (I, X)`

where `I = (specimen_id, source_ref)` is identity/provenance metadata and `X` is the predictor-visible morphology object. `X` has exactly twelve registered coordinate families:

1. state carrier;
2. operator structure;
3. control routing;
4. update channel;
5. memory organization;
6. sharing/symmetry;
7. communication channel;
8. tool channel;
9. verification path;
10. resource footprint;
11. development law;
12. interface geometry.

Each family has a fixed field set in `MORPHOLOGY_DESCRIPTOR_V1.json`. The validator refuses missing or extra coordinates and missing or extra fields.

## Metadata-remint invariance

Define the allowed predictor projection `P(D)=X`.

**Theorem F4-M.** For any two valid descriptors `D=(I,X)` and `D'=(I',X)` with identical morphology features and arbitrary metadata remint `I -> I'`,

`P(D) = P(D')`.

The SHA-256 morphology fingerprint is computed only from canonical serialization of `X`, so it is invariant under the same remint.

*Proof.* `predictor_projection` validates the complete record, then returns only the `features` object. Neither identity field is read into the returned value. The fingerprint is a deterministic function of that projection alone.

This blocks direct family/source/specimen identity leakage through the predictor interface.

## Architecture-name exclusion

The registered coordinate names and semantics describe state, transformations, routing, updating, memory, sharing, channels, verification, resources, development and interfaces; none is a named model family. Predictor-visible feature strings are recursively checked against a frozen forbidden list of common architecture/family/update-law names. A matched negative twin injects such a name into a feature value and must be rejected.

This is a syntactic and interface-level guarantee, not a claim that structural coordinates cannot statistically identify a family. They are expected to carry structural information. Nor can a static validator rule out an adversary deliberately encoding identity into innocent-looking numbers. The future F4 prediction protocol must therefore freeze descriptor extraction prospectively and hide held-family outcomes during fitting.

## Completeness at registered scope

**Theorem F4-C.** If `validate_descriptor(D)` returns normally, then the predictor-visible object contains exactly all twelve registered coordinate families and exactly each family's required fields.

*Proof.* The validator compares feature-coordinate keys with the registry key set by equality, then compares each coordinate payload's keys with its required-field set by equality. Any omission or addition raises before projection.

This is schema completeness, not ontological completeness of all possible morphology descriptions. A future counterexample that requires a new architecture-independent coordinate falsifies the current registered basis and should extend or replace it rather than being silently encoded in identity metadata.

## Parent subtraction and claim boundary

The strongest parents are generic architecture characterization, algorithmic/resource descriptors, sufficient structural statistics and leakage-resistant feature design. The GMI-specific role here is to freeze one predictor-facing contract aligned with the already registered ecology, capability and developmental objects. No capability outcome has been used, no regression/classifier has been fitted, no held-family prediction has been frozen, and no G6 claim is made.
