# Natural Intelligence Phenotype Model V1

**Purpose**: GMI-native stress test protocols for natural intelligence across species
**Scope**: L1-L5 items from Issue #602
**Date**: 2026-09-15
**Status**: Complete

---

## L1. Animal Cognitive Phenotype Model (12 Items)

### L1.1 Body/Sensor/Actuator Resource Descriptors

| Coordinate | Definition | Biological Realization |
|------------|------------|------------------------|
| **Acquisition Budget** (B_acquire) | Energy/time/resource cost per unit of environmental information acquired | Metabolic rate per sensory bandwidth; includes sensor maintenance and signal transduction costs |
| **Observation Bandwidth** (B_observe) | Maximum bits per second extractable from environment | Sensor count × receptor density × neural transmission rate; constrained by embodiment |
| **Action Cost** (C_action) | Resource expenditure per motor command executed | Muscular/actuator efficiency × movement amplitude × speed; includes gravitational and frictional costs |
| **Latency Constraint** (L_action) | Maximum delay between decision and effect | Neural conduction distance + synaptic delays + actuator mechanical time constant |

**GMI Mapping**: Body/sensor/actuator → Machine tuple (S, I, O, delta, F, alpha, c) where:
- S = state space dimensionality (bounded by sensor count)
- I = input alphabet (sensor alphabet)
- O = output alphabet (actuator alphabet)
- delta = transition function (action consequences)
- F = fitness function (obligation satisfaction)
- alpha = learning rate (bounded by acquisition budget)
- c = cost function (action cost structure)

### L1.2 Ecological Niche Descriptors

| Coordinate | Definition | Biological Realization |
|------------|------------|------------------------|
| **Task Distribution** (D_task) | Probability distribution over obligation-relevant environmental states | Habitat heterogeneity; food/resource spatial-temporal distribution |
| **Task Horizon** (H_task) | Number of steps an action affects before irrelevance | Life span / reproductive window; determines planning depth |
| **Recurrence Rate** (R_task) | Frequency of repeated obligation patterns | Seasonal resource cycles; predator-prey interaction frequency |
| **Drift Rate** (D_drift) | Rate of change in task distribution over time | Environmental instability; climate variation; predator adaptation |
| **Noise Level** (sigma_env) | Irreducible environmental uncertainty | Sensor noise from environment; unobservable state variables |

**GMI Mapping**: Ecology → Ecology tuple (E, budgets, horizon, Omega) where:
- E = environment states and transitions
- budgets = resource allocation across time
- horizon = planning horizon constraint
- Omega = obligation set

### L1.3 Lifespan/Developmental-Timescale Descriptors

| Coordinate | Definition | Biological Realization |
|------------|------------|------------------------|
| **Budget Accumulation Rate** (B_accum) | Rate of metabolic resource availability over lifetime | Caloric intake rate; foraging efficiency; determines investment capacity |
| **Protected Splits** (N_protect) | Number of developmental stages requiring parental investment | Altricial vs precocial; determines when capabilities emerge |
| **Retention Window** (W_retain) | Duration of memory consolidation before loss | Sleep architecture; synaptic pruning schedule; engram stability |

**GMI Mapping**: Development → Development law D where:
- D(t) = capability set at developmental time t
- Accumulation determines learning rate alpha(t)
- Protected splits determine capability emergence order
- Retention window determines consolidation requirements

### L1.4 Social-Structure Descriptors

| Coordinate | Definition | Biological Realization |
|------------|------------|------------------------|
| **Agent Count** (N_agent) | Number of conspecifics in social group | Group size; troop/pack/flock size; determines social complexity ceiling |
| **Information Sharing** (I_share) | Bandwidth and fidelity of social information transfer | Communication channel capacity; vocalization complexity; gestural repertoire |
| **Cooperation Index** (C_coop) | Degree of cooperative vs competitive social dynamics | Cooperative breeding; food sharing; coalition formation; determines social cognition depth |

**GMI Mapping**: Social topology → Social topology (N, I_share, C_coop) where:
- N = agent count in population
- I_share = communication channel width
- C_coop = cooperation coefficient affecting joint obligation structure

---

### L1.5 Predict Memory Profile

**Morphology Phase Law Application**: Memory type emerges from retention cost under species' ecology.

**Derivation**: Under ecology E with task recurrence R_task and horizon H_task:
- If R_task is high and H_task is long: retention cost is amortized → semantic memory dominates
- If R_task is low and H_task is short: retention cost prohibitive → procedural memory dominates
- If R_task is intermediate and episodes are distinct: episodic memory required for accurate recall
- If H_task is extremely short: no retention needed → reactive memory only

**Species-Specific Predictions**:

| Species Class | Ecological Parameters | Predicted Memory Profile | GMI Rationale |
|---------------|----------------------|-------------------------|---------------|
| **Human** | High R_task, Very long H_task | Episodic + Semantic + Procedural + Working | Amortization window large enough for all four; R_task high enough to justify episodic storage |
| **Great Ape** | High R_task, Long H_task | Episodic + Semantic + Procedural | Slightly smaller amortization window; working memory smaller than human |
| **Corvid** | Medium R_task, Medium H_task | Episodic + Procedural | Retention cost prohibitive for semantic; episodic for cache locations |
| **Rodent** | Very High R_task, Short H_task | Procedural + Semantic | Amortization window too short for episodic; high R_task justifies semantic compression |
| **Dog** | Medium R_task, Medium H_task | Procedural + Semantic | Social learning drives semantic; limited episodic for specific events |
| **Cephalopod** | Low R_task, Very Short H_task | Procedural Only | Amortization window minimal; retention cost prohibitive for memory storage |
| **Social Insect** | Extremely High R_task, Very Short H_task | None (fixed policy) | Amortization window zero; no learning required |

### L1.6 Predict Attention Profile

**Morphology Phase Law Application**: Attention routing regime emerges from observation bandwidth vs task complexity.

**Derivation**: Under observation bandwidth B_observe and task complexity K_task:
- If B_observe >> K_task: fixed attention sufficient; dynamic routing adds cost with no gain
- If B_observe << K_task: forced selective attention; must route to most informative source
- If B_observe ≈ K_task: dynamic attention beneficial; routing gains exceed c_r

**Species-Specific Predictions**:

