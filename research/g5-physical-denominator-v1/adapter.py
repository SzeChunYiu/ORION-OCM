"""Thin adapter: research WAL store behind the incumbent LedgerStore method names.

Production ``src/ocm/store/ledger.py`` is not modified. Experiments that need
the G5.1 parent import ``ResearchLedgerStore`` from this module.
"""

from __future__ import annotations

from wal_ledger import CheckpointedWALLedger


class ResearchLedgerStore(CheckpointedWALLedger):
    """Drop-in research substitute for ``ocm.store.ledger.LedgerStore``."""
