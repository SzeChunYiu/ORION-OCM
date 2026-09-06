# Thin integration and controls

The new g1_stanza profile/donor/field/vessel/worker/capture modules adapt the existing G1 request and chunk protocols.
The only existing-file hooks are stanza_donor.load_pipeline's model_root, g1_vessel's fixed syntax_operator_id,
capture_g1_matched's two named donor profiles, and grade_g1_matched.resources' resource-field compatibility.
No production src file changed. No arbitrary controller/checker/worker injection was introduced.

Both arms receive supplied word lists or the same complete public CLIA tasks.
Both use the same exact recurrent checkpoint bundle, cvc5 proposal interface and independent Z3 checks.
Syntax remains a model-supported observation; a structure check is not an accuracy oracle.
The OCM catalogue includes Stanza and cvc5 for every request. Native uses the direct donor/checker path.
The native worker and its source-identity collector do not import OCMRuntime.
Selected outputs, memory, load/copy work and full durable state inventory remain separate for each arm.

The pipeline cache is keyed by resolved archive and fixed profile and survives only within one process.
Profile validation and lookup are cheap per sentence. Full hashes bind cache load before/after and worker entry/end.
This is trusted fixed-source custody, not process-isolated immutability or a filesystem watcher.
If the archive changes at a chunk barrier, that chunk cannot be graded as a successful execution.
The prior implementation hashed242MB twice per sentence. Its source and controls remain under
controls/pre-hash-boundary-correction; the prospective change applied identically to both arms before any predictions.

Final fixture controls cover model-root/declared-loader closure, forms-only caching, structural error versus inability,
default-source compatibility, native import isolation, native/OCM selected-tree equality,
full catalogue/checked admission, live/reload/revoke/reinstate and unrelated mathematical retention,
missing checker/model binding/input refusals, fixed successor profile/lineage/cadence,
capture overwrite and arbitrary-profile refusal, CPU UNKNOWN semantics, and archive drift at the chunk barrier.
Tests invoke a public CLIA max3 unit donor control; no trained Stanza model is loaded.

The final scoped test command was:
    PYTHONPATH=$PWD/src OCM_G1_DEV_PATH=<custody EWT DEV> <g1-env>/bin/python -m pytest research/ocm-n1 research/ocm-prototype -q --ignore=research/ocm-prototype/results --ignore-glob='research/ocm-prototype/test_hosted_*.py'

The existing development scorer and all its quality denominators are unchanged.
The only grader change reads explicit direct-child CPU observations and reports total tree CPU UNKNOWN.
Its legacy-field behavior is retained and tested.
The review-ready record is the exact pre-commit source checkpoint; its committed=false field describes that historical checkpoint.