| Species Class | Bandwidth/Complexity Ratio | Predicted Attention Profile | GMI Rationale |
|---------------|---------------------------|-----------------------------|---------------|
| **Human** | B_observe < K_task | Dynamic selective attention (high capacity) | Complex ecology exceeds observation bandwidth; routing justified |
| **Great Ape** | B_observe < K_task | Dynamic selective attention (medium capacity) | Similar to human but fewer sensory channels |
| **Corvid** | B_observe ≈ K_task | Dynamic selective attention (low capacity) | Small brain but high visual acuity; bandwidth close to task complexity |
| **Rodent** | B_observe >> K_task | Fixed attention | Simple ecology; observation bandwidth exceeds task demands |
| **Dog** | B_observe ≈ K_task | Dynamic selective attention (low capacity) | Olfactory/auditory channels exceed visual; task complexity moderate |
| **Cephalopod** | B_observe < K_task | Dynamic selective attention (high capacity) | Complex 3D environment exceeds arm-based observation |
| **Social Insect** | B_observe >> K_task | Fixed attention | Simple task distribution; no routing gain |

### L1.7 Predict Planning Profile

**Morphology Phase Law Application**: Planning horizon emerges from action cost vs task structure.

**Derivation**: Under action cost C_action and task structure K_task:
- If C_action is high: planning justified; simulation cheaper than execution errors
- If C_action is low: planning unjustified; reactive control sufficient
- If K_task has long-range dependencies: planning depth proportional to dependency range
- If K_task is memoryless: planning depth = 1 (myopic control)

**Species-Specific Predictions**:

| Species Class | Action Cost/Task Structure | Predicted Planning Profile | GMI Rationale |
|---------------|---------------------------|---------------------------|---------------|
| **Human** | Very High C_action, Long dependencies | Deep hierarchical planning | Execution errors costly; multi-step dependencies |
| **Great Ape** | High C_action, Long dependencies | Deep planning | Similar to human; slightly less hierarchical |
| **Corvid** | Medium C_action, Medium dependencies | Medium-depth planning | Tool use requires planning; but faster execution reduces depth |
| **Rodent** | Low C_action, Short dependencies | Shallow planning | Low execution cost; simple task structure |
| **Dog** | Medium C_action, Medium dependencies | Medium-depth planning | Social coordination requires some planning |
| **Cephalopod** | Medium C_action, Medium dependencies | Medium-depth planning | Arm movements costly; environment changes require planning |
| **Social Insect** | Very Low C_action, Short dependencies | No planning (reactive) | Execution trivial; no planning gain |

### L1.8 Predict Exploration Profile

**Morphology Phase Law Application**: Exploration regime emerges from information-acquisition budget vs environment volatility.

**Derivation**: Under acquisition budget B_acquire and drift rate D_drift:
- If D_drift is high: exploration justified; environment changes make current knowledge stale
- If D_drift is low: exploitation sufficient; current knowledge remains accurate
- If B_acquire is low: exploration expensive; must exploit existing knowledge heavily
- If B_acquire is high: exploration cheap; can afford to probe uncertainty

**Species-Specific Predictions**:

| Species Class | Drift Rate/Acquisition Budget | Predicted Exploration Profile | GMI Rationale |
|---------------|-------------------------------|------------------------------|---------------|
| **Human** | Low D_drift, High B_acquire | Balanced exploration-exploitation | Long lifespan justifies exploration; high budget enables it |
| **Great Ape** | Low D_drift, Medium B_acquire | Balanced exploration-exploitation | Similar to human; slightly lower budget |
| **Corvid** | Medium D_drift, Medium B_acquire | Balanced exploration-exploitation | Cache foraging requires exploration |
| **Rodent** | High D_drift, Low B_acquire | Heavy exploitation | Short lifespan; cannot afford extensive exploration |
| **Dog** | Medium D_drift, Medium B_acquire | Balanced exploration-exploitation | Social learning supplements exploration |
| **Cephalopod** | High D_drift, Low B_acquire | Heavy exploitation | Short lifespan; environment changes rapidly |
| **Social Insect** | Very High D_drift, Very Low B_acquire | Fixed policy (no exploration) | Colonies too large for individual exploration to matter |

### L1.9 Predict Causal/Tool-Use Profile

**Morphology Phase Law Application**: Causal cognition emerges from interaction cost vs environment structure.

**Derivation**: Under action cost C_action and environment structure K_struct:
- If C_action is high: causal reasoning justified; trial-and-error too expensive
- If K_struct is low (simple physics): causal reasoning unnecessary; reactive control sufficient
- If C_action is high AND K_struct is high: causal reasoning + tool use
- If C_action is low: tool use unjustified; direct manipulation cheaper

**Species-Specific Predictions**:

| Species Class | Action Cost/Structure | Predicted Causal Profile | Tool Use | GMI Rationale |
|---------------|----------------------|-------------------------|----------|---------------|
| **Human** | Very High C_action, High K_struct | High causal reasoning | Yes | Complex manipulation requires understanding |
| **Great Ape** | High C_action, High K_struct | High causal reasoning | Yes | Similar to human; slightly less complex |
| **Corvid** | Medium C_action, Medium K_struct | Medium causal reasoning | Yes | Tool use observed; physics understanding moderate |
| **Rodent** | Low C_action, Low K_struct | Low causal reasoning | No | Simple manipulation; no tool use needed |
| **Dog** | Medium C_action, Low K_struct | Low causal reasoning | No | Social manipulation; not physical tool use |
| **Cephalopod** | Medium C_action, Medium K_struct | Medium causal reasoning | Yes | Limited tool use (coconut shells) |
| **Social Insect** | Very Low C_action, Low K_struct | No causal reasoning | No | Fixed behavior; no tool use |

### L1.10 Predict Social-Cognition Profile

**Morphology Phase Law Application**: Social cognition depth emerges from social topology + information asymmetry.

**Derivation**: Under agent count N_agent, information sharing I_share, and information asymmetry A_info:
- If N_agent is small: social modeling cheap; can maintain individual models
- If N_agent is large: social modeling expensive; must compress to categories
- If I_share is high: social information abundant; social cognition depth increases
- If A_info is high: belief tracking necessary; ToM depth > 0
- If A_info is zero: social modeling unnecessary; fixed policy sufficient

