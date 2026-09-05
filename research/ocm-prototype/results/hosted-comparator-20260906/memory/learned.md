# Learned Notes

## Language lessons

- Evidence L1: In the taught clause order, the first noun phrase is the subject/agent, the second noun phrase is the object/patient, and the final past-tense verb supplies the verb and tense.
- Evidence L2: `dax` means `cat`.
- Evidence L3: `crate` means `parcel`.
- Evidence L4: `lifted` is the past tense of `lift`.

## Verified procedures

- Evidence C1: For coefficients `0,2,1` (constant first), the verified program is `inc,square,dec`.
  This computes `(x + 1)^2 - 1 = x^2 + 2*x`.
  Checker command: `python3 tools/check_polynomial.py --program inc,square,dec --coefficients 0,2,1`.
  Checker result: `identity_verified=true`.
