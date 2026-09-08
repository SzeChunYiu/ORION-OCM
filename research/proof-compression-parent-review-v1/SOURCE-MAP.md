# Concrete source reuse map

The source links below point upstream. Their downloaded byte hashes and exact read
windows are in [SOURCE-READS.json](SOURCE-READS.json). Git commit/tree
metadata independently bind 18 CD Tools blobs to `42ae1d5d52270ab5b9831d301a9fe281826c4cee`;
[GIT-SOURCE-BINDING.json](GIT-SOURCE-BINDING.json) retains every comparison.

| Source / lines | Reuse / required boundary |
| --- | --- |
| [dagsav_cd.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/dagsav_cd.pl), 89–118, 163–200 | `terms_dagsav/4`: factorize a term forest, count each factor occurrence, sort negative edge save-value and reference keys. Reuse core; preserve ground/variable identity and deterministic order. |
| [factorized_ds_cd.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/factorized_ds_cd.pl), 50–70, 99–135 | Cached MGTs over factored ground D-terms; fresh copying and occurs-check on detachment. Shared representation must not identify independently instantiated formula variables. Open typed cuts need the Horn context API. |
| [thgen_dagsav.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/applications/thgen/prolog/thgen_dagsav.pl), 24–37, 81–93, 145–202, 263–300 | Concrete miner: distinct source terms, DAG factors, MGT computation, lexicographic reranking, variant/subsumption reduction. Top-level generated-POI imports and fixed fast-I/O sources must be excluded from our adapter. |
| [thgen_prepare_dagsav.sh](http://cs.christophwernhard.com/cdtools/downloads/cdtools/applications/thgen/scripts/thgen_prepare_dagsav.sh), 3–18 | Existing launcher uses PIE, CD Tools, SWI and the experiment module; not an approved entry point for OCM input custody. |
| [tgr_utils.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/tgr_utils.pl), 565–680 | `term_dag_compression/3` wraps SWI factorization with explicit `start_lhs` variables and propagation. Copy caller terms: numbering can instantiate them. |
| [tgr_treerepair.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/tgr_treerepair.pl), 22–139 | `term_treerepair/3`, existing Prolog TreeRePair entry point; delegates replacement/pruning and provides parameter handling. Reserve for a measured need for parameterized patterns. Its delegated algorithms were not audited here. |
| [tgr_sorting.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/tgr_sorting.pl), 268–346 | Existing rank, edge/tree/DAG sizes, argument multiplicities and `actual_sav` interface. Do not reuse a linear-only estimate as nonlinear expansion cost. Detailed implementation not audited. |
| [mm_proof_macros.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/mm_proof_macros.pl), 44–155 | Existing theorem-to-macro conversion and ordered body parameters. Defaults strip syntax; `override` bypasses normal processing. Adapter must freeze options and prohibit unregistered overrides. |
| [mm_tgr.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/mm_tgr.pl), 125–177, 306–427 | Whole-library and selected-theorem dependency-closure APIs; Horn-MGT registration. Default theorem verification is false; optional grammar fixing changes grammar. Neither is OCM/native authority. |
| [mm_addsyntax.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/mm_addsyntax.pl), 54–143, 155–192 | `mm_proofmacro_add_syntax/8` carries ordered essential names and extended variables/DV. Lines101–105 explicitly defer inference of extra context for fresh lemmas. Keep `modify=0`; other settings are documented experimental. |
| [mm_proof_output.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/src/cdtools/mm_proof_output.pl), 38–56, 91–140 | Print syntax-complete proof and replace an existing theorem for external Metamath verification. Does not provide our fresh-claim receipt, exact failing-stage discrimination or lifecycle binding. |
| [thgen_mm_proofconversion.pl](http://cs.christophwernhard.com/cdtools/downloads/cdtools/applications/thgen/prolog/thgen_mm_proofconversion.pl), 25–108 | Existing implication-form/compiler mechanism. Imports generated POI data and applies particular axiom/definition conversions: not a drop-in typed/native transport. |

SWI's [term_factorized/3 contract](https://www.swi-prolog.org/pldoc/doc_for?object=term_factorized/3)
explicitly permits cyclic terms. A proof-grammar adapter therefore needs its own
finite/acyclic contract; the factorizer returning is not an admissibility certificate.

## License, version and dependencies

The source headers specify GPL version 3 or later; [COPYING.TXT](http://cs.christophwernhard.com/cdtools/downloads/cdtools/COPYING.TXT)
was retained in the internal read record. Preserve that license when reusing code; do not relabel it as MIT.
A separate research tool/process keeps the donor boundary explicit, without making
an unreviewed claim about the licensing of a combined distribution.

The official [checkout stamp](http://cs.christophwernhard.com/cdtools/downloads/cdtools/CHECKOUT_DATE.TXT) is 2026-03-16 and the
[CHANGELOG](http://cs.christophwernhard.com/cdtools/downloads/cdtools/CHANGELOG.TXT) names THGEN addition on that date. This is a usable
research source release, not evidence of later maintenance or a support promise.
The August 2026 paper revision is separately versioned. The exact source hashes,
not the paper date or a mutable download URL, identify the inspected implementation.

[README](http://cs.christophwernhard.com/cdtools/downloads/cdtools/README.TXT) specifies Unix/Linux, SWI-Prolog tested at 10.0.0 and PIE;
external provers/TPTP/TreeRePair are optional or path-specific. The
[Metamath README](http://cs.christophwernhard.com/cdtools/downloads/cdtools/README_METAMATH.TXT) describes generated `.pl`/`.qlf` caches
and a particular set.mm version. Its setup workload is not free and must not be run
against a full unregistered corpus as an incidental install step.

The separate [2023 lemma repo](https://github.com/zsoltzombori/lemma/tree/2cba14d3b4b359d4bc491ba3b7541771a2c8900e)
is pinned to `2cba14d3b4b359d4bc491ba3b7541771a2c8900e` (March2023 last commit).
[model.py](https://raw.githubusercontent.com/zsoltzombori/lemma/2cba14d3b4b359d4bc491ba3b7541771a2c8900e/model.py), lines1–3 and58–75, imports torch/GCN and represents
its linear selector using `torch.nn.Linear`. That entire module is excluded. The
inspected recursive tree contains no license-named file, and GitHub metadata reports
license null: reuse rights were not established for that separate repository.
The pure CD Tools GPL modules remain the first implementation candidate.