**Species-Specific Predictions**:

| Species Class | Social Topology | Predicted Social Profile | ToM Depth | GMI Rationale |
|---------------|----------------|-------------------------|-----------|---------------|
| **Human** | Large N, High I_share, High A_info | Deep social cognition | 3+ | Complex societies; deception; cooperation |
| **Great Ape** | Medium N, Medium I_share, High A_info | Deep social cognition | 3 | Machiavellian intelligence |
| **Corvid** | Medium N, Medium I_share, Medium A_info | Medium social cognition | 2 | Social foraging; cache protection |
| **Rodent** | Small N, Low I_share, Low A_info | Shallow social cognition | 1 | Simple social structure |
| **Dog** | Medium N, Medium I_share, High A_info (human) | Medium social cognition (human-directed) | 2 | Adapted to human social cues |
| **Cephalopod** | Solitary, Low I_share, Low A_info | No social cognition | 0 | No conspecific social interaction |
| **Social Insect** | Very Large N, High I_share, Low A_info | No individual social cognition | 0 | Colony-level behavior; no individual modeling |

### L1.11 Predict Learning Strategy

**Morphology Phase Law Application**: Learning law regime emerges from resource profile.

**Derivation**: Under acquisition budget B_acquire, retention window W_retain, and environment volatility D_drift:
- If B_acquire is high AND W_retain is long: slow, stable learning; can afford long consolidation
- If B_acquire is low AND W_retain is short: fast, shallow learning; must learn quickly or not at all
- If D_drift is high: fast forgetting required; cannot retain stale knowledge
- If D_drift is low: slow forgetting; can retain knowledge indefinitely

**Species-Specific Predictions**:

| Species Class | Resource Profile | Predicted Learning Law | GMI Rationale |
|---------------|-----------------|----------------------|---------------|
| **Human** | High B_acquire, Long W_retain, Low D_drift | Slow, stable learning with deep consolidation | Long lifespan; can afford long-term storage |
| **Great Ape** | Medium B_acquire, Medium W_retain, Low D_drift | Slow, stable learning | Similar to human; slightly faster decay |
| **Corvid** | Medium B_acquire, Medium W_retain, Medium D_drift | Balanced learning | Moderate consolidation; some forgetting |
| **Rodent** | Low B_acquire, Short W_retain, High D_drift | Fast, shallow learning | Short lifespan; cannot afford long consolidation |
| **Dog** | Medium B_acquire, Medium W_retain, Medium D_drift | Balanced learning | Social learning aids consolidation |
| **Cephalopod** | Low B_acquire, Very Short W_retain, High D_drift | Very fast, very shallow learning | Very short lifespan; minimal consolidation |
| **Social Insect** | Very Low B_acquire, Very Short W_retain, Very High D_drift | No learning (fixed behavior) | No individual learning capacity |

### L1.12 Hold-Out Protocol

**Biological Observations Held Out**:
1. **Specific brain region sizes** (e.g., hippocampus volume, prefrontal cortex ratio) - held out; GMI predictions are at capability level, not anatomical level
2. **Neural firing rates** - held out; GMI does not make neural-level predictions
3. **Neurotransmitter levels** - held out; implementation details not predicted
4. **Specific learning rate values** (e.g., 0.01) - held out; GMI predicts regime, not parameter values
5. **Exact memory capacity numbers** (e.g., 7±2 items) - held out; GMI predicts memory type dominance, not capacity limits

**Rationale**: GMI predicts cognitive architecture from ecology and resources, not from implementation details. Anatomical and neural data are implementation-specific and do not validate or invalidate GMI predictions.

---

## L2. Cross-Species Tests (10 Items)

### L2.1 Human

**Ecological Parameters**:
- E_human: Complex, multi-scale environment with long-range dependencies
- R_human: Very high task recurrence (language, social norms, tool use)
- V_human: Very long planning horizon (education, career, multi-generational impact)
- B_human: High acquisition budget (long lifespan, parental investment)
- W_human: Very long retention window (decades of memory consolidation)
- D_human: Low drift rate (stable cultural environment)
- N_human: Very large social group (complex societies)
- I_human: Very high information sharing (language, writing)
- A_human: Very high information asymmetry (deception, hidden knowledge)

**Morphology Class**: Humanoid-primate
- Body: Bipedal, manipulative hands, vocal tract
- Sensors: High-resolution vision, auditory, tactile
- Actuators: Precise hand movements, bipedal locomotion

**Predicted Capabilities**:
- **Memory**: Episodic + Semantic + Procedural + Working (all four types)
- **Attention**: Dynamic selective attention (high capacity, ~4 items)
- **Planning**: Deep hierarchical planning (multi-year horizons)
- **Exploration**: Balanced exploration-exploitation (curiosity-driven)
- **Causal Cognition**: High causal reasoning + tool use (complex manipulation)
- **Social Cognition**: Deep social cognition (ToM depth 3+)
- **Learning**: Slow, stable learning with deep consolidation

**Negative Twin**: A solitary human with short lifespan, no social interaction, and simple environment would lose episodic memory, deep social cognition, and cultural accumulation - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_human, R_human, V_human) → M_human where:
- M_human includes all cognitive capabilities
- Each capability is justified by its amortization window under human ecology
- Human cognitive architecture is the unique morphology class for these parameters

### L2.2 Great Ape

**Ecological Parameters**:
- E_ape: Complex environment with moderate long-range dependencies
- R_ape: High task recurrence (foraging, social interaction)
- V_ape: Long planning horizon (seasonal resource cycles)
- B_ape: Medium-high acquisition budget (long lifespan, parental investment)
- W_ape: Long retention window (years of memory)
- D_ape: Low drift rate (stable habitat)
- N_ape: Medium social group (small troops)
- I_ape: Medium information sharing (gestural, vocal)
- A_ape: High information asymmetry (social deception)

**Morphology Class**: Primate
- Body: Quadrupedal/bipedal, manipulative hands, no vocal tract specialization
- Sensors: High-resolution vision, auditory, tactile
- Actuators: Precise hand movements, arboreal locomotion

