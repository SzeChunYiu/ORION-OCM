"""Attained-image recovery with exposed, type-sensitive observation codebooks."""
from dataclasses import dataclass
from core_v28 import need, semantic, tup, typed_key


def encode(values):
    tup(values)
    keys, codes, labels = {}, [], []
    for value in values:
        key = typed_key(value)
        if key not in keys:
            keys[key] = len(codes)
            codes.append(value)
        labels.append(keys[key])
    return tuple(codes), tuple(labels)


@dataclass(frozen=True)
class Recovery:
    observation_codes: tuple
    target_codes: tuple
    observation_labels: tuple
    target_labels: tuple
    decoder: dict


def recovery(observations, targets):
    tup(observations)
    tup(targets)
    need(len(observations) == len(targets), "model domains differ")
    observation_codes, observation_labels = encode(observations)
    target_codes, target_labels = encode(targets)
    decoder = semantic.decoder(observation_labels, target_labels)
    if decoder is None:
        return None
    return Recovery(observation_codes, target_codes, observation_labels, target_labels, decoder)


def verify_recovery(observations, targets, certificate):
    tup(observations)
    tup(targets)
    need(len(observations) == len(targets), "model domains differ")
    need(type(certificate) is Recovery, "Recovery certificate required")
    expected_o, labels_o = encode(observations)
    expected_t, labels_t = encode(targets)
    for actual, expected in ((certificate.observation_codes, expected_o), (certificate.target_codes, expected_t),
                             (certificate.observation_labels, labels_o), (certificate.target_labels, labels_t)):
        need(typed_key(actual) == typed_key(expected), "typed codebook or label drift")
    return semantic.verify_decoder(labels_o, labels_t, certificate.decoder)
