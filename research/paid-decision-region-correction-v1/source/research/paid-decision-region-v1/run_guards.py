"""Pure runner admission guards; no donor imports."""


def require_zero_maintenance(full, short):
    if type(full) is not int or type(short) is not int:
        raise TypeError("maintenance counters must be built-in integers")
    if full != 0 or short != 0:
        raise AssertionError("short-circuit parent unexpectedly introduced maintenance")
