"""Learner-dependent transfer plus full logical lifetime comparisons."""
from collections import Counter
from fractions import Fraction as F
from math import isqrt
from teaching_machine_v1 import (HYPOTHESES, MESSAGES, learn, teach, pack, receive,
                                 encoder_oracle, truth_table_oracle, acquire)
from teaching_costs_v1 import prices, comparison, first_saving

def run_teaching():
    rows = []
    for mode in (0,1):
        for message in MESSAGES:
            if learn(message,mode) != truth_table_oracle(message,mode):
                raise ValueError("independent decoder relation")
        for h in HYPOTHESES:
            trace=Counter()
            acquired = acquire(lambda x:h[x],trace)
            message = teach(acquired,mode,trace)
            if message != encoder_oracle(h,mode):
                raise ValueError("independent optimal message")
            if receive(pack(message,mode),mode) != h:
                raise ValueError("actual transfer")
            row = comparison(h,mode,prices(),1)
            n = first_saving(row["C"],row["S"],row["U"])
            before = comparison(h,mode,prices(),n-1)
            after = comparison(h,mode,prices(),n)
            if before["taught"] < before["independent"] or after["taught"] >= after["independent"]:
                raise ValueError("charged break-even boundary")
            cheap = comparison(h,mode,prices(0),2)
            if first_saving(cheap["C"],cheap["S"],cheap["U"]) is not None:
                raise ValueError("cheap oracle no-saving control")
            rows.append(dict(target=h,mode=mode,message=message,bits=pack(message,mode),
                             source_acquisition_events=dict(trace), first_saving_agents=n,
                             at_boundary=after, before_boundary=before,
                             zero_oracle_price_no_saving=cheap))
    wrong = teach((0,0),0)
    mismatch = learn(wrong,1)
    if mismatch == (0,0):
        raise ValueError("wrong learner control")
    empty = pack((-1,-1),0)
    untrusted_errors = sum(receive(empty,0) != h for h in HYPOTHESES)
    if untrusted_errors != 3:
        raise ValueError("untrusted consistent-message control")
    fallbacks = [acquire(lambda x,h=h:h[x],Counter()) for h in HYPOTHESES]
    if fallbacks != list(HYPOTHESES):
        raise ValueError("paid truthful fallback")
    return dict(rows=rows, decoder_relations=18, adequate_encoders=8,
                wrong_learner_output=mismatch, untrusted_empty_errors=untrusted_errors,
                oracle_fallback_adequate=True, newly_created_skills=0,
                sublinear_unbounded_remainder=[dict(n=n,remainder=isqrt(n),
                                                  average_extra=F(isqrt(n),n))
                                               for n in (1,4,16,64,256)])
