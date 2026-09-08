"""JSON Schema files exist and reject extra properties."""
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from g2_cognitive_objects.canonical import loads
from g2_cognitive_objects.fixture import frozen_fixture
from g2_cognitive_objects.schema import SCHEMA_DIR, ValidationError, validate_named
from g2_cognitive_objects.types import emit


REQUIRED_SCHEMAS = (
    "cognitive_episode_v1.json",
    "method_record_v1.json",
    "method_schema_v1.json",
    "reuse_event_v1.json",
    "failure_attempt_v1.json",
    "scope_transfer_v1.json",
    "representation_change_v1.json",
    "resource_vector.json",
    "acquisition_lineage.json",
    "usefulness_evidence.json",
    "correctness_evidence.json",
    "current_authorization_state.json",
    "common.json",
)


def test_required_schema_files_exist():
    for name in REQUIRED_SCHEMAS:
        assert (SCHEMA_DIR / name).is_file(), name


def test_extra_property_refused():
    raw = emit(frozen_fixture())
    data = loads(raw)
    data["extra"] = True
    with pytest.raises(ValidationError):
        validate_named(data, "episode_fixture_v1.json")


def test_nested_episode_schema():
    data = loads(emit(frozen_fixture()))
    validate_named(data["episode"], "cognitive_episode_v1.json")
    validate_named(data["method_record"], "method_record_v1.json")
    validate_named(data["reuse_event"], "reuse_event_v1.json")
    validate_named(data["failure_attempt"], "failure_attempt_v1.json")
    validate_named(data["scope_transfer"], "scope_transfer_v1.json")
    validate_named(data["representation_change"], "representation_change_v1.json")
    validate_named(data["episode"]["resources"], "resource_vector.json")
    validate_named(data["episode"]["acquisition_lineage"], "acquisition_lineage.json")
    validate_named(data["episode"]["correctness"], "correctness_evidence.json")
    validate_named(data["episode"]["usefulness"], "usefulness_evidence.json")
    validate_named(data["episode"]["authorization"], "current_authorization_state.json")
