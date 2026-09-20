import RelParentV27
import RestrictedV26
namespace TaskInterfacesV27
open TypedPathsV11 ProcessMapsV26 StochasticV14
universe u
abbrev Interface (X : Type u) := X → Prop
abbrev Carrier {X : Type u} (I : Interface X) := {x : X // I x}
def category (X : Type u) : Category (Interface X) where
  Hom I J := TotalRel (Carrier I) (Carrier J)
  id I := TotalRel.ident (Carrier I)
  comp := TotalRel.comp
  assoc := TotalRel.assoc
  left_id := TotalRel.left_id
  right_id := TotalRel.right_id
variable {X : Type u}
def decode {I J : Interface X} (t : (category X).Hom I J) : RelParentV27.Rel X X :=
  fun x y => ∃ hx : I x, ∃ hy : J y, t.relates ⟨x,hx⟩ ⟨y,hy⟩
def Dom (r : RelParentV27.Rel X X) : Interface X := fun x => ∃ y,r x y
def Ran (r : RelParentV27.Rel X X) : Interface X := fun y => ∃ x,r x y
theorem decoded_domain {I J : Interface X} (t : (category X).Hom I J) (x : X) :
    Dom (decode t) x ↔ I x := by
  constructor
  · rintro ⟨y,hx,_,_⟩; exact hx
  · intro hx
    obtain ⟨y,hy⟩ := t.total ⟨x,hx⟩
    exact ⟨y.val,hx,y.property,hy⟩
theorem decoded_range {I J : Interface X} (t : (category X).Hom I J) (y : X) :
    Ran (decode t) y → J y := by rintro ⟨x,_,hy,_⟩; exact hy
theorem decoded_comp {I J K : Interface X} (t : (category X).Hom I J)
    (s : (category X).Hom J K) :
    decode (TotalRel.comp t s)=RelParentV27.comp (decode t) (decode s) := by
  funext x z; apply propext
  constructor
  · rintro ⟨hx,hz,y,ht,hs⟩
    exact ⟨y.val,⟨hx,y.property,ht⟩,⟨y.property,hz,hs⟩⟩
  · rintro ⟨y,⟨hx,hy,ht⟩,⟨hy',hz,hs⟩⟩
    exact ⟨hx,hz,⟨y,hy⟩,ht,hs⟩
def canonical (r : RelParentV27.Rel X X) : (category X).Hom (Dom r) (Ran r) where
  relates x y := r x.val y.val
  total x := by
    obtain ⟨y,hy⟩ := x.property
    exact ⟨⟨y,x.val,hy⟩,hy⟩
theorem decode_canonical (r : RelParentV27.Rel X X) : decode (canonical r)=r := by
  funext x y; apply propext
  constructor
  · rintro ⟨_,_,h⟩; exact h
  · intro h; exact ⟨⟨y,h⟩,⟨x,h⟩,h⟩
def inclusion {I J : Interface X} (h : ∀ x,I x→J x) : Carrier I → Carrier J :=
  fun x => ⟨x.val,h x.val x.property⟩
def bridge {I J : Interface X} (h : ∀ x,I x→J x) : (category X).Hom I J :=
  TotalRel.graph (inclusion h)
theorem bridge_label {I J : Interface X} (h : ∀ x,I x→J x) (x : Carrier I) :
    (inclusion h x).val=x.val := rfl
def possible (P : {I J : Interface X} → (category X).Hom I J → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc (category X)) P) :
    Category (Interface X) := RestrictedV26.category (category X) P closed
theorem possible_hom (P : {I J : Interface X} → (category X).Hom I J → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc (category X)) P)
    (I J : Interface X) : (possible P closed).Hom I J={t : (category X).Hom I J // P t} := rfl
end TaskInterfacesV27
