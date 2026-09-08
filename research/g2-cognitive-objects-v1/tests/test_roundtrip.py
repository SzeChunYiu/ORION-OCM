"""Round-trip the frozen G2.1 episode fixture through dataclasses and JSON Schema."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from g2_cognitive_objects.canonical import loads
from g2_cognitive_objects.fixture import frozen_fixture
from g2_cognitive_objects.schema import validate_named
from g2_cognitive_objects.types import EpisodeFixtureV1, emit, parse

EXAMPLES = HERE / "examples"
FROZEN = EXAMPLES / "frozen_episode.json"


def test_frozen_episode_round_trips():
    original = frozen_fixture()
    raw = emit(original)
    loaded = parse(EpisodeFixtureV1, raw)
    assert emit(loaded) == raw
    validate_named(loads(raw), "episode_fixture_v1.json")
    assert loaded.claim_authority == "SCHEMA_TRANSPORT_ONLY"
    assert loaded.reuse_event.g24.complete is False
    assert loaded.episode.correctness.independent_of_usefulness is True
    assert loaded.episode.usefulness.independent_of_correctness is True
    assert loaded.episode.usefulness.status.value == "CANNOT_CHECK"
    assert loaded.method_record.authorization.serving_liveness.value == "LIVE"
    assert loaded.failure_attempt.authorization.proof_liveness.value == "LIVE"
    assert loaded.failure_attempt.authorization.serving_liveness.value == "DEAD"


def test_checked_in_frozen_file_matches_emitter():
    expected = emit(frozen_fixture())
    assert FROZEN.is_file(), "examples/frozen_episode.json must be emitted and checked in"
    on_disk = FROZEN.read_bytes()
    assert on_disk == expected
    again = parse(EpisodeFixtureV1, on_disk)
    assert emit(again) == on_disk
    validate_named(loads(on_disk), "episode_fixture_v1.json")
