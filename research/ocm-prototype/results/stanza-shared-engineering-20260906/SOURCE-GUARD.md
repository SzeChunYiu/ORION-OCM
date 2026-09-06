# Prospective source guard

The successor-plan preparation exposed one narrow omission: the capture recorded current source identity but
did not compare it with the prospective identity. The Stanza route now refuses a different source identity before
creating its output directory. The original UDPipe route is unchanged.

The control changes the prospective identity and verifies a refusal with no output directory.
The full scoped N1/G1 suite passed again:153 tests in20.93s, zero failures or skips.
Its exact log/XML are controls/prospective-source-guard.*; the earlier153-test records are retained.

The previously reviewed source is recoverable at commit eecb62aa522b5de3280c237dcbe1a200836692a6.
ARTIFACTS.json binds the current source; controls/review-ready.json remains the earlier review checkpoint.
The registered operator/checker source identity is checked by the capture. The separate launch/source manifest also
binds the capture, external grader and relevant data before the planned command.
No prediction or change to scoring, model weights, controller or scientific authority occurred.
