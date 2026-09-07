"""Broad experiment/launcher inventory, outside conventional public-operation cost."""
from pathlib import Path
from unary_method_plain import raw,parse,hashed,bump,inventory

def sources(work=None):
    here=Path(__file__).resolve().parent;root=here.parents[1]
    paths=list((root/"src/ocm").rglob("*.py"))+list((root/"src/orion_v2").rglob("*.py"))
    for pattern in ("unary_rule_*.py","unary_method_*.py","unary_parent_*.py"):paths+=list(here.glob(pattern))
    paths+=list((root/"docs/plans/unary-adaptive-parent-v2-1").glob("*.md"))
    paths+=[root/"research/math-language-v1"/n for n in
            ("unary_contract.py","unary_language.py","unary_solver.py","unary_verify.py")]
    return inventory(paths,root,work)
