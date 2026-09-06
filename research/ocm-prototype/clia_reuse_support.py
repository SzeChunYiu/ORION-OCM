"""Use existing warrant algebra to expose actual assumption support, not derived receipt IDs."""
from ocm.kso.warrant import WarrantProfile
import clia_reuse_descriptor as D


def encode(profile):
    return D.profile({k: [sorted(str(e) for e in term) for term in getattr(profile, k)] for k in ('lower', 'upper')})


def decode(profile):
    p = D.profile(profile)
    return WarrantProfile(tuple(frozenset(t) for t in p['lower']), tuple(frozenset(t) for t in p['upper']))


def assumptions(runtime, profile, seen=frozenset()):
    """Substitute known derived-record warrants through existing meet/join operations."""
    expanded = {}
    for bound in ('lower', 'upper'):
        total = WarrantProfile.zero()
        for term in getattr(profile, bound):
            product = WarrantProfile.one()
            for eid in term:
                if eid in seen: raise ValueError('cyclic derived evidence')
                record = runtime.state.evidence.records.get(eid)
                if record is None: raise ValueError('unknown supporting evidence')
                p = record.warrant if record.is_assumption else assumptions(runtime, record.warrant, seen | {eid})
                product = product.meet(p)
            total = total.join(product)
        expanded[bound] = getattr(total, bound)
    return WarrantProfile(expanded['lower'], expanded['upper'])
