"""Run the committed fetcher ``fetch_posterior_sources_v1.py`` (commit 2a)
UNCHANGED, with one runtime override: the User-Agent contact.

The committed constant carried a personal e-mail address.  This lane does not
send that address to a third party, so the contact is replaced by the public
repository URL before the fetch starts.  The rule PS-1, the admission test and
every recorded field are the committed fetcher's own; the record's
``user_agent`` field reflects the header actually sent.

Usage (laptop-billy, once, after the freeze commit):
  python3 -B run_fetch_v1.py --freeze-time 2026-09-19T07:16:31Z \
      --freeze-commit 233bb38a504f7ba10a1a75578840c0416b2e5c0d \
      --sources-dir /home/billy/ocm-scratch/revive-kl/sources --k 6
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import fetch_posterior_sources_v1 as fetcher  # noqa: E402

fetcher.UA = ("ORION-OCM-833-revive-kl/1.0 (research custody of posterior-dated sources; "
              "https://github.com/SzeChunYiu/ORION-OCM)")

if __name__ == "__main__":
    fetcher.main(sys.argv[1:])