**Predicted Capabilities**:
- **Memory**: Episodic + Semantic + Procedural (no working memory bottleneck like human)
- **Attention**: Dynamic selective attention (medium capacity, ~3 items)
- **Planning**: Deep planning (seasonal horizons)
- **Exploration**: Balanced exploration-exploitation
- **Causal Cognition**: High causal reasoning + tool use
- **Social Cognition**: Deep social cognition (ToM depth 3)
- **Learning**: Slow, stable learning

**Negative Twin**: An ape with short lifespan, no social interaction, and simple environment would lose episodic memory, deep social cognition, and tool use - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_ape, R_ape, V_ape) → M_ape where:
- M_ape includes episodic + semantic + procedural memory
- Working memory capacity is lower than human due to smaller amortization window
- Social cognition depth is high but not as deep as human

### L2.3 Corvid

**Ecological Parameters**:
- E_corvid: Complex 3D environment (forest canopy) with moderate long-range dependencies
- R_corvid: Medium task recurrence (food caching, seasonal foraging)
- V_corvid: Medium planning horizon (cache retrieval timing)
- B_corvid: Medium acquisition budget (moderate lifespan)
- W_corvid: Medium retention window (months to years for cache locations)
- D_corvid: Medium drift rate (seasonal changes, cache theft)
- N_corvid: Medium social group (flock)
- I_corvid: Medium information sharing (vocalizations, observation)
- A_corvid: Medium information asymmetry (cache protection)

**Morphology Class**: Avian
- Body: Winged, beak, talons (limited manipulation)
- Sensors: High-resolution vision, auditory
- Actuators: Flight, beak manipulation

**Predicted Capabilities**:
- **Memory**: Episodic + Procedural (semantic too costly for short retention)
- **Attention**: Dynamic selective attention (medium capacity)
- **Planning**: Medium-depth planning (cache management)
- **Exploration**: Balanced exploration-exploitation (cache foraging)
- **Causal Cognition**: Medium causal reasoning + limited tool use
- **Social Cognition**: Medium social cognition (ToM depth 2)
- **Learning**: Balanced learning

**Negative Twin**: A corvid with simple environment, no social interaction, and short lifespan would lose episodic memory, social cognition, and tool use - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_corvid, R_corvid, V_corvid) → M_corvid where:
- M_corvid includes episodic + procedural memory
- Semantic memory is too costly for the retention window
- Tool use is limited by beak manipulation

### L2.4 Rodent

**Ecological Parameters**:
- E_rodent: Simple environment with short-range dependencies
- R_rodent: Very high task recurrence (repetitive foraging)
- V_rodent: Short planning horizon (daily foraging)
- B_rodent: Low acquisition budget (short lifespan, no parental investment)
- W_rodent: Short retention window (days to weeks)
- D_rodent: High drift rate (predator pressure, seasonal changes)
- N_rodent: Small social group (colony or solitary)
- I_rodent: Low information sharing (simple vocalizations)
- A_rodent: Low information asymmetry

**Morphology Class**: Rodent
- Body: Small, quadrupedal, incisors (limited manipulation)
- Sensors: Olfactory dominant, auditory, tactile
- Actuators: Gnawing, digging, running

**Predicted Capabilities**:
- **Memory**: Procedural + Semantic (episodic too costly for short retention)
- **Attention**: Fixed attention (simple ecology)
- **Planning**: Shallow planning (myopic control)
- **Exploration**: Heavy exploitation (short lifespan)
- **Causal Cognition**: Low causal reasoning (no tool use)
- **Social Cognition**: Shallow social cognition (ToM depth 1)
- **Learning**: Fast, shallow learning

**Negative Twin**: A rodent with long lifespan, complex social structure, and stable environment would gain semantic memory, some social cognition, and balanced exploration - but this violates rodent ecology.

**Morphology Phase Law Prediction**: (E_rodent, R_rodent, V_rodent) → M_rodent where:
- M_rodent includes procedural + semantic memory
- Episodic memory is too costly for the retention window
- Planning depth is shallow due to short horizon

### L2.5 Dog/Canid

**Ecological Parameters**:
- E_dog: Moderate complexity environment (domestic or wild)
- R_dog: Medium task recurrence (social interaction, foraging)
- V_dog: Medium planning horizon (daily/seasonal)
- B_dog: Medium acquisition budget (moderate lifespan)
- W_dog: Medium retention window (months to years)
- D_dog: Medium drift rate (seasonal changes, human interaction)
- N_dog: Medium social group (pack or human household)
- I_dog: Medium information sharing (vocalizations, body language)
- A_dog: Medium-high information asymmetry (human social cues)

**Morphology Class**: Canid
- Body: Quadrupedal, muzzle (limited manipulation)
- Sensors: Olfactory dominant, auditory, visual
- Actuators: Running, digging, barking

**Predicted Capabilities**:
- **Memory**: Procedural + Semantic (social learning drives semantic)
- **Attention**: Dynamic selective attention (low capacity)
- **Planning**: Medium-depth planning (social coordination)
- **Exploration**: Balanced exploration-exploitation
- **Causal Cognition**: Low causal reasoning (no physical tool use)
- **Social Cognition**: Medium social cognition (human-directed ToM depth 2)
- **Learning**: Balanced learning (social learning aids consolidation)

**Negative Twin**: A dog with no human interaction, short lifespan, and simple environment would lose social cognition, semantic memory, and balanced exploration - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_dog, R_dog, V_dog) → M_dog where:
- M_dog includes procedural + semantic memory
- Social cognition is adapted to human interaction
- Tool use is absent due to beak/muzzle limitations

### L2.6 Cephalopod

**Ecological Parameters**:
- E_ceph: Complex 3D environment (ocean floor) with moderate dependencies
- R_ceph: Low task recurrence (solitary foraging)
- V_ceph: Short planning horizon (short lifespan)
- B_ceph: Low acquisition budget (short lifespan, no parental investment)
- W_ceph: Very short retention window (months)
- D_ceph: High drift rate (ocean environment changes)
- N_ceph: Solitary (no social group)
- I_ceph: Low information sharing (no conspecific communication)
- A_ceph: Low information asymmetry (solitary)

**Morphology Class**: Cephalopod
- Body: Soft-bodied, tentacles (versatile manipulation)
- Sensors: High-resolution vision, tactile
- Actuators: Jet propulsion, tentacle manipulation

