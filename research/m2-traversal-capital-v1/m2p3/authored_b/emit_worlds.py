#!/usr/bin/env python3
"""
Deterministic puzzle world generator.
Generates worlds.jsonl containing 6+ distinct puzzle worlds with hidden chunk sets.
"""

import itertools
import json
from typing import List, Dict, Tuple, Set


def apply_op(poly: Dict[int, int], op: str) -> Dict[int, int]:
    """Apply an operation to a polynomial represented as {exponent: coefficient}."""
    if op == 'add1':
        result = poly.copy()
        result[0] = result.get(0, 0) + 1
        return result
    elif op == 'sub1':
        result = poly.copy()
        result[0] = result.get(0, 0) - 1
        return result
    elif op == 'dbl':
        return {exp: coeff * 2 for exp, coeff in poly.items()}
    elif op == 'sqr':
        result = {}
        for exp1, coeff1 in poly.items():
            for exp2, coeff2 in poly.items():
                exp = exp1 + exp2
                result[exp] = result.get(exp, 0) + coeff1 * coeff2
        return result
    else:
        raise ValueError(f"Unknown op: {op}")


def builder_to_poly(builder: List[str]) -> Dict[int, int]:
    """Convert a builder (sequence of ops) to the polynomial it computes (starting from x)."""
    poly = {1: 1}  # Start with x
    for op in builder:
        poly = apply_op(poly, op)
    return poly


def normalize_poly(poly: Dict[int, int]) -> Tuple:
    """Convert polynomial to a canonical immutable tuple for hashing/comparison."""
    terms = sorted((exp, coeff) for exp, coeff in poly.items() if coeff != 0)
    return tuple(terms)


def decomposes_into_chunks(builder: List[str], chunks: List[List[str]]) -> bool:
    """Check if a builder decomposes exactly into concatenated chunks using DP."""
    chunks_set = set(tuple(c) for c in chunks)

    n = len(builder)
    # dp[i] = True if builder[0:i] decomposes into chunks
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and tuple(builder[j:i]) in chunks_set:
                dp[i] = True
                break

    return dp[n]


def enumerate_builders(max_length: int):
    """Enumerate all builders in canonical order: shorter first, then lexicographic."""
    ops = ['add1', 'sub1', 'dbl', 'sqr']
    for length in range(max_length + 1):
        for combo in itertools.product(ops, repeat=length):
            yield list(combo)


def get_world_members(chunks: List[List[str]], min_builder_length: int,
                      max_builder_length: int = 8) -> Tuple[Dict[int, List], Dict]:
    """
    Get all polynomials that belong to this world.
    Returns: (members_by_length, canonical_builders)
    """
    canonical_builders = {}  # poly_id -> builder
    members_by_length = {}   # builder_length -> [poly_id, ...]

    for builder in enumerate_builders(max_builder_length):
        if len(builder) < min_builder_length:
            continue

        if not decomposes_into_chunks(builder, chunks):
            continue

        poly = builder_to_poly(builder)
        poly_id = normalize_poly(poly)

        # Only record the first (canonical) builder for each polynomial
        if poly_id not in canonical_builders:
            canonical_builders[poly_id] = builder
            length = len(builder)
            if length not in members_by_length:
                members_by_length[length] = []
            members_by_length[length].append(poly_id)

    return members_by_length, canonical_builders


def divide_into_parts(members_by_length: Dict[int, List],
                      fractions: Dict[str, float]) -> Dict[str, int]:
    """Divide members into initial/tuning/future parts per length class."""
    initial_count = 0
    tuning_count = 0
    future_count = 0

    for length in sorted(members_by_length.keys()):
        members = members_by_length[length]
        n = len(members)

        if n == 0:
            continue

        n_initial = max(1, round(n * fractions['initial']))
        n_tuning = max(0, round(n * fractions['tuning']))
        n_future = n - n_initial - n_tuning

        # Ensure future is at least 1 if n > 2
        if n > 2 and n_future == 0:
            if n_tuning > 0:
                n_tuning -= 1
                n_future = 1
            else:
                n_initial -= 1
                n_future = 1

        initial_count += n_initial
        tuning_count += n_tuning
        future_count += n_future

    return {
        'initial': initial_count,
        'tuning': tuning_count,
        'future': future_count,
        'total': initial_count + tuning_count + future_count
    }


