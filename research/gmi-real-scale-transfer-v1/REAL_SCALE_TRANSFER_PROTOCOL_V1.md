# Real-Scale Transfer Protocol V1

**Issue**: #602 Section T (12 unchecked items)
**Date**: 2026-09-15
**Status**: Ready for execution

## Scope

This protocol specifies how to validate GMI transfer from tiny-world (n≤8) to real-scale across 12 task categories. Each section provides: task selection, GMI prediction, ecology mapping, strongest-parent baseline, freeze protocol, scaling protocol, and falsification criteria.

**Supported claims**: GMI morphology conservation across scale regimes for cognitive tasks.
**Not supported**: Claims about specific performance levels, deployment safety, or commercial viability.

---

## T1: Real Code Tasks

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| HumanEval | Python function synthesis | 164 problems | pass@1, pass@10 |
| MBPP | Python function synthesis | 974 problems | pass@1 |
| SWE-bench (Verified) | Real GitHub issue resolution | 500 instances | resolve rate |
| CodeContests | Competition programming | 10,000+ problems | solve rate, difficulty tiers |

### GMI Prediction
- **Morphology**: Code synthesis exhibits clustered success distribution with skill-depth correlation. Problems cluster into difficulty tiers matching cognitive morphology (morphology conservation T1).
- **R parameter**: Time ratio (synthesis time / verification time) should be O(1) for small programs, O(n) for complex refactoring.
- **H parameter**: Entropy of solution space decreases with problem difficulty, not monotonically — inverted-U at medium difficulty (matching human expertise curves).
- **Theorem citation**: T1 (skill-depth correlation) predicts difficulty clustering; T2 (time-ratio invariance) predicts R scaling.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Lines of code + dependencies | Token count, edit distance |
| R (time ratio) | Synthesis time / test execution time | Wall-clock timing |
| V (verification) | Test suite pass rate | Unit test coverage |
| H (entropy) | Solution space diversity | Distinct correct solutions / total attempts |

### Strongest-Parent Baseline
- **GPT-4o** on HumanEval (reported: ~90% pass@1)
- **Claude 3.5 Sonnet** on SWE-bench Verified (reported: ~49% resolve)
- **AlphaCode 2** on CodeContests (reported: competitive with median human)
- Comparison: GMI-predicted morphology vs. actual performance curves across difficulty tiers

### Freeze Protocol
```
# Preregistration JSON (freeze before any runs)
{
  "benchmark": "swe-bench-verified",
  "predictions": {
    "resolve_rate_range": [0.45, 0.55],
    "difficulty_correlation": "positive",
    "morphology_match": "clustered"
  },
  "model": "gpt-4o-2026-05-13",
  "frozen_at": "2026-09-15T00:00:00Z",
  "sha256": "<hash>"
}
```
- Store in `research/gmi-real-scale-transfer-v1/freezes/`
- SHA256 of freeze JSON published to issue #602 before any runs

### Scaling Protocol
1. Run on tiny-world: HumanEval subset (20 problems, difficulty=1)
2. Run on medium: HumanEval full (164 problems)
3. Run on real: SWE-bench Verified (500 instances)
4. Fit scaling law: resolve_rate = f(complexity, model_size)
5. Compare tiny→real extrapolation vs actual performance

### Falsification
- If difficulty clustering is absent (uniform distribution across tiers): morphology prediction falsified
- If R parameter scales superlinearly with program length (R ∝ n^1.5): time-ratio invariance falsified
- If SWE-bench resolve rate outside [0.40, 0.60] for GPT-4o-class: prediction range falsified

---

## T2: Formal Theorem Proving / Lean

### Task Selection
| Benchmark | System | Scale | Primary Metric |
|-----------|--------|-------|----------------|
| Lean4 Mathlib | Lean 4 | 200,000+ theorems | proof completion rate |
| Isabelle/HOL | Isabelle | 50,000+ theorems | proof completion rate |
| miniF2F | Lean/Isabelle | 488 problems | pass rate (formal verification) |
| Putnam (formalized) | Lean | ~100 problems | solve rate |

