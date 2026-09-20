import InterchangeV13
namespace OptionalV13

abbrev DiscreteHom (a b : BitProc) := a=b
def discreteId (a : BitProc) : DiscreteHom a a := rfl
def discreteComp {a b c : BitProc} (f : DiscreteHom a b) (g : DiscreteHom b c) :
    DiscreteHom a c := f.trans g
def discreteTensor {a b c d : BitProc} (f : DiscreteHom a b) (g : DiscreteHom c d) :
    DiscreteHom (sequence a c) (sequence b d) := by cases f; cases g; rfl

theorem discrete_assoc {a b c d : BitProc}
    (f : DiscreteHom a b) (g : DiscreteHom b c) (h : DiscreteHom c d) :
    discreteComp (discreteComp f g) h = discreteComp f (discreteComp g h) := rfl

theorem discrete_left {a b : BitProc} (f : DiscreteHom a b) :
    discreteComp (discreteId a) f = f := rfl
theorem discrete_right {a b : BitProc} (f : DiscreteHom a b) :
    discreteComp f (discreteId b) = f := rfl

theorem discrete_tensor_interchange {a b c d e f : BitProc}
    (p : DiscreteHom a b) (q : DiscreteHom b c)
    (r : DiscreteHom d e) (s : DiscreteHom e f) :
    discreteTensor (discreteComp p q) (discreteComp r s) =
      discreteComp (discreteTensor p r) (discreteTensor q s) := rfl

def discreteAssociator (a b c : BitProc) :
    DiscreteHom (sequence (sequence a b) c) (sequence a (sequence b c)) :=
  sequence_assoc a b c

def discreteLeftUnitor (a : BitProc) : DiscreteHom (sequence .identity a) a :=
  sequence_left a
def discreteRightUnitor (a : BitProc) : DiscreteHom (sequence a .identity) a :=
  sequence_right a

/-- Any two parallel structural composites agree in the discrete category. -/
theorem discrete_coherence {a b : BitProc} (f g : DiscreteHom a b) : f=g := rfl

theorem no_discrete_braiding :
    ¬ ∀ a b, DiscreteHom (sequence a b) (sequence b a) := by
  intro h
  exact resets_noncommute (h .reset0 .reset1)

end OptionalV13
