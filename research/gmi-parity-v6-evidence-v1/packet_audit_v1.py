"""Full static consistency audit of retained valid V6 packets; zero candidate calls."""
from __future__ import annotations
import copy
from authority_v1 import HERE, load_authority, packet_name, read_packet
from frozen_contract_v1 import AuditError, require, sha
from metadata_v1 import validate_metadata
from priming_v1 import validate_priming
from resource_evidence_v6 import opcode_contract, validate_resources

EXCLUSIONS = {
    "historical_host_authenticated": False,
    "historical_binary_authenticated": False,
    "historical_first_attempt_authenticated": False,
    "preregistration_temporal_priority_authenticated": False,
    "registered_expectation_truth_established": False,
    "population_or_cross_substrate_generalization": False,
}


def audit_content(packet, authority):
    try:
        binding, prereg, module = authority
        validate_metadata(packet, binding, prereg, module)
        instrument = packet["instrumentation"]
        require(type(instrument) is dict, "instrument must be an object")
        priming = validate_priming(instrument, opcode_contract(module))
        # The inherited resource core is byte-for-byte unchanged. Validate the two
        # V6 additions separately, then present precisely the original field set.
        measured = copy.deepcopy(packet)
        del measured["instrumentation"]["priming_witness_diagnostics"]
        del measured["instrumentation"]["priming_was_required_on_this_interpreter"]
        result = validate_resources(measured, module)
        return {"status": "COMPLETE_STATIC_V6_MEASURED_EVIDENCE_PASS", **result,
                "recorded_capability_cases": 32, "complete_recorded_frames": 64,
                "recorded_timed_blocks": 128, "recorded_timed_candidate_calls": 20480000,
                "priming": priming, "candidate_calls_executed": 0,
                "priming_calls_executed": 0, "timing_calls_executed": 0, **EXCLUSIONS}
    except (KeyError, TypeError, AttributeError, IndexError, ValueError) as exc:
        if isinstance(exc, AuditError):
            raise
        raise AuditError("malformed packet: " + str(exc)) from exc


def audit_retained(version, base=HERE):
    authority = load_authority(base)
    packet = read_packet(version, base)
    return {"packet": packet_name(version),
            "packet_sha256": sha((base / "raw/frozen" / packet_name(version)).read_bytes()),
            "python_version": version, **audit_content(packet, authority)}
