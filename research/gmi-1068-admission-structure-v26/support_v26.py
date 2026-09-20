"""Test-only conversion; expected semantics live in independent tuple oracles."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
import core_v26 as core
import oracle_v26 as oracle


def actual(c):
    result=core.old_categories.reconstruct(core.Table(c[0]))
    oracle.certify(unpack(result),c)
    return result


def make(c):
    rows,src,dst,ids=c
    result=core.Typed(len(ids),src,dst,ids,core.Table(rows))
    core.old_categories.validate_category(result)
    return result


def unpack(cat):return cat.table.rows,cat.source,cat.target,cat.identities
