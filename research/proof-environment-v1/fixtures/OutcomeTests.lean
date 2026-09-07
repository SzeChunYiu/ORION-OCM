import OCMEnvironment.Outcomes
open OCMEnvironment
def main : IO Unit := do
  for code in #["EXCLUDED_DEPENDENCY [target]", "UNREGISTERED_AXIOM A", "PRIMITIVE_IDENTITY_MISMATCH Nat", "INDEPENDENT_TARGET_MISMATCH"] do
    unless refusalTerminal code == "REJECTED" do throw <| IO.userError s!"policy denial misclassified {code}"
  for code in #["UNSAFE_OR_PARTIAL A", "DETERMINISTIC_TIMEOUT", "unknown infrastructure error"] do
    unless refusalTerminal code == "CANNOT_CHECK" do throw <| IO.userError s!"incomplete check misclassified {code}"
  IO.println "7 outcome controls PASS"