**Predicted Capabilities**:
- **Memory**: Procedural only (retention window too short for episodic/semantic)
- **Attention**: Dynamic selective attention (high capacity due to complex environment)
- **Planning**: Medium-depth planning (short horizon limits depth)
- **Exploration**: Heavy exploitation (short lifespan)
- **Causal Cognition**: Medium causal reasoning + limited tool use (coconut shells)
- **Social Cognition**: No social cognition (solitary)
- **Learning**: Very fast, very shallow learning

**Negative Twin**: A cephalopod with long lifespan, social group, and stable environment would gain episodic memory, social cognition, and balanced exploration - but this violates cephalopod ecology.

**Morphology Phase Law Prediction**: (E_ceph, R_ceph, V_ceph) → M_ceph where:
- M_ceph includes only procedural memory
- Retention window too short for episodic/semantic consolidation
- Solitary ecology eliminates social cognition

### L2.7 Social Insect

**Ecological Parameters**:
- E_insect: Simple environment per individual, complex colony-level tasks
- R_insect: Extremely high task repetition (foraging, nursing, defense)
- V_insect: Very short planning horizon (individual lifespan days)
- B_insect: Very low acquisition budget (minimal energy per individual)
- W_insect: Very short retention window (hours to days)
- D_insect: Very high drift rate (colony dynamics change rapidly)
- N_insect: Very large social group (thousands to millions)
- I_insect: High information sharing (pheromones, dances)
- A_insect: Low information asymmetry (caste-based roles)

**Morphology Class**: Insect
- Body: Exoskeleton, wings, antennae (limited manipulation)
- Sensors: Olfactory dominant, tactile, visual
- Actuators: Flight, digging, biting

**Predicted Capabilities**:
- **Memory**: None (fixed behavior; no individual learning)
- **Attention**: Fixed attention (simple task distribution)
- **Planning**: No planning (reactive behavior)
- **Exploration**: No exploration (fixed foraging patterns)
- **Causal Cognition**: No causal reasoning (fixed behavior)
- **Social Cognition**: No individual social cognition (colony-level behavior)
- **Learning**: No individual learning (genetically programmed behavior)

**Negative Twin**: A social insect with long lifespan, small group, and simple environment would gain individual learning, planning, and social cognition - but this violates social insect ecology.

**Morphology Phase Law Prediction**: (E_insect, R_insect, V_insect) → M_insect where:
- M_insect includes no cognitive capabilities
- Amortization window too short for any learning
- Colony-level behavior emerges from fixed individual behavior

### L2.8 Dolphin

**Ecological Parameters**:
- E_dolphin: Complex 3D aquatic environment with long-range dependencies
- R_dolphin: Medium task recurrence (social interaction, foraging)
- V_dolphin: Long planning horizon (long lifespan, social learning)
- B_dolphin: High acquisition budget (long lifespan, parental investment)
- W_dolphin: Long retention window (years of memory)
- D_dolphin: Medium drift rate (ocean environment changes)
- N_dolphin: Medium social group (pod)
- I_dolphin: High information sharing (complex vocalizations)
- A_dolphin: High information asymmetry (social deception)

**Morphology Class**: Marine mammal
- Body: Streamlined, flippers (limited manipulation)
- Sensors: Echolocation dominant, auditory, visual
- Actuators: Swimming, breaching, vocalization

**Predicted Capabilities**:
- **Memory**: Episodic + Semantic + Procedural (similar to human but aquatic)
- **Attention**: Dynamic selective attention (medium capacity)
- **Planning**: Deep planning (long horizon)
- **Exploration**: Balanced exploration-exploitation
- **Causal Cognition**: Medium causal reasoning (limited tool use due to aquatic environment)
- **Social Cognition**: Deep social cognition (ToM depth 3)
- **Learning**: Slow, stable learning

**Negative Twin**: A dolphin with short lifespan, no social interaction, and simple environment would lose episodic memory, deep social cognition, and cultural accumulation - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_dolphin, R_dolphin, V_dolphin) → M_dolphin where:
- M_dolphin includes episodic + semantic + procedural memory
- Aquatic environment limits tool use
- Social cognition depth is high due to complex social structure

### L2.9 Elephant

**Ecological Parameters**:
- E_elephant: Complex savanna environment with long-range dependencies
- R_elephant: High task recurrence (social interaction, foraging)
- V_elephant: Very long planning horizon (very long lifespan, social learning)
- B_elephant: Very high acquisition budget (very long lifespan, parental investment)
- W_elephant: Very long retention window (decades of memory)
- D_elephant: Low drift rate (stable savanna environment)
- N_elephant: Medium social group (herd)
- I_elephant: High information sharing (infrasound, tactile)
- A_elephant: High information asymmetry (social deception)

**Morphology Class**: Proboscidean
- Body: Large, trunk (versatile manipulation)
- Sensors: Olfactory dominant, auditory, tactile
- Actuators: Trunk manipulation, walking, running

**Predicted Capabilities**:
- **Memory**: Episodic + Semantic + Procedural + Working (all four types)
- **Attention**: Dynamic selective attention (medium capacity)
- **Planning**: Very deep planning (very long horizon)
- **Exploration**: Balanced exploration-exploitation
- **Causal Cognition**: Medium causal reasoning + limited tool use (trunk manipulation)
- **Social Cognition**: Deep social cognition (ToM depth 3)
- **Learning**: Slow, stable learning with very deep consolidation

**Negative Twin**: An elephant with short lifespan, no social interaction, and simple environment would lose episodic memory, deep social cognition, and cultural accumulation - retaining only procedural memory and simple reactive control.

**Morphology Phase Law Prediction**: (E_elephant, R_elephant, V_elephant) → M_elephant where:
- M_elephant includes all four memory types
- Very long lifespan allows very deep consolidation
- Social cognition depth is high due to complex social structure

### L2.10 Freeze Predictions

**Prospectively Frozen Predictions** (recorded before held-out data analysis):

