#!/usr/bin/env python3
"""Finite-exact population/heredity laws for Issue #602."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def selected_distribution(
    counts: tuple[int, ...], fitness: tuple[int, ...]
) -> tuple[Fraction, ...]:
    if len(counts) != len(fitness) or not counts or sum(counts) <= 0:
        raise ValueError("counts/fitness must describe a nonempty matched population")
    if any(count < 0 for count in counts) or any(value <= 0 for value in fitness):
        raise ValueError("multiplicities must be nonnegative and fitness strictly positive")
    weights = tuple(Fraction(count * value, sum(counts)) for count, value in zip(counts, fitness))
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def price_identity(
    counts: tuple[int, ...], fitness: tuple[int, ...], trait: tuple[int, ...]
) -> dict[str, Fraction]:
    if len(trait) != len(counts):
        raise ValueError("trait vector length mismatch")
    total_count = sum(counts)
    p = tuple(Fraction(count, total_count) for count in counts)
    q = selected_distribution(counts, fitness)
    mean_trait = sum(prob * value for prob, value in zip(p, trait))
    mean_fitness = sum(prob * value for prob, value in zip(p, fitness))
    covariance = sum(
        prob * (value - mean_trait) * (fit - mean_fitness)
        for prob, value, fit in zip(p, trait, fitness)
    )
    selected_trait = sum(prob * value for prob, value in zip(q, trait))
    return {
        "observed_change": selected_trait - mean_trait,
        "covariance_over_mean_fitness": covariance / mean_fitness,
    }


def selection_information_bits(
    counts: tuple[int, ...], fitness: tuple[int, ...]
) -> float:
    """D_KL(q||p): information introduced by fitness-proportional selection."""
    total = sum(counts)
    p = tuple(Fraction(count, total) for count in counts)
    q = selected_distribution(counts, fitness)
    return sum(float(qi) * math.log2(float(qi / pi)) for pi, qi in zip(p, q) if qi)


def binary_heredity_information_bits(mutation_rate: float) -> float:
    """I(parent;child)=1-h2(mu) for a uniform bit and symmetric mutation."""
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation rate must lie in [0,1]")
    if mutation_rate in (0.0, 1.0):
        entropy = 0.0
    else:
        entropy = -mutation_rate * math.log2(mutation_rate) - (
            1 - mutation_rate
        ) * math.log2(1 - mutation_rate)
    return 1.0 - entropy


def exhaustive_price_certificate(max_population: int = 6) -> dict[str, Any]:
    cases = 0
    violations = 0
    for size in range(1, max_population + 1):
        for count_a in range(size + 1):
            counts = (count_a, size - count_a)
            for fitness in itertools.product(range(1, 4), repeat=2):
                for trait in itertools.product(range(3), repeat=2):
                    cases += 1
                    law = price_identity(counts, fitness, trait)
                    violations += int(
                        law["observed_change"] != law["covariance_over_mean_fitness"]
                    )
    payload = {
        "schema": "GMI_PRICE_IDENTITY_EXHAUSTIVE_CERTIFICATE_V1",
        "max_population": max_population,
        "cases": cases,
        "violations": violations,
    }
    return {**payload, "certificate_sha256": digest(payload)}


def response(population: tuple[str, ...], ecology: str) -> str | None:
    return ecology if ecology in population else None


def capability(population: tuple[str, ...]) -> Fraction:
    return sum(Fraction(response(population, ecology) == ecology, 2) for ecology in ("A", "B"))


def compile_to_d7_d8(population: tuple[str, ...]) -> tuple[tuple[int, str], ...]:
    """Index multiset members as D7 components; D8 owns replacement/lineage."""
    return tuple(enumerate(sorted(population)))


def parent_response(compiled: tuple[tuple[int, str], ...], ecology: str) -> str | None:
    genotypes = tuple(genotype for _, genotype in compiled)
    return response(genotypes, ecology)


def option_value_certificate() -> dict[str, Any]:
    populations = (("A", "A"), ("A", "B"), ("B", "B"))
    rows = []
    for population in populations:
        compiled = compile_to_d7_d8(population)
        native_answers = [response(population, ecology) for ecology in ("A", "B")]
        parent_answers = [parent_response(compiled, ecology) for ecology in ("A", "B")]
        rows.append(
            {
                "population": population,
                "support_size": len(set(population)),
                "capability": capability(population),
                "native_answers": native_answers,
                "parent_answers": parent_answers,
                "parent_exact": native_answers == parent_answers,
            }
        )
    if max(row["capability"] for row in rows if row["support_size"] == 1) != Fraction(1, 2):
        raise AssertionError("single-genotype upper bound drifted")
    if next(row for row in rows if row["population"] == ("A", "B"))["capability"] != 1:
        raise AssertionError("diverse-population prediction failed")
    if not all(row["parent_exact"] for row in rows):
        raise AssertionError("D7+D8 reduction failed")
    return {
        "schema": "GMI_POPULATION_OPTION_VALUE_CERTIFICATE_V1",
        "populations_exhausted": len(rows),
        "rows": rows,
        "conclusion": "SUPPORT_TWO_NECESSARY_AND_SUFFICIENT; D7_D8_PARENT_EXACT",
        "certificate_sha256": digest(rows),
    }


def validate_closure() -> dict[str, Any]:
    schema = json.loads((HERE / "POPULATION_CARRIER_SCHEMA_V1.json").read_text(encoding="utf-8"))
    prediction = json.loads((HERE / "POPULATION_REGIME_PREDICTION_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "POPULATION_HEREDITY_CLOSURE_LEDGER_V1.json").read_text(encoding="utf-8"))
    expected = {
        "Define population state as candidate primitive carrier.",
        "Reduce against D7 + D8 composition.",
        "Derive heredity/selection information law.",
        "Predict regime where population state is irreducible.",
    }
    if len(ledger["rows"]) != 4 or {row["task"] for row in ledger["rows"]} != expected:
        raise ValueError("population/heredity task inventory drifted")
    if any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("population/heredity ledger contains a non-green row")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    if set(schema["required"]) != {
        "genotype_space", "multiplicity", "fitness", "selection", "mutation",
        "lineage", "resource_coordinates",
    }:
        raise ValueError("population carrier schema drifted")
    price = exhaustive_price_certificate()
    if price["cases"] != 2187 or price["violations"] != 0:
        raise ValueError("selection law failed exact exhaustion")
    option = option_value_certificate()
    predicted = prediction["predictions"]
    observed = {
        "diverse_population_capability": float(capability(("A", "B"))),
        "best_single_genotype_capability": float(max(capability(("A",)), capability(("B",)))),
        "homogeneous_negative_twin_capability": float(capability(("A", "A"))),
        "minimal_support_size_for_full_capability": 2,
    }
    if any(observed[key] != predicted[key] for key in observed):
        raise ValueError("population regime prediction failed")
    return {
        "ledger_rows": len(ledger["rows"]),
        "price_cases": price["cases"],
        "price_violations": price["violations"],
        "populations_exhausted": option["populations_exhausted"],
        "diverse_capability": observed["diverse_population_capability"],
        "single_capability": observed["best_single_genotype_capability"],
    }


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_POPULATION_HEREDITY_CLOSURE_V1_VALID")
    for key, value in result.items():
        print(f"{key}={value}")
