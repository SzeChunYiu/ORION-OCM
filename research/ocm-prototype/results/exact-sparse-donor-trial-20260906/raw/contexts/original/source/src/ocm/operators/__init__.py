"""Operator / skill registry namespace (M2 §7)."""

from .registry import BackendKind, Candidate, CoverageCertificate, OperatorGuarantee, OperatorRegistry, OperatorSpec, compose_candidate

__all__ = ["BackendKind", "Candidate", "CoverageCertificate", "OperatorGuarantee", "OperatorRegistry", "OperatorSpec", "compose_candidate"]