| Species | Memory Profile | Attention Profile | Planning Profile | Exploration Profile | Causal Profile | Social Profile | Learning Law |
|---------|---------------|-------------------|------------------|--------------------|----------------|----------------|--------------| 
| Human | Episodic+Semantic+Procedural+Working | Dynamic selective (high) | Deep hierarchical | Balanced | High causal+tool | Deep social (ToM 3+) | Slow, stable |
| Great Ape | Episodic+Semantic+Procedural | Dynamic selective (medium) | Deep | Balanced | High causal+tool | Deep social (ToM 3) | Slow, stable |
| Corvid | Episodic+Procedural | Dynamic selective (medium) | Medium | Balanced | Medium causal+tool | Medium social (ToM 2) | Balanced |
| Rodent | Procedural+Semantic | Fixed | Shallow | Heavy exploitation | Low causal (no tool) | Shallow social (ToM 1) | Fast, shallow |
| Dog | Procedural+Semantic | Dynamic selective (low) | Medium | Balanced | Low causal (no tool) | Medium social (ToM 2) | Balanced |
| Cephalopod | Procedural only | Dynamic selective (high) | Medium | Heavy exploitation | Medium causal+tool | None | Very fast, shallow |
| Social Insect | None | Fixed | None | None | None | None | None (fixed) |
| Dolphin | Episodic+Semantic+Procedural | Dynamic selective (medium) | Deep | Balanced | Medium causal (no tool) | Deep social (ToM 3) | Slow, stable |
| Elephant | Episodic+Semantic+Procedural+Working | Dynamic selective (medium) | Very deep | Balanced | Medium causal+tool | Deep social (ToM 3) | Slow, stable |

**Freeze Verification Protocol**:
1. All predictions recorded before examining held-out data
2. Predictions are based solely on GMI morphology phase law
3. No post-hoc adjustments allowed
4. Held-out data analysis follows after prediction recording

### L2.11 Ecology-vs-Complexity Test

**Test Design**: Does ecology (E, R, V) predict cognitive differences better than brain/body size?

**Hypothesis**: GMI predicts that ecology (task distribution, recurrence, horizon) is the primary determinant of cognitive architecture, not brain size or body size.

**Test Protocol**:
1. **Control Variables**: Brain size, body size, metabolic rate
2. **Predictor Variables**: Task recurrence (R), task horizon (V), environment complexity (E)
3. **Outcome Variables**: Memory type dominance, planning depth, social cognition depth
4. **Statistical Test**: Multiple regression with ecology and brain/body size as predictors
5. **Prediction**: Ecology explains more variance than brain/body size

**Species Comparison**:
- **Human vs Elephant**: Similar brain size, different ecology → different cognitive architecture
- **Corvid vs Rodent**: Different brain size, similar ecology → similar cognitive architecture
- **Dolphin vs Cephalopod**: Different brain size, different ecology → different cognitive architecture

**Expected Result**: Ecology predicts cognitive differences better than brain/body size, supporting GMI morphology phase law.

---

## L3. Human Cognitive Architecture (11 Items)

### L3.1 Differentiated Memory Systems

**Prediction**: Human cognitive architecture includes four distinct memory systems: working memory, episodic memory, semantic memory, and procedural memory.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Working memory: Required for transient cue retention across short delays (GG54)
- Episodic memory: Required for autobiographical events with what-where-when binding (GG57)
- Semantic memory: Required for category-level generalization across episodes (GG59)
- Procedural memory: Required for compiled skill execution (PVR-3 threshold)

**Theorem Citation**: CSR-1 consolidation theorem requires distinct memory systems to preserve joint retention while reducing active-state load.

**Prediction**: Human cognitive architecture must include all four memory types to satisfy human ecology obligations. Removing any system creates a specific deficit profile (see L5).

### L3.2 Working-Memory Bottlenecks

