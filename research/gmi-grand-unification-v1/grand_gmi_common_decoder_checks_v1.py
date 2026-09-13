#!/usr/bin/env python3
"""Exact finite checks for joint risks; no ecology-specific action leakage."""
from fractions import Fraction as F
from itertools import product
import json


def binary_channels():
    return tuple(tuple((1 - p, p) for p in row)
                 for row in product((F(0), F(1, 2), F(1)), repeat=2))


def decoder_rows(probabilities, nz, ny):
    return tuple(tuple((1 - probabilities[z * ny + y], probabilities[z * ny + y])
                       for y in range(ny)) for z in range(nz))


def deterministic_decoders(nz, ny):
    return tuple(decoder_rows(bits, nz, ny)
                 for bits in product((F(0), F(1)), repeat=nz * ny))


def risk(channel, decoder, sources, losses):
    return tuple(sum((mass * channel[x][z] * decoder[z][y][a] * losses[e][x][y][a]
                      for x, row in enumerate(source)
                      for y, mass in enumerate(row)
                      for z in range(len(channel[x]))
                      for a in range(len(decoder[z][y]))), F(0))
                 for e, source in enumerate(sources))


def cell_losses(channel, sources, losses, z, y, e):
    return tuple(sum((sources[e][x][y] * channel[x][z] * losses[e][x][y][a]
                      for x in range(len(channel))), F(0))
                 for a in range(len(losses[e][0][y])))


def oracle_envelope(channel, sources, losses):
    return tuple(sum((min(cell_losses(channel, sources, losses, z, y, e))
                      for z in range(len(channel[0]))
                      for y in range(len(sources[e][0]))), F(0))
                 for e in range(len(sources)))


def common_argmins_exist(channel, sources, losses):
    for z in range(len(channel[0])):
        for y in range(len(sources[0][0])):
            common = set(range(len(losses[0][0][y])))
            for e in range(len(sources)):
                row = cell_losses(channel, sources, losses, z, y, e)
                common &= {a for a, value in enumerate(row) if value == min(row)}
            if not common:
                return False
    return True


def compose_channel(channel, garbling):
    return tuple(tuple(sum((channel[x][z] * garbling[z][j]
                            for z in range(len(garbling))), F(0))
                       for j in range(len(garbling[0])))
                 for x in range(len(channel)))


def compose_decoder(garbling, decoder):
    return tuple(tuple(tuple(sum((garbling[z][j] * decoder[j][y][a]
                                  for j in range(len(decoder))), F(0))
                             for a in range(len(decoder[0][y])))
                       for y in range(len(decoder[0])))
                 for z in range(len(garbling)))


def hidden_ecology_witness():
    channel = ((F(1),),)
    sources = (((F(1),),), ((F(1),),))
    losses = ((((0, 1),),), (((1, 0),),))
    profiles = tuple(risk(channel, d, sources, losses)
                     for d in deterministic_decoders(1, 1))
    oracle = oracle_envelope(channel, sources, losses)
    fair = risk(channel, decoder_rows((F(1, 2),), 1, 1), sources, losses)
    assert oracle == (0, 0) and oracle not in profiles
    assert profiles == ((0, 1), (1, 0)) and fair == (F(1, 2), F(1, 2))
    assert not common_argmins_exist(channel, sources, losses)
    # Every randomized decoder has profile (p,1-p), so max >= its mean 1/2.
    assert all(sum(r) == 1 for r in profiles) and sum(fair) == 1
    return {"oracle_envelope": list(oracle), "deterministic_profiles": profiles,
            "randomized_robust_minimum": F(1, 2), "deterministic_robust_minimum": 1,
            "oracle_jointly_attainable": False}


def exhaustive_common_argmin_check():
    # All 256 binary loss tables E x X x A, nine binary half-grid channels.
    sources = (((F(1, 3),), (F(2, 3),)), ((F(3, 4),), (F(1, 4),)))
    decoders = deterministic_decoders(2, 1)
    checked = unattainable = 0
    for values in product((0, 1), repeat=8):
        losses = tuple(tuple((tuple(values[e * 4 + x * 2:e * 4 + x * 2 + 2]),)
                             for x in range(2)) for e in range(2))
        for channel in binary_channels():
            envelope = oracle_envelope(channel, sources, losses)
            profiles = tuple(risk(channel, d, sources, losses) for d in decoders)
            actual = envelope in profiles
            assert tuple(min(row[e] for row in profiles) for e in range(2)) == envelope
            assert actual == common_argmins_exist(channel, sources, losses)
            assert all(all(row[e] >= envelope[e] for e in range(2)) for row in profiles)
            checked += 1
            unattainable += not actual
    return {"instances": checked, "oracle_envelope_unattainable_instances": unattainable}