# World configuration: chunk sets, parameters, and metadata
WORLDS_CONFIG = [
    {
        'world_id': 'world_1_basic_add_dbl_sub',
        'chunks': [['add1', 'add1'], ['dbl', 'dbl'], ['sub1', 'sub1'], ['dbl', 'add1']],
        'min_builder_length': 4,
        'part_fractions': {'initial': 0.50, 'tuning': 0.20, 'future': 0.30},
        'name': 'Add, Double, Subtract',
        'description': 'Chunks combining addition, doubling, and subtraction in short sequences'
    },
    {
        'world_id': 'world_2_mixed_cross',
        'chunks': [['add1', 'dbl'], ['sub1', 'add1'], ['dbl', 'sub1'], ['add1', 'sub1']],
        'min_builder_length': 4,
        'part_fractions': {'initial': 0.45, 'tuning': 0.25, 'future': 0.30},
        'name': 'Mixed Cross-Operations',
        'description': 'Four chunks with mixed operation pairs exploring interplay'
    },
    {
        'world_id': 'world_3_varied_lengths',
        'chunks': [['dbl', 'dbl'], ['add1', 'dbl', 'add1'], ['sub1', 'sub1'],
                   ['sqr', 'add1'], ['dbl', 'sqr']],
        'min_builder_length': 5,
        'part_fractions': {'initial': 0.55, 'tuning': 0.15, 'future': 0.30},
        'name': 'Varied Chunk Lengths',
        'description': 'Five chunks with mix of length 2 and 3, introducing squaring'
    },
    {
        'world_id': 'world_4_six_chunks',
        'chunks': [['add1', 'add1'], ['sub1', 'sub1'], ['dbl', 'dbl'],
                   ['dbl', 'add1'], ['add1', 'dbl'], ['sub1', 'add1']],
        'min_builder_length': 4,
        'part_fractions': {'initial': 0.50, 'tuning': 0.20, 'future': 0.30},
        'name': 'Six Core Chunks',
        'description': 'Six chunks exploring linear transformations with symmetry'
    },
    {
        'world_id': 'world_5_nonlinear_focus',
        'chunks': [['sqr', 'add1'], ['sqr', 'sub1'], ['sqr', 'dbl'],
                   ['dbl', 'dbl'], ['add1', 'add1', 'dbl'], ['sub1', 'dbl']],
        'min_builder_length': 4,
        'part_fractions': {'initial': 0.40, 'tuning': 0.30, 'future': 0.30},
        'name': 'Nonlinear Focus',
        'description': 'Six chunks with emphasis on squaring operations'
    },
    {
        'world_id': 'world_6_full_palette',
        'chunks': [['add1', 'dbl'], ['dbl', 'add1'], ['sub1', 'dbl'], ['dbl', 'sub1'],
                   ['add1', 'sub1'], ['sub1', 'add1'], ['dbl', 'dbl'], ['add1', 'dbl', 'sub1']],
        'min_builder_length': 4,
        'part_fractions': {'initial': 0.50, 'tuning': 0.25, 'future': 0.25},
        'name': 'Full Palette',
        'description': 'Eight chunks covering diverse patterns of linear operations'
    }
]


def main():
    """Generate all worlds and write worlds.jsonl to current directory."""
    worlds = []

    for config in WORLDS_CONFIG:
        chunks = config['chunks']
        min_length = config['min_builder_length']

        # Compute world members
        members_by_length, canonical_builders = get_world_members(chunks, min_length)

        total_members = sum(len(m) for m in members_by_length.values())

        # Divide into parts
        counts = divide_into_parts(members_by_length, config['part_fractions'])

        # Build world object
        world = {
            'world_id': config['world_id'],
            'chunks': chunks,
            'min_builder_length': min_length,
            'part_fractions': config['part_fractions'],
            'surface': {
                'name': config['name'],
                'description': config['description'],
                'total_members': total_members,
                'members_by_length': {str(k): len(v) for k, v in sorted(members_by_length.items())}
            },
            'intent': {
                'intent_role': 'audit_only',
                'expected_total_members': total_members,
                'expected_part_counts': counts
            }
        }

        worlds.append(world)

    # Write to worlds.jsonl in current directory
    with open('worlds.jsonl', 'w') as f:
        for world in worlds:
            f.write(json.dumps(world) + '\n')

    print(f"Generated {len(worlds)} worlds in worlds.jsonl")
    for world in worlds:
        print(f"  {world['world_id']}: {world['surface']['total_members']} members")


if __name__ == '__main__':
    main()
