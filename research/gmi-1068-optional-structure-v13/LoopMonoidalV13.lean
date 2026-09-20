import InterchangeV13
namespace OptionalV13

/-- The product of the discrete object monoid with the one-object C2 category. -/
structure LoopHom (a b : BitProc) where
  endpoints : a=b
  bit : Bool

namespace LoopHom
@[ext] theorem ext {a b : BitProc} {f g : LoopHom a b} (h : f.bit=g.bit) : f=g := by
  cases f; cases g
  cases h
  rfl

def ident (a : BitProc) : LoopHom a a := ⟨rfl,false⟩
def comp {a b c : BitProc} (f : LoopHom a b) (g : LoopHom b c) : LoopHom a c :=
  ⟨f.endpoints.trans g.endpoints, Bool.xor f.bit g.bit⟩
def tensor {a b c d : BitProc} (f : LoopHom a b) (g : LoopHom c d) :
    LoopHom (sequence a c) (sequence b d) :=
  ⟨(congrArg (fun x => sequence x c) f.endpoints).trans (congrArg (sequence b) g.endpoints), Bool.xor f.bit g.bit⟩

theorem comp_assoc {a b c d : BitProc}
    (f : LoopHom a b) (g : LoopHom b c) (h : LoopHom c d) :
    comp (comp f g) h = comp f (comp g h) := by
  apply ext
  change Bool.xor (Bool.xor f.bit g.bit) h.bit = Bool.xor f.bit (Bool.xor g.bit h.bit)
  cases f.bit <;> cases g.bit <;> cases h.bit <;> decide

theorem left_id {a b : BitProc} (f : LoopHom a b) : comp (ident a) f=f := by
  apply ext
  change Bool.xor false f.bit = f.bit
  cases f.bit <;> rfl
theorem right_id {a b : BitProc} (f : LoopHom a b) : comp f (ident b)=f := by
  apply ext
  change Bool.xor f.bit false = f.bit
  cases f.bit <;> rfl

theorem tensor_ident (a b : BitProc) : tensor (ident a) (ident b) = ident (sequence a b) := rfl

theorem tensor_interchange {a b c d e f : BitProc}
    (p : LoopHom a b) (q : LoopHom b c) (r : LoopHom d e) (s : LoopHom e f) :
    tensor (comp p q) (comp r s) = comp (tensor p r) (tensor q s) := by
  apply ext
  exact xor_interchange p.bit q.bit r.bit s.bit

def structural {a b : BitProc} (h : a=b) : LoopHom a b := ⟨h,false⟩
def associator (a b c : BitProc) :
    LoopHom (sequence (sequence a b) c) (sequence a (sequence b c)) :=
  structural (sequence_assoc a b c)
def leftUnitor (a : BitProc) : LoopHom (sequence .identity a) a :=
  structural (sequence_left a)
def rightUnitor (a : BitProc) : LoopHom (sequence a .identity) a :=
  structural (sequence_right a)

theorem structural_inverse {a b : BitProc} (h : a=b) :
    comp (structural h) (structural h.symm) = ident a ∧
    comp (structural h.symm) (structural h) = ident b := ⟨rfl,rfl⟩

theorem associator_natural {a b c d e f : BitProc}
    (p : LoopHom a d) (q : LoopHom b e) (r : LoopHom c f) :
    comp (tensor (tensor p q) r) (associator d e f) =
      comp (associator a b c) (tensor p (tensor q r)) := by
  apply ext
  change Bool.xor (Bool.xor (Bool.xor p.bit q.bit) r.bit) false =
    Bool.xor false (Bool.xor p.bit (Bool.xor q.bit r.bit))
  cases p.bit <;> cases q.bit <;> cases r.bit <;> rfl

theorem leftUnitor_natural {a b : BitProc} (f : LoopHom a b) :
    comp (tensor (ident .identity) f) (leftUnitor b) = comp (leftUnitor a) f := by
  apply ext
  change Bool.xor (Bool.xor false f.bit) false = Bool.xor false f.bit
  cases f.bit <;> rfl

theorem rightUnitor_natural {a b : BitProc} (f : LoopHom a b) :
    comp (tensor f (ident .identity)) (rightUnitor b) = comp (rightUnitor a) f := by
  apply ext
  change Bool.xor (Bool.xor f.bit false) false = Bool.xor false f.bit
  cases f.bit <;> rfl

theorem pentagon (a b c d : BitProc) :
    comp (associator (sequence a b) c d) (associator a b (sequence c d)) =
      comp (comp (tensor (associator a b c) (ident d))
        (associator a (sequence b c) d))
        (tensor (ident a) (associator b c d)) := rfl

theorem triangle (a b : BitProc) :
    comp (associator a .identity b) (tensor (ident a) (leftUnitor b)) =
      tensor (rightUnitor a) (ident b) := rfl

def toggle (a : BitProc) : LoopHom a a := ⟨rfl,true⟩
theorem toggle_nonidentity (a : BitProc) : toggle a ≠ ident a := by
  intro h
  have hb := congrArg LoopHom.bit h
  exact Bool.noConfusion hb

theorem toggle_involution (a : BitProc) : comp (toggle a) (toggle a) = ident a := rfl

theorem no_cross_hom {a b : BitProc} (h : a≠b) : ¬ Nonempty (LoopHom a b) := by
  rintro ⟨f⟩
  exact h f.endpoints

theorem no_braiding_component :
    ¬ Nonempty (LoopHom (sequence .reset0 .reset1) (sequence .reset1 .reset0)) :=
  no_cross_hom resets_noncommute

theorem no_braiding :
    ¬ ∀ a b, Nonempty (LoopHom (sequence a b) (sequence b a)) := by
  intro h
  exact no_braiding_component (h .reset0 .reset1)
end LoopHom
end OptionalV13
