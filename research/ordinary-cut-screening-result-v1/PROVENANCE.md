# Source, process and evidence custody

The accepted process chain is caller **2286297** → observer **2286298** → screening child **2286299**. The fixed create-only records support one authorized attempt here; the review did not perform a global execution census. [Gate](records/observer/ROOT-SCREENING-GATE.json) · [issued request](records/observer/EXECUTION-REQUEST-DRAFT.json)

The independent outcome review reconciles 76 START pins, 77 post-run unchanged flags, all 77 output files and 110 imported-module entries. Project/Lark paths match their qualified locations. Other imported standard-library modules have an interpreter-path boundary, not a byte-hash inventory of every imported standard-library source. Those sources are not copied into this capsule.

The complete driver source, controls, observer/caller/binder source, patches and source/observer/outcome reviews are retained. The provisional binder's stale request pin is preserved with its corrected successor. No frozen source or receipt was rewritten by publication. [Source review](review/source/REVIEW.json) · [observer review](review/observer/REVIEW.json) · [outcome review](review/outcome/REVIEW.json)

The source and observer records are historical qualification stages. Their statements that actual screening or the gate was absent describe their freeze time. The later consumed gate and actual process/result records govern this attempt. The literal DRAFT filename/status in the issued request is preserved; its exact bytes were separately bound by the gate, not silently updated after execution.

Fourteen authored integration controls preceded execution. Observer qualification separately records nine authored output controls and one isolated missing-gate startup. Three older cleanup process controls were reused through the reviewed unchanged cleanup block; they were not rerun for this result. These control populations are not additional screening experiments. [Integration receipt](records/source/QUALIFICATION.json) · [observer receipt](records/observer/qualification-01/QUALIFICATION.json)

[UPSTREAM.json](UPSTREAM.json) maps the exact prior P1/result/cost inputs to immutable PR164 RAW members and the Lark 1.3.1 runtime/wheel to immutable PR166 RAW members. Large prior inputs, complete prior archives and standard-library sources are not duplicated. The small reused cleanup receipt is retained directly for inspection.

[RAW-MEMBERS.json](RAW-MEMBERS.json) binds every archived byte to its original path. [COPY-MANIFEST.json](COPY-MANIFEST.json) binds direct copies. Packaging performed only source/data copying, hashing, archive readback and link checks: no target imports, controls, screening, native or learner execution. Frozen absolute paths remain historical locations, not a relocated execution qualification.
