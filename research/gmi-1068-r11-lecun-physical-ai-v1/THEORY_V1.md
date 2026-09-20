# R11 — GMI translation of LeCun/JEPA/world-model/physical-AI programme

A GMI world model is not a primitive module. It is a representation z=q(h) together with an admissible predictive process P(z,a)->z' that is sufficient for the future contextual questions/planning problem being solved.

JEPA-style prediction in representation space is interpreted as predicting a quotient/representation rather than reconstructing all raw observation coordinates.

## Sufficiency/resource theorem (finite witness)
Let raw observation X=(T,N), with T task-relevant and N nuisance. If every contextual target depends only on T, representation Z=T is sufficient. It uses one bit rather than the two-bit raw state and can preserve target accuracy exactly. If the target changes to (T,N), the same quotient is no longer sufficient: histories differing only in N collapse and no decoder from Z can recover the required target.

Thus representation-space prediction is favored only when the discarded distinctions are irrelevant enough relative to resource savings. It is not universally superior to reconstruction.

## Planning
Model-predictive planning is search/composition over predicted future contextual values. With an exact predictive process, the model search agrees with true finite dynamics. Approximation error, multimodal futures, partial observability and planning cost can reverse the preference relative to reactive/model-free/search-based alternatives.

## Collapse boundary
A constant encoder and constant predictor can make a pure joint-embedding matching loss zero. Therefore predictive agreement alone does not guarantee task-relevant information. Anti-collapse constraints, architectural asymmetries, variance/covariance/Gaussian regularization, inverse-dynamics discrimination, etc. are additional assumptions/mechanisms whose scientific value is empirical/theoretical, not ontological.

## Embodiment / physical AI
Physical AI is ordinary GMI with sensor/action interface objects, physical substrate restrictions on admissible processes, interaction histories, and context values tied to physical consequences. It is not a new fundamental category of intelligence.

## Energy
Energy-based objectives instantiate a context/order over candidate states/actions. They can be useful without being a universal intelligence primitive.

## Hostile ecologies
- purely reactive target: a world model adds cost without capability gain;
- raw-detail target: aggressive latent quotient loses required information;
- multimodal future: deterministic point prediction can erase modes needed by the context;
- action-irrelevant world: planning is unnecessary overhead;
- wrong long-horizon dynamics: model error can compound and make reactive/search alternatives preferable.

Claim ceiling:
GRAND_GMI_V2_R11_GMI_TRANSLATION_OF_LECUN_JEPA_WORLD_MODEL_AND_PHYSICAL_AI_PROGRAMME_AT_REGISTERED_SOURCE_SCOPE
