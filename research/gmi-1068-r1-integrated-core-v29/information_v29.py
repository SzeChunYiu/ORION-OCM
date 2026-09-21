"""Declared finite response families and explicit attained-image codebooks."""
from dataclasses import dataclass
from core_v29 import index, nat, need, semantic, tup, typed_key


@dataclass(frozen=True)
class Family:
    model_count: int
    query_count: int
    output_count: int
    responses: tuple

    def __post_init__(self):
        for size in (self.model_count, self.query_count, self.output_count):
            nat(size)
        tup(self.responses)
        need(len(self.responses) == self.model_count, "model count mismatch")
        for row in self.responses:
            tup(row)
            need(len(row) == self.query_count, "query count mismatch")
            for value in row:
                if value is not None:
                    index(value, self.output_count)


def checked_family(family):
    need(type(family) is Family, "actual Family required")
    family.__post_init__()
    return family


def attained_recovery(codes, observations):
    tup(codes)
    tup(observations)
    need(len(codes) == len(observations), "model domains differ")
    for code in codes:
        nat(code)
    codebook, labels = [], []
    for row in observations:
        tup(row)
        for value in row:
            if value is not None:
                nat(value)
        if row not in codebook:
            codebook.append(row)
        labels.append(codebook.index(row))
    labels = tuple(labels)
    decoder = semantic.decoder(codes, labels)
    if decoder is not None:
        need(semantic.verify_decoder(codes, labels, decoder), "attained decoder failed")
    return {"code_labels": codes, "response_codebook": tuple(codebook),
            "response_labels": labels, "decoder": decoder,
            "recoverable": decoder is not None}


def transport_report(source, target, query_map, output_map, codes):
    checked_family(source)
    checked_family(target)
    need(source.model_count == target.model_count, "common model domain required")
    tup(query_map)
    tup(output_map)
    need(len(query_map) == source.query_count, "total query map required")
    need(len(output_map) == source.output_count, "total output map required")
    for query in query_map:
        index(query, target.query_count)
    for output in output_map:
        index(output, target.output_count)
    restricted = tuple(tuple(row[q] for q in query_map) for row in target.responses)
    mapped = tuple(tuple(None if value is None else output_map[value] for value in row)
                   for row in source.responses)
    source_recovery = attained_recovery(codes, source.responses)
    restricted_recovery = attained_recovery(codes, restricted)
    full_recovery = attained_recovery(codes, target.responses)
    return {"commutes": mapped == restricted,
            "output_injective": len(set(output_map)) == len(output_map),
            "source_recoverable": source_recovery["recoverable"],
            "restricted_target_recoverable": restricted_recovery["recoverable"],
            "full_target_recoverable": full_recovery["recoverable"],
            "source_recovery": source_recovery,
            "restricted_target_recovery": restricted_recovery,
            "full_target_recovery": full_recovery}


def verify_transport_report(source, target, query_map, output_map, codes, certificate):
    need(type(certificate) is dict, "report dictionary required")
    expected = transport_report(source, target, query_map, output_map, codes)
    need(typed_key(certificate) == typed_key(expected), "transport report drift")
    return True
