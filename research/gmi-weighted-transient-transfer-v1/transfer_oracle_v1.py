"""Independent exact path execution and absorbing-chain linear equations."""
from fractions import Fraction as F
from itertools import product
from functools import lru_cache

def eliminate(matrix, rhs):
    n = len(rhs)
    aug = [list(matrix[i]) + [rhs[i]] for i in range(n)]
    for k in range(n):
        pivot = next((i for i in range(k,n) if aug[i][k]), None)
        if pivot is None:
            raise ValueError("singular absorbing equations")
        aug[k], aug[pivot] = aug[pivot], aug[k]
        v = aug[k][k]
        aug[k] = [x/v for x in aug[k]]
        for i in range(n):
            if i != k:
                v = aug[i][k]
                aug[i] = [x-v*y for x,y in zip(aug[i],aug[k])]
    return tuple(row[-1] for row in aug)

def stationary(item, policy):
    n = len(item.rows)
    rows = [item.rows[x][policy[x]] for x in range(n)]
    # A finite stationary chain is proper from every state iff each state
    # reaches a terminal in its positive-probability directed graph.
    reachable = {x for x,row in enumerate(rows) if sum(row[n:]) > 0}
    while True:
        extra = {x for x,row in enumerate(rows)
                 if any(row[y] > 0 for y in reachable)}
        new = reachable | extra
        if new == reachable:
            break
        reachable = new
    if len(reachable) != n:
        raise ValueError("not proper from the complete state register")
    matrix = [[F(x == y)-rows[x][y] for y in range(n)] for x in range(n)]
    return dict(cost=eliminate(matrix,[item.charges[x][policy[x]] for x in range(n)]),
                steps=eliminate(matrix,[F(1)]*n))

@lru_cache(None)
def trees(states, actions, horizon):
    if horizon == 0:
        return (None,)
    children = trees(states, actions, horizon-1)
    return tuple((a, kids) for a in range(actions)
                 for kids in product(children, repeat=states))

def execute(item, tree, initial_state=0):
    """Enumerate each path; return accrued cost and the full leaf distribution."""
    n = len(item.rows)
    cost = F(0)
    leaves = [F(0)]*n
    def visit(x, node, probability):
        nonlocal cost
        if node is None:
            leaves[x] += probability
            return
        a, children = node
        cost += probability*item.charges[x][a]
        for y,p in enumerate(item.rows[x][a][:n]):
            if p:
                visit(y, children[y], probability*p)
    visit(initial_state, tree, F(1))
    return cost, tuple(leaves)

def completed_cost(item, tree, tail_policy, initial_state=0):
    prefix, leaves = execute(item, tree, initial_state)
    tail = stationary(item, tail_policy)["cost"]
    return prefix+sum(p*v for p,v in zip(leaves,tail))

def best_stationary(item, fees=None):
    policies = tuple(product(*(range(len(row)) for row in item.rows)))
    evaluated = [(policy,stationary(item,policy)["cost"][0] +
                  (F(0) if fees is None else fees[policy])) for policy in policies]
    return min(evaluated, key=lambda x:(x[1],x[0]))
