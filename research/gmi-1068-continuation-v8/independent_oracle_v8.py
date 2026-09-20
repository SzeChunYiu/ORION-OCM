"""Independent product-pair BFS, recursive responses and generated machines.

No production imports; responses expose every observation and emitted edge.
"""
from collections import deque
from itertools import product
from random import Random


def response(observations, transitions, state, word, budget=None):
    """Recursive reference execution; budget rejects before emitting an edge."""
    first = (("OBS", observations[state]),)
    if not word:
        return first
    edge = transitions[state][word[0]]
    if edge is None or (budget is not None and edge[1] > budget):
        return first + (("ILLEGAL",),)
    output, cost, target = edge
    residual = None if budget is None else budget - cost
    return first + (("EDGE", output, cost),) + response(
        observations, transitions, target, word[1:], residual)


def distinguish(observations, transitions, left, right):
    """Return a shortest distinguishing word, or None after complete pair BFS."""
    if observations[left] != observations[right]:
        return ()
    queue = deque([(left, right, ())])
    visited = {(left, right)}
    while queue:
        first, second, prefix = queue.popleft()
        for action, (a, b) in enumerate(zip(transitions[first], transitions[second])):
            word = prefix + (action,)
            if (a is None) != (b is None):
                return word
            if a is None:
                continue
            if a[:2] != b[:2] or observations[a[2]] != observations[b[2]]:
                return word
            pair = (a[2], b[2])
            if pair not in visited:
                visited.add(pair)
                queue.append((*pair, word))
    return None


def partition(observations, transitions):
    representatives, classes = [], []
    for state in range(len(observations)):
        for index, representative in enumerate(representatives):
            if distinguish(observations, transitions, state, representative) is None:
                classes.append(index)
                break
        else:
            classes.append(len(representatives))
            representatives.append(state)
    return tuple(classes)


def words(action_count, depth):
    return tuple(word for length in range(depth + 1)
                 for word in product(range(action_count), repeat=length))


def exhaustive_two_state():
    options = (None,) + tuple(product(range(2), range(2), range(2)))
    for observations in product((None, 0, 1), repeat=2):
        for flat in product(options, repeat=4):
            yield observations, (flat[:2], flat[2:])


def generated_larger():
    for size in range(3, 7):
        for seed in range(16):
            random = Random(65536 * size + seed)
            observations = tuple(random.choice((None, 0, 1)) for _ in range(size))
            transitions = tuple(tuple(None if random.randrange(5) == 0 else
                                (random.randrange(3), random.randrange(3), random.randrange(size))
                                for _ in range(2)) for _ in range(size))
            yield observations, transitions


def nondeterministic_responses(observations, transitions, state, word):
    """May-response sets for the explicit nondeterminism boundary fixture."""
    start = (("OBS", observations[state]),)
    if not word:
        return {start}
    choices = transitions[state][word[0]]
    if not choices:
        return {start + (("ILLEGAL",),)}
    return {start + (("EDGE", output, cost),) + suffix
            for output, cost, target in choices
            for suffix in nondeterministic_responses(observations, transitions, target, word[1:])}


def nondeterministic_bisimulation(observations, transitions):
    relation = {(a, b) for a in range(len(observations)) for b in range(len(observations))
                if observations[a] == observations[b]}
    while True:
        retained = set()
        for first, second in relation:
            matches = True
            for left, right in zip(transitions[first], transitions[second]):
                for sources, targets in ((left, right), (right, left)):
                    if any(not any(a[:2] == b[:2] and (a[2], b[2]) in relation
                                   for b in targets) for a in sources):
                        matches = False
            if matches:
                retained.add((first, second))
        if retained == relation:
            return relation
        relation = retained