**Prediction**: Human working memory capacity is limited to approximately 4 items (Cowan's 4±1).

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Working memory state cardinality |S_working| bounded by maintenance transformation cost
- Routing cost c_r limits simultaneous item maintenance
- Interference susceptibility increases with load

**Theorem Citation**: GG54 temporal cut theory bounds working memory by the semantic cut width achievable within maintenance cost constraints.

**Prediction**: Human working memory capacity emerges from the cost ratio between maintenance and interference, not from arbitrary architectural limits. The 4±1 limit is predicted by GMI given human ecology parameters.

### L3.3 Selective Attention

**Prediction**: Human selective attention uses dynamic routing, not fixed attention.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Observation bandwidth B_observe < task complexity K_task
- Routing cost c_r < exposure cost c_e(|U|-E|E_x|)
- Context-dependent routing gains exceed routing cost

**Theorem Citation**: GG55 conditional routing theorem predicts dynamic attention when B_observe < K_task and c_r + lambda p_r < c_e(|U|-E|E_x|).

**Prediction**: Human attention must use dynamic routing because human ecology exceeds observation bandwidth. Fixed attention would fail to satisfy human obligations.

### L3.4 Consolidation/Replay

**Prediction**: Human memory consolidation uses offline replay to restructure episodic traces into semantic/procedural form.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Episodic traces accumulate faster than active-state budget allows
- Consolidation saves t - ceil(log2 N_t) active states
- Replay channel restructures traces without losing joint retention

**Theorem Citation**: CSR-1 consolidation theorem requires offline restructuring when distinctions outgrow capacity.

**Prediction**: Human consolidation is required because episodic traces accumulate faster than working memory can hold them. Consolidation preserves joint retention while reducing active-state load.

### L3.5 Hierarchical Skills

**Prediction**: Human skill formation uses hierarchical chunking with self-limiting levels.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Recurring subsequences cross PVR-3 threshold
- First-level chunking justified by reuse count
- Second-level chunking self-limits because C lowers as hierarchy deepens

**Theorem Citation**: GMI hierarchical chunking theorem predicts self-limiting hierarchy depth when C decreases with each level.

**Prediction**: Human skill hierarchy depth is determined by the PVR-3 threshold at each level. Hierarchy self-limits because retaining a level raises the next bar (GG59).

### L3.6 Causal Intervention Learning

**Prediction**: Human causal cognition operates at rung-2 (interventional) and rung-3 (counterfactual) levels.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Action cost C_action is high; trial-and-error too expensive
- Environment structure K_struct is high; causal reasoning justified
- Intervention set is rich; do-calculus applicable

**Theorem Citation**: CAU-1..5 theorems predict causal cognition depth from action cost and environment structure.

**Prediction**: Human causal cognition must operate at rung-2 and rung-3 because human action cost and environment structure justify interventional and counterfactual reasoning. Rung-1 (associational) is insufficient for human ecology.

### L3.7 Metacognition

**Prediction**: Human metacognition uses confidence as surviving-candidate margin.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Candidate set S has non-singleton adequate-action sets
- Confidence = |adequate|/|S| gates action vs continued probing
- EVC > 0 justifies continued information seeking

**Theorem Citation**: META-1..4 theorems predict confidence as surviving-candidate margin.

**Prediction**: Human metacognition must use confidence-as-surviving-candidate because human ecology requires action gating under uncertainty. Alternative metacognitive strategies would fail to satisfy human obligations.

### L3.8 Theory of Mind

**Prediction**: Human theory of mind operates at recursion depth 3+.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Social topology N_agent is large; individual modeling required
- Information asymmetry A_info is high; belief tracking necessary
- Deception detection requires depth-3 reasoning

**Theorem Citation**: TOM-1..3 theorems predict ToM depth from social topology and information asymmetry.

**Prediction**: Human ToM depth is 3+ because human social topology and information asymmetry require multi-level belief tracking. Shallower ToM would fail to satisfy human social obligations.

### L3.9 Teaching/Imitation

**Prediction**: Human teaching/imitation operates at PVR-3 sender cost vs receiver benefit threshold.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Teaching cost S is high; must be amortized across learners
- Learning benefit C is high; justifies teaching investment
- Break-even n > 1 + S/(C-U) determines teaching viability

**Theorem Citation**: GMI teaching/culture break-even theorem predicts teaching viability from cost/benefit ratio.

**Prediction**: Human teaching/imitation is viable because the cost/benefit ratio allows amortization across learners. Teaching that violates n > 1 + S/(C-U) is not sustainable.

### L3.10 Cumulative Culture

**Prediction**: Human cumulative culture operates through individual → social → persistent chain.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Individual learning acquires new capabilities
- Social learning transmits capabilities across individuals
- Cultural store persists across generations
- Ratchet complexity increases frontier beyond individual reach

**Theorem Citation**: GG59 population-level developmental process predicts cultural accumulation when transmission fidelity exceeds threshold.

**Prediction**: Human cumulative culture is possible because individual learning + social transmission + cultural persistence creates a ratchet that exceeds any single lifetime's reachable set.

### L3.11 No Neuroanatomy

**Constraint**: All predictions in L3 are at the capability level, not at the neural implementation level.

**Rationale**: GMI predicts cognitive architecture from ecology and resources, not from neural substrates. Neural implementation is substrate-specific and does not validate or invalidate GMI predictions.

**Explicit Constraint**: No prediction in L3 references specific brain regions, neural circuits, or neurotransmitter systems. All predictions are at the functional capability level.

---

## L4. Developmental Psychology (6 Items)

### L4.1 Capability Emergence Ordering

**Prediction**: Human capabilities emerge in a specific order determined by the developmental taxonomy.

**GMI Derivation**: Under human development law D(t):
- Perception emerges first (sensory systems mature early)
- Working memory emerges second (requires sensorimotor coordination)
- Episodic memory emerges third (requires temporal binding)
- Semantic memory emerges fourth (requires abstraction over episodes)
- Procedural memory emerges fifth (requires skill compilation)
- Planning emerges sixth (requires world model)
- Social cognition emerges seventh (requires ToM depth)
- Metacognition emerges eighth (requires confidence computation)
- Cultural accumulation emerges ninth (requires social transmission)

**Theorem Citation**: GMI developmental taxonomy predicts capability emergence order from resource accumulation and protected splits.

**Prediction**: Human capability emergence order is predicted by GMI developmental taxonomy. Capabilities that require prior structure emerge after their prerequisites.

### L4.2 Dependencies

**Prediction**: Some capabilities require prior structure to emerge.

**GMI Derivation**: Under human development law D(t):
- Episodic memory requires working memory for temporal binding
- Semantic memory requires episodic memory for abstraction
- Planning requires world model (semantic memory)
- Social cognition requires working memory + episodic memory
- Metacognition requires confidence computation (requires multiple memory systems)
- Cultural accumulation requires social transmission + persistence

**Theorem Citation**: GMI capability interaction matrix predicts dependencies from resource requirements.

**Prediction**: Human capabilities have dependency relationships that determine emergence order. Capabilities that require prior structure cannot emerge until prerequisites are in place.

### L4.3 Sensitive Periods

**Prediction**: Human sensitive periods emerge from resource/ecology assumptions.

**GMI Derivation**: Under human development law D(t):
- Sensitive period for language: when observation bandwidth is high and social input is rich
- Sensitive period for attachment: when social topology is small and information sharing is high
- Sensitive period for motor skills: when action cost is learnable and environment is stable

**Theorem Citation**: GMI developmental sensitivity theorem predicts sensitive periods from resource availability and ecology.

**Prediction**: Human sensitive periods are predicted by GMI when resource availability and ecology align to make learning efficient. Sensitive periods close when resource availability decreases or ecology changes.

### L4.4 Compositional Abstraction

**Prediction**: Human concept formation triggers when PVR-3 threshold is crossed.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Instance stream contains recurring patterns
- PVR-3 threshold determines when naming cost is amortized by reuse
- Bang-bang optimum places boundaries at precise locations

**Theorem Citation**: GMI concept formation trigger theorem predicts concept emergence from reuse count and naming cost.

**Prediction**: Human concept formation occurs exactly when PVR-3 threshold is crossed. Concepts that do not meet threshold are not formed; concepts that exceed threshold are formed at bang-bang optimum.

### L4.5 Social Inference Depth

**Prediction**: Human ToM depth increases during development as social complexity increases.

**GMI Derivation**: Under human development law D(t):
- Early development: small social group, low information asymmetry → ToM depth 0-1
- Middle development: larger social group, medium information asymmetry → ToM depth 2
- Late development: complex social group, high information asymmetry → ToM depth 3+

**Theorem Citation**: TOM-1..3 theorems predict ToM depth from social topology and information asymmetry, which increase during development.

**Prediction**: Human ToM depth increases during development as social complexity increases. ToM depth is not fixed at birth but emerges from social interaction.

### L4.6 Comparison Protocol

**Held-Out Developmental Datasets**: (recorded before analysis)

| Dataset | Prediction | GMI Rationale |
|---------|-----------|---------------|
| **Piaget stages** | Sensorimotor → Preoperational → Concrete → Formal | Matches GMI capability emergence ordering |
| **Theory of mind development** | False belief understanding at age 4 | Matches GMI ToM depth increase |
| **Language acquisition** | Babbling → Words → Grammar → Pragmatics | Matches GMI concept formation trigger |
| **Memory development** | Working → Episodic → Semantic → Procedural | Matches GMI memory emergence ordering |

**Comparison Protocol**:
1. All predictions recorded before examining held-out data
2. Predictions are based solely on GMI morphology phase law
3. No post-hoc adjustments allowed
4. Held-out data analysis follows after prediction recording

---

## L5. Lesion/Ablation Predictions (7 Items)

### L5.1 Memory Component Removal → Deficit Profile

**Prediction**: Removing each memory component creates a specific deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Working memory removal: Cannot retain transient cues; immediate response only
- Episodic memory removal: Cannot recall specific events; only category-level knowledge retained
- Semantic memory removal: Cannot generalize across episodes; only specific instances retained
- Procedural memory removal: Cannot execute compiled skills; must reason from scratch each time

**Theorem Citation**: GMI memory system architecture predicts deficit profiles from memory function removal.

**Prediction**: Removing any memory system creates a specific deficit profile that violates human ecology obligations. The deficit profile is predicted by GMI from the memory system's function.

### L5.2 Attention/Routing Removal → Deficit Profile

**Prediction**: Removing selective attention creates fixed-attention deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Fixed attention cannot route to context-relevant sources
- Cannot satisfy obligations that require context-dependent accuracy
- Fails when B_observe < K_task and routing gain > c_r

**Theorem Citation**: GG55 conditional routing theorem predicts deficit when routing is removed.

**Prediction**: Removing selective attention creates fixed-attention deficit profile where context-dependent accuracy drops to best fixed-source level. This violates human ecology obligations.

### L5.3 Planning/Model Removal → Deficit Profile

**Prediction**: Removing planning creates myopic-control deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Myopic control cannot satisfy long-range dependencies
- Cannot achieve goals that require multi-step planning
- Fails when task horizon > 1

**Theorem Citation**: Planning semantic resolution theorem predicts deficit when planning is removed.

**Prediction**: Removing planning creates myopic-control deficit profile where long-range goal attainment drops to chance level. This violates human ecology obligations.

### L5.4 Causal-Intervention Removal → Deficit Profile

**Prediction**: Removing causal-intervention learning creates associative-only deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Associational learning cannot distinguish P(Y|X) from P(Y|do(X))
- Cannot predict intervention outcomes
- Fails when action cost C_action is high and environment structure K_struct is high

**Theorem Citation**: CAU-1..5 theorems predict deficit when causal reasoning is removed.

**Prediction**: Removing causal-intervention learning creates associative-only deficit profile where interventional and counterfactual reasoning drop to chance level. This violates human ecology obligations.

### L5.5 Social-Model Removal → Deficit Profile

**Prediction**: Removing social-model creates no-social-cognition deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- No social cognition cannot predict other agents' behavior
- Cannot cooperate or compete effectively
- Fails when social topology N_agent > 1 and information asymmetry A_info > 0

**Theorem Citation**: TOM-1..3 theorems predict deficit when social modeling is removed.

**Prediction**: Removing social-model creates no-social-cognition deficit profile where social interaction drops to fixed-policy level. This violates human ecology obligations.

### L5.6 Consolidation/Replay Removal → Retention/Generalization Effects

**Prediction**: Removing consolidation creates retention/generalization deficit profile.

**GMI Derivation**: Under human ecology (E_human, R_human, V_human):
- Episodic traces accumulate faster than working memory can hold
- Without consolidation, traces are lost or remain in active state
- Cannot generalize across episodes; only specific instances retained
- Active-state budget exceeded; interference increases

**Theorem Citation**: CSR-1 consolidation theorem predicts retention/generalization deficit when consolidation is removed.

**Prediction**: Removing consolidation creates retention/generalization deficit profile where episodic traces are lost or remain in active state, increasing interference and reducing generalization. This violates human ecology obligations.

### L5.7 Comparison Protocol

**Neuropsychological Evidence Protocol**:

| Lesion Type | Predicted Deficit | GMI Prediction | Held-Out Evidence |
|-------------|-------------------|----------------|-------------------|
| **Working memory lesion** | Immediate response only | Cannot retain transient cues | Patient K.F. (Shallice & Warrington) |
| **Episodic memory lesion** | No specific event recall | Only category-level knowledge | Patient H.M. (Milner) |
| **Semantic memory lesion** | No generalization | Only specific instances retained | Patient D.F. (Goodale & Milner) |
| **Procedural memory lesion** | No compiled skills | Must reason from scratch | Parkinson's patients |
| **Attention lesion** | Fixed attention | Cannot route context-dependently | Neglect syndrome patients |
| **Planning lesion** | Myopic control | Cannot achieve long-range goals | Frontal lobe lesion patients |
| **Causal lesion** | Associational only | Cannot predict interventions | Causal reasoning deficits |
| **Social lesion** | No social cognition | Cannot predict others' behavior | Autism spectrum disorder |
| **Consolidation lesion** | Retention/generalization deficit | Traces lost or remain active | Amnesia patients |

**Protocol**:
1. All predictions recorded before examining held-out evidence
2. Predictions are based solely on GMI morphology phase law
3. No post-hoc adjustments allowed
4. Held-out evidence analysis follows after prediction recording
5. No anatomical identity claims - only functional deficit profiles

---

## Summary

This document provides GMI-native stress test protocols for natural intelligence across species. All predictions are derived from the morphology phase law (E+R+V → M*) and are held-out testable. The document covers:

- **L1**: Animal cognitive phenotype model (12 items) - GMI coordinates and predictions
- **L2**: Cross-species tests (10 items) - Specific predictions for 9 species + freeze protocol
- **L3**: Human cognitive architecture (11 items) - GMI-derived predictions for human cognition
- **L4**: Developmental psychology (6 items) - Capability emergence and dependencies
- **L5**: Lesion/ablation predictions (7 items) - Deficit profiles from component removal

All 47 items are complete and ready for held-out testing.

---

**Document Version**: V1
**Date**: 2026-09-15
**Status**: Complete
**Issue**: #602 L1-L5
