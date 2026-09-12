import json

import gmi_k4d_worlds as w


def test_all_22_generators_replay_and_seed_changes_world():
    rows=w.validate_all(seed=12345,scale=1)
    assert len(rows)==22
    assert {r["family_id"] for r in rows}==set(w.FAMILY_IDS)
    assert all(r["fingerprint"]!=r["next_seed_fingerprint"] for r in rows)


def test_query_complete_algorithmic_calibrations_have_no_fake_development_channel():
    for fid in ("K4-A05","K4-A06","K4-A17"):
        x=w.generate(fid,77,1)
        assert x["development"]==[]
        assert x["target_information_source"]==["QUERY"]
        assert x["queries"]
        assert x["verifier"] is not None


def test_external_authority_world_uses_authority_not_hidden_development():
    x=w.generate("K4-A14",88,2)
    assert x["development"]==[]
    assert x["authority"] and x["authority"]["records"]
    assert set(x["target_information_source"])=={"QUERY","EXTERNAL_AUTHORITY"}
    for q,y in zip(x["queries"],x["expected"]):
        assert x["authority"]["records"][q]==y


def test_learning_families_have_development_evidence_and_held_queries():
    query_only={"K4-A05","K4-A06","K4-A14","K4-A17"}
    for fid in w.FAMILY_IDS:
        x=w.generate(fid,99,1)
        assert x["queries"]
        if fid not in query_only:
            assert x["development"], fid
            assert "DEVELOPMENT" in x["target_information_source"], fid


def test_no_historical_architecture_names_in_world_schema():
    surface=json.dumps([w.generate(fid,101,1) for fid in w.FAMILY_IDS],sort_keys=True).lower()
    for banned in ("transformer","mixture of experts","mixture_of_experts","cnn","lstm","rag","knn"):
        assert banned not in surface


def test_world_fingerprint_commits_to_expected_outputs_and_information_channels():
    x=w.generate("K4-A01",111,1)
    y=json.loads(json.dumps(x))
    y["expected"][0]+=1
    old=y.pop("world_fingerprint")
    assert w._fp(y)!=x["world_fingerprint"]
    z=json.loads(json.dumps(x));z["target_information_source"]=["QUERY"]
    z.pop("world_fingerprint")
    assert w._fp(z)!=x["world_fingerprint"]
