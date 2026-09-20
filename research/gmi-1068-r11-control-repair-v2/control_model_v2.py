"""Finite discounted MDP checks with exact rational arithmetic; no external deps."""
from fractions import Fraction as F
from itertools import product


def require(condition, message):
    """Keep evidence checks active under optimized Python execution."""
    if not condition:
        raise AssertionError(message)


def validate(model):
    n, actions, transition, reward, gamma = model
    require(n > 0 and actions > 0 and 0 <= gamma < 1, "invalid MDP dimensions/discount")
    require(len(transition) == len(reward) == n, "state dimension mismatch")
    for s in range(n):
        require(len(transition[s]) == len(reward[s]) == actions, "action mismatch")
        for a in range(actions):
            row = transition[s][a]
            require(len(row) == n and all(p >= 0 for p in row), "invalid transition")
            require(sum(row) == 1, "transition not normalized")


def solve_linear(matrix, rhs):
    """Gauss-Jordan over Q, used only for finite policy evaluation."""
    n = len(rhs)
    aug = [[F(v) for v in matrix[i]] + [F(rhs[i])] for i in range(n)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if aug[i][j])
        aug[j], aug[pivot] = aug[pivot], aug[j]
        c = aug[j][j]
        aug[j] = [x / c for x in aug[j]]
        for i in range(n):
            if i != j:
                c = aug[i][j]
                aug[i] = [x - c * y for x, y in zip(aug[i], aug[j])]
    return tuple(row[-1] for row in aug)


def policy_value(model, policy):
    n, actions, p, r, gamma = model
    require(len(policy) == n and all(0 <= a < actions for a in policy), 'check failed: len(policy) == n and all((0 <= a < actions for a in policy))')
    matrix = [[F(i == j) - gamma * p[i][policy[i]][j] for j in range(n)] for i in range(n)]
    return solve_linear(matrix, [r[i][policy[i]] for i in range(n)])


def optimal_value(model):
    validate(model)
    n, actions, p, r, gamma = model
    evaluated = [(pi, policy_value(model, pi)) for pi in product(range(actions), repeat=n)]
    optimum = tuple(max(v[s] for _, v in evaluated) for s in range(n))
    policies = [pi for pi, values in evaluated if values == optimum]
    require(policies, "no common optimal stationary policy")
    require(optimum == tuple(max(r[s][a] + gamma * sum(p[s][a][t] * optimum[t] for t in range(n))
                                for a in range(actions)) for s in range(n)), "Bellman residual")
    return optimum, policies


def residuals(ground, abstract, phi, bound):
    validate(ground)
    validate(abstract)
    n, actions, p, r, gamma = ground
    m, aa, q, b, gg = abstract
    require(aa == actions and gg == gamma, "action/discount mismatch")
    require(len(phi) == n and set(phi) == set(range(m)), "quotient not onto")
    require(bound >= 0 and all(abs(x) <= bound for rewards in (r, b) for row in rewards for x in row), "reward bound")
    er, ep = F(0), F(0)
    for s in range(n):
        for a in range(actions):
            er = max(er, abs(r[s][a] - b[phi[s]][a]))
            push = [sum(p[s][a][t] for t in range(n) if phi[t] == z) for z in range(m)]
            ep = max(ep, sum(abs(push[z] - q[phi[s]][a][z]) for z in range(m)) / 2)
    value_bound = er / (1-gamma) + 2*gamma*bound*ep / (1-gamma)**2
    return er, ep, value_bound


def fixture(perturbation=F(0), gamma=F(1, 2)):
    """Two task states, two nuisance states, two actions; perturb both conditions."""
    phi = (0, 0, 1, 1)
    q = tuple(tuple((F(3, 4), F(1, 4)) if a == 0 else (F(1, 4), F(3, 4))
                    for a in range(2)) for z in range(2))
    b = tuple(tuple(F(2*z+a, 4) for a in range(2)) for z in range(2))
    p, r = [], []
    for s in range(4):
        change = perturbation * (1 if s % 2 else -1)
        p.append(tuple(tuple((q[phi[s]][a][t//2] + (change if t//2 == 0 else -change))
                             * (F(1, 3) if t % 2 == 0 else F(2, 3)) for t in range(4)) for a in range(2)))
        r.append(tuple(b[phi[s]][a] + change for a in range(2)))
    return (4, 2, tuple(p), tuple(r), gamma), (2, 2, q, b, gamma), phi


def noncollapse_fixture(gamma=F(1, 2)):
    """Current independent bit is observed then discarded before the action."""
    phi = (0, 0, 1, 1)
    p = tuple(tuple(tuple(F(1, 2) if t//2 == s//2 else F(0) for t in range(4))
                    for a in range(2)) for s in range(4))
    r = tuple(tuple(F(a == s % 2) for a in range(2)) for s in range(4))
    q = tuple(tuple(tuple(F(z == zz) for zz in range(2)) for a in range(2)) for z in range(2))
    b = ((F(1, 2), F(1, 2)),) * 2
    return (4, 2, p, r, gamma), (2, 2, q, b, gamma), phi
