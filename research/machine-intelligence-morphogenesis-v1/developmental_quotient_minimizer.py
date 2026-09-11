from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping

State = Hashable
Event = Hashable
Output = Hashable


@dataclass(frozen=True)
class Transition:
    next_state: State
    output: Output


def minimize_mealy(
    states: Iterable[State],
    events: Iterable[Event],
    transition: Mapping[State, Mapping[Event, Transition]],
):
    """Exact partition refinement for a finite deterministic Mealy machine.

    Event symbols may represent ordinary queries/actions or developmental events
    such as teaching/feedback. Outputs may include verified answers and resource
    receipts. The returned blocks are therefore exact future-trace equivalence
    classes under the supplied event alphabet.
    """
    states = tuple(states)
    events = tuple(events)

    by_output = defaultdict(set)
    for state in states:
        immediate = tuple(transition[state][event].output for event in events)
        by_output[immediate].add(state)
    groups = list(by_output.values())

    while True:
        group_of = {state: index for index, group in enumerate(groups) for state in group}
        refined = []
        changed = False

        for group in groups:
            buckets = defaultdict(set)
            for state in group:
                signature = (
                    tuple(transition[state][event].output for event in events),
                    tuple(
                        group_of[transition[state][event].next_state]
                        for event in events
                    ),
                )
                buckets[signature].add(state)
            if len(buckets) > 1:
                changed = True
            refined.extend(buckets.values())

        groups = refined
        if not changed:
            break

    return tuple(frozenset(group) for group in groups)


def developmental_fixture():
    """Four-state exact witness.

    States 0 and 1 have identical current query behaviour.  State 0 learns from
    `teach1`; state 1 ignores it.  States 2 and 3 are exact duplicates and should
    quotient together.
    """
    events = ("q0", "q1", "teach1")
    states = (0, 1, 2, 3)
    raw = {
        0: {
            "q0": (0, ("ans0", 1)),
            "q1": (0, ("ans0", 1)),
            "teach1": (2, ("ack", 1)),
        },
        1: {
            "q0": (1, ("ans0", 1)),
            "q1": (1, ("ans0", 1)),
            "teach1": (1, ("ack", 1)),
        },
        2: {
            "q0": (2, ("ans0", 1)),
            "q1": (2, ("ans1", 1)),
            "teach1": (2, ("ack", 1)),
        },
        3: {
            "q0": (3, ("ans0", 1)),
            "q1": (3, ("ans1", 1)),
            "teach1": (3, ("ack", 1)),
        },
    }
    transition = {
        state: {
            event: Transition(next_state, output)
            for event, (next_state, output) in row.items()
        }
        for state, row in raw.items()
    }
    return states, events, transition


if __name__ == "__main__":
    states, events, transition = developmental_fixture()
    print(minimize_mealy(states, events, transition))
