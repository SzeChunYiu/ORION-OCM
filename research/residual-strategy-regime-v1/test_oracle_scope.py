def test_action_set_expansion_can_strictly_beat_old_oracle():
    costs = {"inverse": 5.0, "semantic": 4.0, "partial_prebuild": 3.0}
    old_actions = ("inverse", "semantic")
    expanded_actions = old_actions + ("partial_prebuild",)
    old_oracle = min(costs[action] for action in old_actions)
    expanded_oracle = min(costs[action] for action in expanded_actions)
    assert expanded_oracle <= old_oracle
    assert expanded_oracle < old_oracle