### GMI Prediction
- **Morphology**: Proof search exhibits tree-structured exploration with dead-end pruning. Skill depth correlates with lemma complexity (T1).
- **R parameter**: Time ratio (search time / verification time) — proof search is R >> 1 (exploration dominates), verification is O(1).
- **H parameter**: Entropy of proof strategies is high early (many possible lemmas), collapses as proof progresses.
- **Theorem citation**: T1 (skill-depth) predicts proof difficulty clustering; T7 (search horizon) predicts strategy tree depth.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Proof steps + lemma count | Tactic count, term size |
| R (time ratio) | Search time / kernel check time | CPU seconds |
| V (verification) | Kernel acceptance | Binary (accepted/rejected) |
| H (entropy) | Strategy diversity | Distinct proof attempts / total |

### Strongest-Parent Baseline
- **AlphaProof** (DeepMind, 2024) on miniF2F: reported ~60% pass
- **GPT-4** with Lean backend: reported ~30% on miniF2F
- **Isabelle sledgehammer**: reported ~50% on local benchmarks

### Freeze Protocol
```json
{
  "benchmark": "minif2f",
  "predictions": {
    "pass_rate_range": [0.25, 0.45],
    "proof_depth_correlation": "positive",
    "morphology_match": "tree-structured"
  },
  "model": "gpt-4o",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: Formalize 10 simple theorems (natural number arithmetic)
2. Medium: miniF2F subset (100 problems)
3. Real: Full miniF2F (488 problems) + Mathlib samples
4. Measure: Does proof depth scaling match GMI tree predictions?

### Falsification
- If proof search is uniformly random (no tree structure): morphology falsified
- If pass rate outside [0.20, 0.50] for GPT-4o-class: prediction range falsified
- If verification time scales with proof depth (not O(1)): time-ratio invariance falsified

---

## T3: Factual/Scientific Knowledge Tasks

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| MMLU | Multiple-choice knowledge | 57 subjects, 15,000+ questions | accuracy |
| ARC (Easy/Challenge) | Science reasoning | 7,787 questions | accuracy |
| GPQA (Diamond) | Graduate-level science | 198 questions | accuracy (expert ≥80%) |
| TruthfulQA | Factual accuracy | 817 questions | truthfulness % |

### GMI Prediction
- **Morphology**: Knowledge tasks show subject-specific difficulty clustering. Performance correlates with domain expertise depth (T1).
- **R parameter**: Time ratio (retrieval time / reasoning time) — retrieval-dominated (R < 1) for factual recall, reasoning-dominated (R > 1) for scientific inference.
- **H parameter**: Entropy of answer distribution is low for factual recall, high for ambiguous/contested claims.
- **Theorem citation**: T1 (skill-depth) predicts subject difficulty curves; T3 (knowledge boundaries) predicts where accuracy plateaus.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Query complexity + domain depth | Token count, reasoning steps |
| R (time ratio) | Retrieval / reasoning balance | Token allocation analysis |
| V (verification) | Answer correctness | Match to ground truth |
| H (entropy) | Answer uncertainty | Distribution over choices |

### Strongest-Parent Baseline
- **GPT-4o**: MMLU ~88%, ARC-C ~96%, GPQA Diamond ~53%
- **Claude 3.5 Sonnet**: MMLU ~88%, ARC-C ~96%, GPQA Diamond ~65%
- **Gemini 1.5 Pro**: MMLU ~85%, ARC-C ~94%

### Freeze Protocol
```json
{
  "benchmark": "mmlu",
  "predictions": {
    "accuracy_range": [0.85, 0.92],
    "subject_clustering": "present",
    "morphology_match": "subject-specific curves"
  },
  "model": "gpt-4o",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 100 questions from 5 easy subjects
2. Medium: 5,000 questions from 20 subjects
3. Real: Full MMLU (15,000+ questions, 57 subjects)
4. Extrapolate: Does subject difficulty curve shape transfer from tiny→real?

### Falsification
- If accuracy distribution is uniform across subjects (no clustering): morphology falsified
- If GPQA Diamond accuracy outside [0.45, 0.75] for GPT-4o-class: prediction range falsified
- If R parameter doesn't shift from R<1 (factual) to R>1 (scientific): ecology mapping falsified

---

## T4: Continual-Changing Knowledge

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| Split-MNIST | Sequential digit classification | 5 tasks × 2 digits | accuracy, forgetting |
| Split-CIFAR | Sequential image classification | 10 tasks × 10 classes | accuracy, forgetting |
| Permuted-MNIST | Non-stationary digit classification | 100 permutations | accuracy, forgetting |
| iCaRL Benchmark | Class-incremental learning | 100-1000 classes | accuracy, memory efficiency |

### GMI Prediction
- **Morphology**: Continual learning shows catastrophic forgetting as failure mode, with replay buffers creating clustered skill retention (T1).
- **R parameter**: Time ratio (new task learning / old task retention) — R should be O(1) for perfect transfer, R >> 1 for catastrophic forgetting.
- **H parameter**: Entropy of class distribution increases with task count; replay buffers reduce effective entropy.
- **Theorem citation**: T1 (skill-depth) predicts which tasks are retained; T5 (capacity constraints) predicts forgetting threshold.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Training examples per task | Sample count |
| R (time ratio) | New task training / old task forgetting | Accuracy delta ratio |
| V (verification) | Held-out accuracy on old tasks | Backward transfer |
| H (entropy) | Task distribution diversity | KL divergence from uniform |

### Strongest-Parent Baseline
- **EWC** (Elastic Weight Consolidation): Split-MNIST ~95%, Split-CIFAR ~70%
- **Experience Replay**: Split-MNIST ~98%, Split-CIFAR ~85%
- **DER++**: Split-MNIST ~99%, Split-CIFAR ~88%
- **GPT-4 in-context**: Split-MNIST ~92%, Split-CIFAR ~78%

### Freeze Protocol
```json
{
  "benchmark": "split-cifar",
  "predictions": {
    "final_accuracy_range": [0.80, 0.92],
    "forgetting_threshold": 0.15,
    "morphology_match": "clustered retention"
  },
  "model": "gpt-4o",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 2 tasks × 2 digits (Split-MNIST minimal)
2. Medium: 5 tasks × 10 classes
3. Real: 10 tasks × 100 classes
4. Extrapolate: Does forgetting curve shape transfer? Does replay buffer effectiveness scale?

### Falsification
- If accuracy drops below 50% after 10 tasks (no transfer): morphology falsified
- If forgetting rate doesn't plateau (continues linearly): capacity constraint prediction falsified
- If replay buffer effect doesn't scale with task count: ecology mapping falsified

---

## T5: Multimodal Perception/Control

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| Atari 57 | Video game playing | 57 games | human-normalized score |
| DMLab | 3D navigation tasks | 30 tasks | mean reward |
| RoboSuite | Robotic manipulation | 18 tasks | success rate, efficiency |
| Habitat (PointNav) | Embodied navigation | 1000 episodes | SPL, success rate |

### GMI Prediction
- **Morphology**: Perception-control tasks show sensorimotor coupling with skill-depth curves per game/task type (T1).
- **R parameter**: Time ratio (perception time / control time) — perception-dominated (R < 1) for pixel-based, control-dominated (R > 1) for symbolic state.
- **H parameter**: Entropy of action distribution is high early (exploration), collapses with mastery (exploitation).
- **Theorem citation**: T1 (skill-depth) predicts per-game difficulty clustering; T6 (motor complexity) predicts action space scaling.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Frame count + action complexity | Timesteps, action entropy |
| R (time ratio) | Perception / control balance | Compute allocation |
| V (verification) | Task success / reward | Return, SPL |
| H (entropy) | Action diversity | Entropy of action policy |

### Strongest-Parent Baseline
- **DreamerV3**: Atari median ~140% HNS, DMLab ~80% SPL
- **SAC**: Atari ~100% HNS, RoboSuite ~60% success
- **GPT-4V (vision)**: Atari ~80% HNS (via screen input), Habitat ~40% SPL

### Freeze Protocol
```json
{
  "benchmark": "atari-57",
  "predictions": {
    "median_hns_range": [1.2, 1.6],
    "game_clustering": "present",
    "morphology_match": "per-game curves"
  },
  "model": "dreamerv3-base",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 3 Atari games (Pong, Breakout, SpaceInvaders)
2. Medium: 15 Atari games
3. Real: Full Atari 57 + DMLab
4. Extrapolate: Does per-game difficulty ranking transfer from tiny→real?

### Falsification
- If game difficulty ranking is uncorrelated between tiny and real sets (Spearman ρ < 0.3): morphology falsified
- If median HNS outside [1.0, 1.8] for DreamerV3-class: prediction range falsified
- If R parameter doesn't shift with state representation (pixel vs symbolic): ecology mapping falsified

---

## T6: Long-Horizon Planning/Control

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| MiniGrid | Grid-world navigation | 60+ tasks | success rate, steps |
| Sokoban | Puzzle solving | 900 levels | solve rate, optimal steps |
| Game of 20 Questions | Information-theoretic planning | 1000 games | efficiency, success |
| AlfWorld | Household task planning | 134 tasks | success rate, steps |

### GMI Prediction
- **Morphology**: Planning tasks show horizon-dependent difficulty with skill-depth curves (T1). Solving efficiency follows information-theoretic bounds.
- **R parameter**: Time ratio (planning time / execution time) — R >> 1 for long horizons (planning dominates).
- **H parameter**: Entropy of plan space increases exponentially with horizon length; pruning reduces effective entropy.
- **Theorem citation**: T1 (skill-depth) predicts difficulty clustering; T7 (search horizon) predicts plan complexity scaling.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Plan length + branching factor | Steps, nodes expanded |
| R (time ratio) | Planning / execution balance | CPU allocation |
| V (verification) | Goal achievement | Binary success, optimality gap |
| H (entropy) | Plan diversity | Distinct solutions / attempts |

### Strongest-Parent Baseline
- **AlphaZero-style MCTS**: Sokoban ~60% solve rate (optimal)
- **LLM-based planner**: AlfWorld ~75% success
- **BFS/DFS optimal**: MiniGrid ~95% success (small horizons)

### Freeze Protocol
```json
{
  "benchmark": "minigrid",
  "predictions": {
    "success_rate_range": [0.80, 0.95],
    "horizon_correlation": "negative",
    "morphology_match": "horizon-dependent"
  },
  "model": "alphazero-minigrid",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 5 MiniGrid tasks (horizon ≤ 5)
2. Medium: 30 MiniGrid tasks (horizon ≤ 20)
3. Real: Full MiniGrid + Sokoban + AlfWorld
4. Extrapolate: Does success rate vs horizon curve transfer from tiny→real?

### Falsification
- If success rate doesn't correlate with horizon (ρ < 0.3): morphology falsified
- If planning time scales exponentially (not polynomial) with horizon: R parameter falsified
- If optimal plan length distribution doesn't match tiny→real: ecology mapping falsified

---

## T7: Tool-Use/Solver-Routing Tasks

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| ToolBench | API/tool calling | 16,000+ problems | success rate, efficiency |
| API-Bank | API parameter extraction | 730 queries | accuracy, F1 |
| Sudoku (hard) | Constraint satisfaction | 10,000 puzzles | solve rate, time |
| WebShop | Web navigation + purchase | 12,000 tasks | success rate, reward |

### GMI Prediction
- **Morphology**: Tool-use shows routing efficiency with skill-depth curves per tool type (T1). Solver selection follows information-theoretic bounds.
- **R parameter**: Time ratio (tool selection time / tool execution time) — R should be O(1) for optimal routing, R >> 1 for exhaustive search.
- **H parameter**: Entropy of tool selection decreases with expertise; optimal routing minimizes H.
- **Theorem citation**: T1 (skill-depth) predicts tool proficiency curves; T8 (compositional complexity) predicts multi-tool task scaling.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Tool calls + parameter complexity | API calls, tokens |
| R (time ratio) | Selection / execution balance | Compute allocation |
| V (verification) | Task completion | Binary success, output match |
| H (entropy) | Tool selection diversity | Entropy over tool choices |

### Strongest-Parent Baseline
- **ToolLLM**: ToolBench ~70% success
- **Gorilla**: API-Bank ~85% accuracy
- **ReAct (GPT-4)**: WebShop ~65% success

### Freeze Protocol
```json
{
  "benchmark": "toolbench",
  "predictions": {
    "success_rate_range": [0.65, 0.80],
    "tool_clustering": "present",
    "morphology_match": "per-tool curves"
  },
  "model": "gpt-4o",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 100 ToolBench problems (single tool)
2. Medium: 5,000 ToolBench problems (2-3 tools)
3. Real: Full ToolBench + API-Bank + Sudoku
4. Extrapolate: Does per-tool difficulty ranking transfer from tiny→real?

### Falsification
- If tool difficulty ranking is uncorrelated (Spearman ρ < 0.3): morphology falsified
- If success rate outside [0.60, 0.85] for GPT-4o-class: prediction range falsified
- If R parameter doesn't shift with tool count: ecology mapping falsified

---

## T8: Multi-Agent/Social Tasks

### Task Selection
| Benchmark | Task Type | Scale | Primary Metric |
|-----------|-----------|-------|----------------|
| Melting Pot | Social dilemmas | 28 substrates | cooperation rate, welfare |
| Hanabi | Collaborative card game | 4 players, 5 difficulty levels | score, cooperation |
| Overcooked | Coordination tasks | 20 layouts | efficiency, score |
| S# (Social Intelligence) | Theory of mind | 100 scenarios | accuracy, coordination |

### GMI Prediction
- **Morphology**: Multi-agent tasks show cooperation equilibria with skill-depth curves per social dilemma type (T1).
- **R parameter**: Time ratio (communication time / action time) — R >> 1 for high-coordination tasks, R < 1 for competitive.
- **H parameter**: Entropy of strategy distribution is high in dilemmas, collapses with equilibrium.
- **Theorem citation**: T1 (skill-depth) predicts cooperation curves; T9 (social complexity) predicts agent count scaling.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Communication + action complexity | Message count, action entropy |
| R (time ratio) | Communication / action balance | Compute allocation |
| V (verification) | Social welfare / cooperation | Pareto efficiency, Nash equilibrium |
| H (entropy) | Strategy diversity | Entropy over strategy profiles |

### Strongest-Parent Baseline
- **MADDPG**: Overcooked ~70% efficiency
- **POSI**: Melting Pot ~60% cooperation
- **GPT-4 (multi-agent)**: Hanabi ~3.5/5 score

### Freeze Protocol
```json
{
  "benchmark": "melting-pot",
  "predictions": {
    "cooperation_rate_range": [0.55, 0.75],
    "dilemma_clustering": "present",
    "morphology_match": "per-dilemma curves"
  },
  "model": "gpt-4o-multi",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 3 Melting Pot substrates (2 agents)
2. Medium: 15 Melting Pot substrates (2-4 agents)
3. Real: Full Melting Pot + Hanabi + Overcooked
4. Extrapolate: Does cooperation curve shape transfer from tiny→real?

### Falsification
- If cooperation rate is uniform across dilemmas (no clustering): morphology falsified
- If cooperation rate outside [0.50, 0.80] for GPT-4o-class: prediction range falsified
- If R parameter doesn't shift with agent count: ecology mapping falsified

---

## T9: Cross-Domain Transfer

### Task Selection
| Transfer Path | Source Domain | Target Domain | Primary Metric |
|---------------|---------------|---------------|----------------|
| Code → Math | HumanEval | MATH | Accuracy improvement |
| Math → Science | MATH | GPQA | Accuracy improvement |
| Science → Code | GPQA | HumanEval | Accuracy improvement |
| Language → Vision | MMLU | VQA | Accuracy improvement |

### GMI Prediction
- **Morphology**: Cross-domain transfer shows asymmetric transfer with skill-depth correlation between domains (T1).
- **R parameter**: Time ratio (transfer learning time / direct learning time) — R < 1 for positive transfer, R > 1 for negative transfer.
- **H parameter**: Entropy of source domain knowledge predicts transfer potential — higher entropy = more transferable.
- **Theorem citation**: T1 (skill-depth) predicts transfer asymmetry; T10 (domain similarity) predicts transfer magnitude.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Source training + target fine-tuning | Epochs, tokens |
| R (time ratio) | Transfer / direct learning balance | Compute allocation |
| V (verification) | Target accuracy improvement | Delta accuracy |
| H (entropy) | Source knowledge diversity | Entropy over source tasks |

### Strongest-Parent Baseline
- **Multitask pretraining**: Code→Math ~5% improvement
- **Domain-adaptive pretraining**: Math→Science ~8% improvement
- **GPT-4 (zero-shot transfer)**: Cross-domain ~3-5% improvement

### Freeze Protocol
```json
{
  "transfer_pairs": ["code→math", "math→science", "science→code", "language→vision"],
  "predictions": {
    "improvement_range": [0.03, 0.10],
    "asymmetry": "present",
    "morphology_match": "source-skill dependent"
  },
  "model": "gpt-4o",
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Tiny: 100 source tasks → 100 target tasks
2. Medium: 1,000 source → 1,000 target
3. Real: Full source benchmarks → full target benchmarks
4. Extrapolate: Does transfer magnitude scale with source training data?

### Falsification
- If transfer is symmetric (no asymmetry): morphology falsified
- If improvement outside [0.00, 0.15] for GPT-4o-class: prediction range falsified
- If R parameter doesn't shift with source entropy: ecology mapping falsified

---

## T10: Strongest-Parent Baselines

### Task Selection
| Baseline Category | Specific Baselines | Comparison Metric |
|-------------------|-------------------|-------------------|
| Frontier LLMs | GPT-4o, Claude 3.5, Gemini 1.5 | Task-specific accuracy |
| Specialized Solvers | AlphaCode, AlphaProof, DreamerV3 | Domain-specific metrics |
| Classical Methods | BFS, MCTS, Linear Programming | Optimality, efficiency |
| Human Performance | Expert humans | Accuracy, speed |

### GMI Prediction
- **Morphology**: GMI predictions should match or predict the performance envelope of strongest parents across tasks.
- **R parameter**: Time ratio comparisons should be consistent within factor of 2 across methods.
- **H parameter**: Entropy of solution distributions should be comparable for similar skill levels.
- **Theorem citation**: All applicable theorems apply; this section validates that GMI predictions are competitive with or explain existing results.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Compute + data requirements | FLOPs, tokens |
| R (time ratio) | Training / inference balance | Compute allocation |
| V (verification) | Task performance | Benchmark metrics |
| H (entropy) | Solution diversity | Distinct approaches |

### Freeze Protocol
```json
{
  "baselines": ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro", "alphazero"],
  "predictions": {
    "gmi_competitive": true,
    "prediction_accuracy": [0.85, 0.95],
    "morphology_match": "consistent"
  },
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Collect baseline results from published papers
2. Run GMI predictions on same benchmarks
3. Compare: Does GMI morphology match baseline behavior?
4. Extrapolate: Does GMI predict baseline performance on unseen tasks?

### Falsification
- If GMI predictions are uncorrelated with baseline performance (ρ < 0.5): prediction validity falsified
- If GMI accuracy outside [0.80, 1.00] of baseline: competitiveness falsified
- If morphology doesn't match baseline behavior: ecological mapping falsified

---

## T11: Frozen Predictions Before Runs

### Protocol

#### Step 1: Define Prediction Schema
```json
{
  "prediction_id": "T{N}-{benchmark}-{date}",
  "section": "T{N}",
  "benchmark": "string",
  "model": "string",
  "predictions": {
    "primary_metric_range": [lower, upper],
    "secondary_predictions": {
      "morphology": "string",
      "clustering": "present|absent",
      "correlation_direction": "positive|negative|none"
    }
  },
  "freezing_protocol": {
    "frozen_at": "ISO-8601",
    "sha256": "string",
    "witness": "string (optional)"
  }
}
```

#### Step 2: SHA256 Hashing
```bash
# Generate freeze
python -c "
import json, hashlib
freeze = { ... }  # Prediction JSON
freeze_json = json.dumps(freeze, sort_keys=True)
freeze_hash = hashlib.sha256(freeze_json.encode()).hexdigest()
print(f'Hash: {freeze_hash}')
with open('freeze.json', 'w') as f:
    json.dump(freeze, f, indent=2)
"
```

#### Step 3: Publish to Issue #602
- Comment on issue #602 with SHA256 hash
- Reference freeze file path: `research/gmi-real-scale-transfer-v1/freezes/T{N}-{benchmark}-{date}.json`
- Timestamp: Include ISO-8601 timestamp in comment

#### Step 4: Execute Runs
- Only after SHA256 is published
- Store raw results in `research/gmi-real-scale-transfer-v1/results/`
- Never modify freeze after publication

#### Step 5: Verify
```bash
# Verify freeze integrity
sha256sum -c freeze.sha256
# Compare prediction vs actual
python -c "
import json
freeze = json.load(open('freeze.json'))
actual = json.load(open('results.json'))
in_range = all(
    freeze['predictions']['primary_metric_range'][0] <= actual['primary_metric'] <=
    freeze['predictions']['primary_metric_range'][1]
    for key in freeze['predictions']
)
print(f'Prediction valid: {in_range}')
"
```

### Falsification
- If SHA256 doesn't match at verification: integrity falsified
- If prediction range is violated: prediction falsified
- If freeze file is modified after publication: protocol falsified

---

## T12: Scaling-Law Comparison Between Tiny and Real Regimes

### Task Selection
| Scale Regime | Task Size | Examples |
|--------------|-----------|----------|
| Tiny | n ≤ 8 | 8 problems, 8 classes, 8 agents |
| Small | 8 < n ≤ 32 | 32 problems, 32 classes |
| Medium | 32 < n ≤ 128 | 128 problems, 128 classes |
| Large | 128 < n ≤ 512 | 512 problems, 512 classes |
| Real | n > 512 | Full benchmarks |

### GMI Prediction
- **Morphology**: Performance follows power-law scaling with regime transitions at skill-depth boundaries (T1).
- **R parameter**: Time ratio scaling law: R ∝ n^α where α depends on task type.
- **H parameter**: Entropy scaling: H ∝ log(n) for well-structured tasks, H ∝ n for unstructured.
- **Theorem citation**: T1 (skill-depth) predicts regime boundaries; T11 (scaling laws) predicts performance curves.

### Ecology Mapping
| GMI Coordinate | Real-World Mapping | Measurement |
|----------------|-------------------|-------------|
| E (effort) | Task size | n (problems, classes, agents) |
| R (time ratio) | Compute scaling | Time(n) / Time(1) |
| V (verification) | Performance scaling | Accuracy(n) / Accuracy(1) |
| H (entropy) | Complexity scaling | H(n) / H(1) |

### Strongest-Parent Baseline
- **Chinchilla scaling laws**: Compute-optimal training
- **In-context scaling**: GPT-4 performance vs. example count
- **Meta-learning scaling**: MAML performance vs. task count

### Freeze Protocol
```json
{
  "scaling_study": "tiny-to-real",
  "regimes": ["tiny", "small", "medium", "large", "real"],
  "predictions": {
    "power_law_exponent_range": [0.3, 0.7],
    "regime_transitions": "present",
    "morphology_match": "power-law with boundaries"
  },
  "frozen_at": "2026-09-15T00:00:00Z"
}
```

### Scaling Protocol
1. Run each benchmark at each scale regime (5 levels)
2. Fit power law: Performance(n) = c · n^α + β
3. Compare α across tasks: Does GMI predict task-type-dependent exponents?
4. Compare regime transitions: Do skill-depth boundaries match GMI predictions?

### Falsification
- If power-law fit is poor (R² < 0.7): scaling law prediction falsified
- If exponent α outside [0.2, 0.8] for any task type: prediction range falsified
- If regime transitions don't match skill-depth boundaries: morphology falsified

---

## Execution Checklist

- [ ] Create freeze directory: `research/gmi-real-scale-transfer-v1/freezes/`
- [ ] Create results directory: `research/gmi-real-scale-transfer-v1/results/`
- [ ] Freeze all 12 T predictions (SHA256 + publish to #602)
- [ ] Execute T1-T12 runs (sequential or parallel as resources allow)
- [ ] Verify each freeze against actual results
- [ ] Document falsification outcomes
- [ ] Update issue #602 with results summary

## Appendix: GMI Theorems Referenced

| Theorem | Description | Sections Used |
|---------|-------------|---------------|
| T1 | Skill-depth correlation | T1-T10, T12 |
| T2 | Time-ratio invariance | T1, T2 |
| T3 | Knowledge boundaries | T3 |
| T5 | Capacity constraints | T4 |
| T6 | Motor complexity | T5 |
| T7 | Search horizon | T2, T6 |
| T8 | Compositional complexity | T7 |
| T9 | Social complexity | T8 |
| T10 | Domain similarity | T9 |
| T11 | Scaling laws | T12 |

---

**Document Version**: 1.0
**Last Updated**: 2026-09-15
**Maintained by**: ORION-OCM Research Team
