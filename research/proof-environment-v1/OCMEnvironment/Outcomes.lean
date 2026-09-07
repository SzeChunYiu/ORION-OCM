namespace OCMEnvironment
-- A refusal of the registered policy/identity is distinct from an incomplete check.
-- REJECTED here never asserts that the theorem has no possible proof.
def refusalTerminal (reason : String) : String :=
  if #["EXCLUDED_DEPENDENCY", "UNREGISTERED_AXIOM", "INDEPENDENT_TARGET_MISMATCH",
       "PRIMITIVE_IDENTITY_MISMATCH", "REGISTERED_AXIOM_HEADER_MISMATCH",
       "REGISTERED_PRIMITIVE_MISMATCH"].any (fun code => reason.startsWith code) then "REJECTED"
  else "CANNOT_CHECK"
end OCMEnvironment
