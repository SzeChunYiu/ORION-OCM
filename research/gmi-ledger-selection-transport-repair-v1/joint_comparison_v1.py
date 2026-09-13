"""Correlation-aware finite comparisons; box mode explicitly admits all products."""
from selection_v1 import require,rational

def compare_worlds(worlds):
    rows=tuple(worlds)
    require(bool(rows), "nonempty joint feasible set required")
    differences=[]
    for row in rows:
        require(type(row) is tuple and len(row)==2, "two-cost joint row required")
        a,b=(rational(x,True) for x in row)
        differences.append(a-b)
    largest=max(differences);smallest=min(differences)
    return dict(status="CERTIFIED_STRICTLY_LOWER" if largest<0 else
                       "CERTIFIED_STRICTLY_HIGHER" if smallest>0 else "UNRESOLVED",
                maximum_difference=largest,minimum_difference=smallest,
                scope="SUPPLIED_FINITE_JOINT_WORLDS")

def interval(value):
    require(type(value) is tuple and len(value)==2, "interval pair required")
    lo=rational(value[0],True)
    hi=None if value[1] is None else rational(value[1],True)
    require(hi is None or lo<=hi, "empty/reversed interval")
    return lo,hi

def compare_box(a,b):
    al,ah=interval(a);bl,bh=interval(b)
    return dict(status="CERTIFIED_STRICTLY_LOWER" if ah is not None and ah<bl else
                       "CERTIFIED_STRICTLY_HIGHER" if bh is not None and bh<al else "UNRESOLVED",
                scope="FULL_CARTESIAN_PRODUCT_OF_CLOSED_INTERVALS")
