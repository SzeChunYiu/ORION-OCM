"""Actual finite machine traces, image lesions, and independent Boolean oracle."""
from itertools import product
from memory_costs_v1 import lifetime,intervention_schedule
from memory_machine_v1 import (construct, encode, decode, service, setup, zero_slot,
                               replace_query, intervention, restore)

def expected(h, query):
    return (h[0], h[1], (h[0]+h[1]) % 2)[query]

def run_memory():
    rows = []
    for compact in (False, True):
        for history in product((0, 1), repeat=2):
            image = construct(history, compact)
            bits = encode(image)
            intact = [service(image, q) for q in range(3)]
            if [r["answer"] for r in intact] != [expected(history,q) for q in range(3)]:
                raise ValueError("intact adequacy")
            sham = decode(bits)
            lesioned = replace_query(image, 2, ("L0", "EMIT"))
            slot = zero_slot(image, 0)
            if [service(sham,q) for q in range(3)] != intact:
                raise ValueError("sham trace changed")
            if [service(restore(bits),q) for q in range(3)] != intact:
                raise ValueError("restoration failed")
            for q in (0, 1):
                if service(lesioned,q) != intact[q]:
                    raise ValueError("claimed interface invariance failed")
            edit = intervention(image, lesioned)
            rows.append(dict(compact=compact, history=history, image=bits,
                             setup=setup(image,compact), lifetime=lifetime(image,compact), intact=intact,
                             full_intervention_schedule=intervention_schedule(image,compact),
                             code_lesion=[service(lesioned,q) for q in range(3)],
                             shared_slot_lesion=[service(slot,q) for q in range(3)],
                             intervention={k:v for k,v in edit.items() if k!="image"},
                             restored_exact=True, sham_exact=True))
    h = (1, 0)
    compact = construct(h, True)
    changed = zero_slot(compact, 0)
    affected = [q for q in range(3) if service(compact,q)["answer"] != service(changed,q)["answer"]]
    if affected != [0, 2]:
        raise ValueError("shared-slot countercontrol")
    direct = replace_query(compact, 2, ("EMIT0",))
    if service(direct,2,stack_capacity=0)["answer"] != 0:
        raise ValueError("stack-only countercontrol")
    correlated = [(x,x) for x in (0,1)]
    truth = {h:service(replace_query(construct(h,True),2,("EMIT0",)),2)["answer"]
             for h in product((0,1),repeat=2)}
    if not all(truth[h] == expected(h,2) for h in correlated):
        raise ValueError("correlated promise")
    growth = []
    for t in range(1,5):
        signatures = {tuple(h[q] for q in range(t)) for h in product((0,1),repeat=t)}
        growth.append(dict(t=t, classes=len(signatures), exact_bits=t, raw_bits=t))
    return dict(rows=rows, shared_slot_changes_queries=affected, growth=growth,
                constant_decoder_full_promise_errors=sum(truth[h]!=expected(h,2) for h in truth),
                correlated_promise_errors=0, snapshot_and_restore_charged=True)
