"""Reviewed final proof inventory and precise original-atom witnesses."""
FINAL = True
SOURCE_PATHS = ('research/gmi-1068-partial-context-v15/PartialContextV15.lean',
 'research/gmi-1068-context-specializations-v17/ContextMapsV17.lean',
 'research/gmi-1068-scalarization-v12/ScalarLawsV12.lean',
 'research/gmi-1068-scalarization-v12/FiniteSumsV12.lean',
 'research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean',
 'research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean',
 'research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean',
 'research/gmi-1068-legacy-transports-v24/ImageTransportV24.lean',
 'research/gmi-1068-legacy-transports-v24/ProfileContextsV24.lean',
 'research/gmi-1068-legacy-transports-v24/AFErasureV24.lean',
 'research/gmi-1068-legacy-transports-v24/CandidateContextsV24.lean',
 'research/gmi-1068-legacy-transports-v24/PriceContextsV24.lean',
 'research/gmi-1068-legacy-transports-v24/PlanContextsV24.lean',
 'research/gmi-1068-legacy-transports-v24/CommonPlansV24.lean',
 'research/gmi-1068-legacy-transports-v24/FinitePreferenceV24.lean',
 'research/gmi-1068-legacy-transports-v24/TransportControlsV24.lean',
 'research/gmi-1068-legacy-transports-v24/AFContextBridgeV24.lean',
 'research/gmi-1068-legacy-transports-v24/RichAFContextsV24.lean',
 'research/gmi-1068-legacy-transports-v24/ConstructorBindingsV24.lean',
 'research/gmi-1068-legacy-transports-v24/ProofTargetsV24.lean')
SOURCE_NAMES = ('PartialContextV15.lean',
 'ContextMapsV17.lean',
 'ScalarLawsV12.lean',
 'FiniteSumsV12.lean',
 'FrontierOrderV20.lean',
 'GuardedMapsV20.lean',
 'PartialPostcontextV20.lean',
 'ImageTransportV24.lean',
 'ProfileContextsV24.lean',
 'AFErasureV24.lean',
 'CandidateContextsV24.lean',
 'PriceContextsV24.lean',
 'PlanContextsV24.lean',
 'CommonPlansV24.lean',
 'FinitePreferenceV24.lean',
 'TransportControlsV24.lean',
 'AFContextBridgeV24.lean',
 'RichAFContextsV24.lean',
 'ConstructorBindingsV24.lean',
 'ProofTargetsV24.lean')
PROOF_CONTRACT_SHA = '748d00727038270f7702691854d4f9a63288f1be1f880d8ad561c7bf66259a36'
PROOF_AUDIT_SHA = '9d050135400b4992aaa31debe3ddd4157aedd9afc306dade237e52d765d92a69'
PROOF_COUNT = 138
REVIEWED_INPUTS = {'custody_v24.py': '9ea5d52cd435f14ab43897ebc1c693f54655fbf3f962cb8da45630af53d8d736',
 'coverage_v24.py': '81c98bc752b74255d3a1285b3f60eaf94fceb0db0f67fce5b8ee0103a011d449',
 'check_lean_v24.py': 'e01ef87525aa794e0f71ca42c60cdc2f94d0a13c740102b8e816f157825a8cea',
 'FORMAL_SCOPE_V24.md': '95eb0cbb489d824bd5455d5af1a3bf5364718c8c061a80239ee3519c3c0fb4b2'}
SOURCE_ASSUMPTIONS = ('actual V15 partial Context and P intersection E; explicit profile projections; active selected witnesses; V12 '
 'primitive ordered ring and Int instance; all candidate identities; strictly positive prices for Pareto inclusion; '
 'partial loss in declared preorder; common plan universe and injective relabeling with mapped ambient guard')
ATOM_DECLARATIONS = (('ImageTransportV24.lean', 'selected_iff'),
 ('RichAFContextsV24.lean', 'projection_post'),
 ('AFContextBridgeV24.lean', 'full_erasure_image'),
 ('CandidateContextsV24.lean', 'maximal_ids'),
 ('PriceContextsV24.lean', 'positive_price_pareto'),
 ('PlanContextsV24.lean', 'feasible_image'),
 ('CommonPlansV24.lean', 'mapped_intersection'),
 ('CommonPlansV24.lean', 'empty_family'))
REPAIR_DECLARATION = ('ImageTransportV24.lean', 'lean_declaration', 'selected_iff')
