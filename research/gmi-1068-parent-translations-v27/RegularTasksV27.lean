import TaskInterfacesV27
namespace RegularTasksV27
open StochasticV14 TaskInterfacesV27
universe u
variable {X : Type u}
def Regular (r s : RelParentV27.Rel X X) := ∀ y,Ran r y→Dom s y
def regularTask (r s : RelParentV27.Rel X X) (h : Regular r s) :
    (category X).Hom (Dom r) (Ran s) :=
  (canonical r).comp (bridge h) |>.comp (canonical s)
theorem decode_regular (r s : RelParentV27.Rel X X) (h : Regular r s) :
    decode (regularTask r s h)=RelParentV27.comp r s := by
  funext x z; apply propext
  constructor
  · rintro ⟨hx,hz,y,⟨v,hr,he⟩,hs⟩
    change y=inclusion h v at he
    subst y
    exact ⟨v.val,hr,hs⟩
  · rintro ⟨y,hr,hs⟩
    refine ⟨⟨y,hr⟩,⟨y,hs⟩,⟨y,⟨z,hs⟩⟩,?_,hs⟩
    exact ⟨⟨y,⟨x,hr⟩⟩,hr,Subtype.ext rfl⟩
theorem regular_domain (r s : RelParentV27.Rel X X) (h : Regular r s) (x : X) :
    Dom (decode (regularTask r s h)) x ↔ Dom r x :=
  decoded_domain _ _
theorem regular_raw_domain (r s : RelParentV27.Rel X X) (h : Regular r s) (x : X) :
    Dom (RelParentV27.comp r s) x ↔ Dom r x := by
  rw [← decode_regular r s h]
  exact regular_domain r s h x
theorem range_comp_subset (r s : RelParentV27.Rel X X) (z : X) :
    Ran (RelParentV27.comp r s) z → Ran s z := by
  rintro ⟨x,y,_,hs⟩; exact ⟨y,hs⟩
theorem adjacent_regular (r s t : RelParentV27.Rel X X)
    (hrs : Regular r s) (hst : Regular s t) :
    Regular (RelParentV27.comp r s) t ∧ Regular r (RelParentV27.comp s t) := by
  constructor
  · intro z hz; exact hst z (range_comp_subset r s z hz)
  · intro z hz; exact (regular_raw_domain s t hst z).mpr (hrs z hz)
def R : RelParentV27.Rel (Fin 5) (Fin 5) := fun x y => x=0 ∧ y=1
def S : RelParentV27.Rel (Fin 5) (Fin 5) :=
  fun x y => (x=1 ∧ y=2) ∨ (x=3 ∧ y=4)
def T : RelParentV27.Rel (Fin 5) (Fin 5) := fun x y => x=2 ∧ y=2
theorem inferred_interface_failure :
    Regular R S ∧ Regular (RelParentV27.comp R S) T ∧ ¬Regular S T := by
  simp [Regular,Ran,Dom,RelParentV27.comp,R,S,T]
  exact ⟨4,⟨3,Or.inr ⟨rfl,rfl⟩⟩,by decide⟩
def restrictedInput : RelParentV27.Rel Bool Bool := fun x y => x=false ∧ y=false
def allIdentity : RelParentV27.Rel Bool Bool := fun x y => y=x
theorem declared_output_larger :
    Regular restrictedInput allIdentity ∧ Ran allIdentity true ∧
      ¬Ran (RelParentV27.comp restrictedInput allIdentity) true := by
  unfold Regular Ran Dom RelParentV27.comp restrictedInput allIdentity
  decide
end RegularTasksV27
