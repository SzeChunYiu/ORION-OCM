# Existing native route and its limits

Pinned donor: cvc5 1.3.4, release commit
`f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341`.
This is source-based rationale; it does not identify a measured internal timeout.

- [Default grammar construction](https://github.com/cvc5/cvc5/blob/f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341/src/theory/quantifiers/sygus/sygus_grammar_cons.cpp#L37)
  resolves with allowAny=true. Explicit API grammar resolution uses false by
  default, even when all printed productions match.
- [Single-invocation initialization](https://github.com/cvc5/cvc5/blob/f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341/src/theory/quantifiers/sygus/ce_guided_single_inv.cpp#L116)
  disables mode use on syntax-restricted problems; all avoids that exclusion.
- [Registered native options](https://github.com/cvc5/cvc5/blob/f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341/src/options/quantifiers_options.toml#L1009)
  define single-invocation all and strict reconstruction all. Reconstruction
  none can violate grammar restrictions and is not part of this proposal.
- [Actual reconstruction](https://github.com/cvc5/cvc5/blob/f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341/src/theory/quantifiers/sygus/ce_guided_single_inv.cpp#L454)
  invokes the existing reconstruction algorithm for restricted syntax. Its work
  stays charged; strict reconstruction need not finish within the envelope.
- [Default terminal sources](https://github.com/cvc5/cvc5/blob/f3b21c4483d3b88dc63cb7cd3e5eb092eee5e341/src/theory/quantifiers/sygus/embedding_converter.cpp#L143)
  are relevant arguments and collected conjecture constants. Merely declaring
  an unused helper beside this implicit first-order task does not add a learned
  production. No get-default/append-to-implicit public API was identified in
  the pinned Python synthesis/grammar surface.

The chosen intervention reuses a supported native solver mode; it adds no
solver, tracing system or altered correctness criterion. Returned derivation
membership can arise during reconstruction and does not establish causal search
guidance. No macro, learning, later transfer or efficiency claim is assigned.
