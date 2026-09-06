import Target

set_option linter.unusedVariables false
set_option linter.defProp false

namespace OCMMechanicalProof
def proposed :=
  (@Eq.{1})

theorem constructed : F0Target.statement := @proposed
end OCMMechanicalProof

#print axioms OCMMechanicalProof.constructed
