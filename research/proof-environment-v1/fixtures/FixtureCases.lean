namespace Fixture
universe u
 theorem composition (P Q R : Prop) (f : P → Q) (g : Q → R) (p : P) : R := g (f p)
 theorem polymorphic {α : Sort u} (x : α) : x = x := rfl
 def identity {α : Type u} (x : α) : α := x
 theorem defined {α : Type u} (x : α) : identity x = x := rfl
 opaque opaqueIdentity {α : Type u} (x : α) : α := x
 theorem opaqueUse {α : Type u} (x : α) : opaqueIdentity x = opaqueIdentity x := rfl
 mutual
 inductive Tree where
   | leaf : Nat → Tree
   | branch : Forest → Tree
 inductive Forest where
   | nil : Forest
   | cons : Tree → Forest → Forest
 end
 def treeTag : Tree → Nat
   | .leaf _ => 0
   | .branch _ => 1
 theorem mutualRecursor (n : Nat) : treeTag (.leaf n) = 0 := rfl
 inductive Rose where
   | node : List Rose → Rose
 theorem nested (r : Rose) : r = r := rfl
 structure Box where
   n : Nat
   s : String
 theorem projection (b : Box) : b.n = b.n := rfl
 theorem naturalLiteral : (37 : Nat) = 37 := rfl
 theorem stringLiteral : ("mechanical" : String) = "mechanical" := rfl
 theorem quotient {α : Sort u} (r : α → α → Prop) (q : Quot r) : q = q := rfl
 axiom evidence : True
 opaque opaqueEvidence : True := evidence
 theorem opaqueAxiom : True := opaqueEvidence
 private def forbiddenCanary : String := "WITHHELD_PRIVATE_TABLE_CANARY_20260907"
 theorem privateProof (P : Prop) (h : P) : P := let _x := forbiddenCanary; h
 theorem aliasComposition (P Q R : Prop) (f : P → Q) (g : Q → R) (p : P) : R := composition P Q R f g p
end Fixture
