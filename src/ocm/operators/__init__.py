"""Operator / skill registry namespace (M2 §7)."""

from .registry import BackendKind, Candidate, CoverageCertificate, OperatorRegistry, OperatorSpec, compose_candidate

__all__ = ["BackendKind", "Candidate", "CoverageCertificate", "OperatorRegistry", "OperatorSpec", "compose_candidate"]
