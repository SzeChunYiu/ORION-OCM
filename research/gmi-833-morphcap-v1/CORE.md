# gmi-833-morphcap-v1

Bounded #848 / #833-C foundation tranche for architecture-independent computational-mechanism equivalence and capability objects.

## Scope

- morphology equivalence = isomorphism of a registered architecture-name-free mechanism signature;
- legacy `machine species` = quotient class under that equivalence;
- capability = external task/verifier/resource functional, never an architecture label;
- capability ceiling = supremum over an externally defined admissible realization class;
- impossibility region = threshold above the ceiling or no feasible realization;
- exact two-world observational-aliasing ceiling `1/2`, revealed-information twin ceiling `1`.

## Reproduce

```bash
python3 -I -B research/gmi-833-morphcap-v1/test_morphcap_v1.py -v
python3 -I -O -B research/gmi-833-morphcap-v1/test_morphcap_v1.py -v
python3 -I -B research/gmi-833-morphcap-v1/morphcap_v1.py
```

Claim ceiling: `GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE`.

This does not re-prove the eleven historical capability ceilings; #833 Section K remains open for that work.
