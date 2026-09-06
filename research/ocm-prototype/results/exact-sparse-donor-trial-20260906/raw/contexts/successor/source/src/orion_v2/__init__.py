"""Frozen ORION-V2 compatibility subset for OCM historical replay.

Only modules required by inherited OCM/ME-X1 controls are materialized here.
Each PARENT_OWNED module is byte-identical to ORION-V2 at the frozen M0 source
commit; this package root intentionally does not re-export the ORION-V2 kernel
or grant OCM architectural authority.
"""
