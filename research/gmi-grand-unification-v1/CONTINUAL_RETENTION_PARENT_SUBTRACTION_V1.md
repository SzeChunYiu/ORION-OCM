# Continual Retention Parent Subtraction V1

Status: **PARENT BOUNDARY EXPLICIT**  
Date: 2026-09-12

## Parent-owned content

Continual/lifelong learning, catastrophic forgetting, stability–plasticity, experience replay, generative replay, complementary learning systems, regularization, parameter isolation/expansion and distillation are established research programmes.

Representative parent results include:

- classical catastrophic-forgetting observations in sequential neural learning;
- complementary-learning-system and replay approaches, including generative replay;
- mechanism-specific theories such as NTK/task-overlap analyses of forgetting;
- information-theoretic generalization analyses of replay-based continual learning;
- recent feature-learning theory studying provable effects of data replay.

Grand GMI does not claim those methods or empirical findings as inventions.

## Grand-GMI residual

The residual theorem is architecture-free and obligation-relative.

For all obligations that must remain answerable, form the joint semantic response partition with `N_t` classes. Then:

1. exact zero-error persistent memory with no side information requires exactly `N_t` states;
2. a newly learned task costs semantic capacity only when it refines that partition;
3. replay/external memory is simply another channel across the same past→future cut and obeys the product-alphabet lower bound;
4. a deterministic update that irreversibly merges a required class distinction cannot recover it without new side information;
5. shared task semantics produce exact retained-state compression before any particular neural/algorithmic transfer mechanism is chosen.

Thus the theorem explains which part of catastrophic forgetting is universal information loss and which part is contingent on a chosen development/update rule.