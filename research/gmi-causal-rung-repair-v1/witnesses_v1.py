"""Authored exposed controls; all intervention laws evaluated, no hidden tests."""
from fractions import Fraction as F
from scm_v1 import from_units, law, complete_laws, necessity
from bounds_v1 import identified_or_bounds

def rung_pairs():
    return {
        'six_original': (
            ((0,0,0),(0,0,0),(1,1,1),(1,0,1),(1,0,0),(1,0,0)),
            ((0,0,0),(0,0,0),(1,0,1),(1,0,1),(1,1,0),(1,0,0))),
        'two_smaller': (((1,1,1),(1,0,0)), ((1,0,1),(1,1,0))),
        'three_treatment_supported': (
            ((0,0,0),(1,1,1),(1,0,0)),
            ((0,0,0),(1,0,1),(1,1,0))),
    }

def pair_results():
    out = {}
    for name, rows in rung_pairs().items():
        left, right = map(from_units, rows)
        out[name] = {'root_units': len(rows[0]),
                     'all_nine_joint_laws_equal': complete_laws(left) == complete_laws(right),
                     'observed': law(left), 'all_joint_laws': complete_laws(left),
                     'left_pn': necessity(left),
                     'right_pn': necessity(right),
                     'minimax_absolute_error': abs(necessity(left)-necessity(right))/2}
    return out

def oriented_law(forward, do_x=None):
    # Fully observed X->Y versus Y->X; product independent U fair and E~Bern1/4.
    out = [F(0)]*4
    for u in (0,1):
        for e, pe in ((0,F(3,4)), (1,F(1,4))):
            if forward:
                x = u if do_x is None else do_x
                y = x ^ e
            else:
                y = u
                x = (y ^ e) if do_x is None else do_x
            out[2*x+y] += pe/2
    return tuple(out)

def orientation_result():
    p = oriented_law(True)
    return {'same_full_support_observed': p == oriented_law(False) and min(p)>0,
            'dependent': p[3] != sum(p[2:])*sum(p[1::2]),
            'forward_do1': sum(oriented_law(True,1)[1::2]),
            'reverse_do1': sum(oriented_law(False,1)[1::2])}