def side_information_problem():
    sources = (((F(1, 2), F(0)), (F(1, 6), F(1, 3))),
               ((F(0), F(1, 4)), (F(1, 2), F(1, 4))))
    losses = tuple(tuple(tuple(tuple(int(a != (x ^ y ^ e)) for a in range(2))
                               for y in range(2)) for x in range(2)) for e in range(2))
    return sources, losses


def exhaustive_emulation_check():
    sources, losses = side_information_problem()
    decoders = tuple(decoder_rows(ps, 2, 2)
                     for ps in product((F(0), F(1, 2), F(1)), repeat=4))
    checked = 0
    for channel in binary_channels():
        for garbling in binary_channels():
            coarse = compose_channel(channel, garbling)
            for decoder in decoders:
                fine_decoder = compose_decoder(garbling, decoder)
                assert risk(channel, fine_decoder, sources, losses) == risk(coarse, decoder, sources, losses)
                assert all(sum(row) == 1 for rows in fine_decoder for row in rows)
                checked += 1
    return {"joint_profile_identities": checked, "ecologies_per_profile": 2,
            "side_information_values": 2}


def convex_hull_check():
    sources, losses = side_information_problem()
    channel = ((F(3, 4), F(1, 4)), (F(1, 3), F(2, 3)))
    assignments = tuple(product((0, 1), repeat=4))
    profiles = tuple(risk(channel, decoder_rows(bits, 2, 2), sources, losses)
                     for bits in assignments)
    checked = 0
    for probabilities in product((F(0), F(1, 2), F(1)), repeat=4):
        weights = []
        for bits in assignments:
            weight = F(1)
            for p, bit in zip(probabilities, bits):
                weight *= p if bit else 1 - p
            weights.append(weight)
        mixed = tuple(sum((w * row[e] for w, row in zip(weights, profiles)), F(0))
                      for e in range(2))
        assert sum(weights) == 1
        assert mixed == risk(channel, decoder_rows(probabilities, 2, 2), sources, losses)
        checked += 1
    return {"decoder_mixture_identities": checked, "deterministic_tables": 16}


def deterministic_class_boundary():
    channel = ((F(1), F(0)), (F(0), F(1)))
    garbling = ((F(1, 2), F(1, 2)),) * 2
    decoder = decoder_rows((F(0), F(1)), 2, 1)
    sources = (((F(1),), (F(0),)), ((F(0),), (F(1),)))
    losses = tuple(tuple(((int(0 != e), int(1 != e)),) for x in range(2)) for e in range(2))
    deterministic = {risk(channel, d, sources, losses) for d in deterministic_decoders(2, 1)}
    coarse_profile = risk(compose_channel(channel, garbling), decoder, sources, losses)
    assert coarse_profile == (F(1, 2), F(1, 2)) and coarse_profile not in deterministic
    assert risk(channel, compose_decoder(garbling, decoder), sources, losses) == coarse_profile
    return {"stochastic_garbling_requires_randomized_emulation": True,
            "deterministic_risk_set_inclusion_is_not_unconditional": True}


def run():
    return {"terminal": "GRAND_GMI_COMMON_DECODER_CORRECTION_GREEN_AT_FINITE_SCOPE",
            "determinism": "exhaustive/no-rng/exact-rational",
            "hidden_ecology": hidden_ecology_witness(),
            "argmin_criterion": exhaustive_common_argmin_check(),
            "garbling": exhaustive_emulation_check(),
            "convex_hull": convex_hull_check(),
            "decoder_class_boundary": deterministic_class_boundary(),
            "boundary": "finite mathematical witnesses; no empirical or unrestricted closure"}


def json_value(value):
    if isinstance(value, F):
        return int(value) if value.denominator == 1 else str(value)
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    print(json.dumps(run(), default=json_value, indent=2, sort_keys=True))
