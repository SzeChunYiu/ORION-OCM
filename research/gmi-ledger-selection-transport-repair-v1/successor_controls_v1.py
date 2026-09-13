"""Pinned PR594 countercontrols; no deferred winner or campaign is evaluated."""
import sys
import tempfile
from pathlib import Path
from fractions import Fraction as F
from sources_v1 import module_from_bytes
from historical_v1 import LLS,TL,DC
from joint_comparison_v1 import compare_worlds,compare_box

def run(sources):
    m=module_from_bytes(sources[("PR594",LLS+"learning_law_selection_v1.py")],"new_m",LLS)
    t=module_from_bytes(sources[("PR594",TL+"transport_model_v1.py")],"new_t",TL)
    dc=module_from_bytes(sources[("PR594",DC+"test_developmental_capital_v1.py")],"new_dc",DC)
    malformed=t.compare((F(2),F(1)),(F(3),F(4)))
    valid=t.compare((F(1),F(2)),(F(3),F(4)))
    if malformed!="CERTIFIED_STRICTLY_LOWER" or valid!="CERTIFIED_STRICTLY_LOWER":
        raise ValueError("pinned compare countercontrol changed")
    rejected=False
    try:compare_box((F(2),F(1)),(F(3),F(4)))
    except ValueError:rejected=True
    if not rejected:raise ValueError("reversed interval accepted")
    krc=dc.KRC_K2ReachabilityCondition()
    acquired=krc.acq({"a"},{"a"});reset=krc.acq({"a"},set())
    if not krc.k2({"a"},{"a"}) or (acquired,reset)!=(0,1):
        raise ValueError("atomic retained-part countercontrol")
    prices=m.uniform_prices()
    for i,op in enumerate(m.OPERATIONS):prices[op]=F(2**i)
    if not m.is_generic(prices):raise ValueError("generic-price positive control")
    unresolved=sum(m.select(c,prices)["terminal"]=="UNDETERMINED_TIE" for c in m.all_contracts())
    if unresolved:raise ValueError("generic distinct menu sums should separate")
    names=("learning_law_selection_v1","test_ecology_prediction_v1")
    saved={name:sys.modules.get(name) for name in names}
    try:
        sys.modules[names[0]]=m
        ep=module_from_bytes(sources[("PR590",LLS+"test_ecology_prediction_v1.py")],"ep",LLS)
        sys.modules[names[1]]=ep
        defer=module_from_bytes(sources[("PR594",LLS+"test_deferred_predictions_v1.py")],"defer",LLS)
        with tempfile.TemporaryDirectory(prefix="lst-deferral-") as tmp:
            path=Path(tmp)/"altered.md"
            path.write_bytes(sources[("PR594",LLS+"DEFERRED_PREDICTIONS_V1.md")]+b"\nALTERED TABLE\n")
            defer.DOC=path
            case=defer.TheTableIsFrozen()
            case.test_digest_is_recorded_and_stable()
            case.test_control_editing_the_table_changes_the_digest()
    finally:
        for name in names:
            if saved[name] is None:sys.modules.pop(name,None)
            else:sys.modules[name]=saved[name]
    return dict(status="PINNED_PR594_STATIC_CONTROLS",original_valid_compare=valid,
                original_reversed_interval_false_pass=malformed,
                repaired_reversed_interval_rejected=rejected,
                atomic_retained_part_acquisition=acquired,atomic_reset_acquisition=reset,
                generic_label_ties=unresolved,contracts=128,
                altered_table_passed_original_digest_shape_tests=True,
                correlated=compare_worlds(((1,2),(2,3))),
                marginal_box=compare_box((1,2),(2,3)),
                deferred_winners_evaluated=False)
