"""Environment-first one-shot rewards; no implicit infinite reward stream."""


def action(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("binary integer action required")


def reward(target, action_history):
    action(target)
    if type(action_history) is not tuple:
        raise ValueError("canonical action history required")
    for value in action_history:
        action(value)
    return int(len(action_history) == 1 and action_history[0] == target)
