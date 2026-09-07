"""Plain metadata is checked before Python comparison hooks can run."""
import pytest
from unary_test_support import api, statement as s, task


def replacement(value, kind, calls):
    class PlainSubclass(str):
        pass

    class ComparisonHook(str):
        def __eq__(self, other):
            calls.append("eq")
            return super().__eq__(other)

        def __ne__(self, other):
            calls.append("ne")
            return super().__ne__(other)

    return (PlainSubclass if kind == "subclass" else ComparisonHook)(value)


def example(status):
    if status == "INCONSISTENT":
        return task([s("some"), s("no")], s("every"))
    if status == "ENTAILED":
        return task([], s("every", "A", "A"))
    if status == "CONTRADICTED":
        return task([], s("some", "A", ["not", ["pred", "A"]]))
    return task([], s("some"))


@pytest.mark.parametrize("kind", ["subclass", "hook"])
def test_task_schema_rejects_nonplain_strings_before_comparison(kind):
    contract = api("unary_contract")
    value = example("UNKNOWN")
    assert contract.validate_task(value) == value
    calls = []
    value["schema"] = replacement(value["schema"], kind, calls)
    with pytest.raises(contract.InputRefused, match="UNKNOWN_SCHEMA"):
        contract.validate_task(value)
    assert calls == []


@pytest.mark.parametrize("kind", ["subclass", "hook"])
@pytest.mark.parametrize("field", ["schema", "task_sha256", "status"])
@pytest.mark.parametrize("status", ["ENTAILED", "CONTRADICTED", "UNKNOWN", "INCONSISTENT"])
def test_result_metadata_rejects_nonplain_strings_before_comparison(kind, field, status):
    value = example(status)
    result = api("unary_solver").solve(value)
    verifier = api("unary_verify")
    assert result["status"] == status and verifier.verify_result(value, result)
    calls = []
    result[field] = replacement(result[field], kind, calls)
    accepted = verifier.verify_result(value, result)
    assert calls == []
    assert not accepted
