# G5.3 result

**Terminal:** `FACTORED_WARRANT_VALUE_SUPPORTED`

- Exhaustive n=3: 168/168 legal warrant intervals expand to the antichain oracle; revocation liveness matches.
- Lower and upper DAG roots remain distinct; upper-only evidence is tracked.
- Enumeration overflow is `CANNOT_CHECK_OUTPUT_SIZE`, not an approximation.
- Shared hash-cons compression is mixed (helps at n=6, not at n=8/10 versus summed antichain terms).
- ROBDD/ZDD left open; production `warrant.py` unchanged; no production adoption.
