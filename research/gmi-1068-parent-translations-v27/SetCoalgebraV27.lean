import RawTransportV26
import LTSCoalgebraV27
namespace SetCoalgebraV27
open TypedPathsV11 ProcessMapsV26
universe u
structure SetEndo where
  obj : Type u → Type u
  map : {X Y : Type u} → (X → Y) → obj X → obj Y
  map_id : ∀ X, map (id : X → X)=id
  map_comp : ∀ {X Y Z : Type u} (f : X → Y) (g : Y → Z), map (g ∘ f)=map g ∘ map f
structure System (F : SetEndo.{u}) where
  carrier : Type u
  step : carrier → F.obj carrier
def Hom (F : SetEndo.{u}) (S T : System F) :=
  {f : S.carrier → T.carrier // ∀ s,F.map f (S.step s)=T.step (f s)}
def ident (F : SetEndo.{u}) (S : System F) : Hom F S S :=
  ⟨id,fun s => by rw [F.map_id]; rfl⟩
def comp {F : SetEndo.{u}} {S T U : System F} (f : Hom F S T) (g : Hom F T U) : Hom F S U :=
  ⟨g.val ∘ f.val,by
    intro s
    change F.map (g.val ∘ f.val) (S.step s)=U.step (g.val (f.val s))
    rw [F.map_comp]
    change F.map g.val (F.map f.val (S.step s))=_
    rw [f.property s,g.property (f.val s)]⟩
def category (F : SetEndo.{u}) : Category (System F) where
  Hom := Hom F
  id := ident F
  comp := comp
  assoc _ _ _ := Subtype.ext rfl
  left_id _ := Subtype.ext rfl
  right_id _ := Subtype.ext rfl
def functions : Category (Type u) where
  Hom X Y := X → Y
  id _ := id
  comp f g := g ∘ f
  assoc _ _ _ := rfl
  left_id _ := rfl
  right_id _ := rfl
def forget (F : SetEndo.{u}) : ProcessMap (category F) functions where
  obj := System.carrier
  hom := Subtype.val
  id_law _ := rfl
  comp_law _ _ := rfl
theorem forget_faithful (F : SetEndo.{u}) : (forget F).Faithful := by
  intro S T f g h
  exact Subtype.ext h
def tagged (F : SetEndo.{u}) : Category (System F) where
  Hom S T := S.carrier → T.carrier
  id _ := id
  comp f g := g ∘ f
  assoc _ _ _ := rfl
  left_id _ := rfl
  right_id _ := rfl
def taggedForget (F : SetEndo.{u}) : ProcessMap (category F) (tagged F) where
  obj := id
  hom := Subtype.val
  id_law _ := rfl
  comp_law _ _ := rfl
theorem tagged_object_injective (F : SetEndo.{u}) : (taggedForget F).ObjectInjective :=
  fun _ _ h => h
theorem tagged_raw_transport (F : SetEndo.{u}) : RawTransportV26.TreesCommute (taggedForget F) :=
  RawTransportV26.trees_of_injective _ (tagged_object_injective F)
def power (A : Type u) : SetEndo.{u} where
  obj X := (A×X) → Prop
  map := LTSCoalgebraV27.powerMap
  map_id X := funext (LTSCoalgebraV27.power_id (S:=X))
  map_comp f g := funext (LTSCoalgebraV27.power_comp f g)
def fromLTS {S A : Type u} (r : LTSCoalgebraV27.LTS S A) : System (power A) :=
  ⟨S,LTSCoalgebraV27.successors r⟩
theorem lts_hom_iff {S T A : Type u} (r : LTSCoalgebraV27.LTS S A)
    (q : LTSCoalgebraV27.LTS T A) (f : S → T) :
    (∃ h : Hom (power A) (fromLTS r) (fromLTS q), h.val=f) ↔
      LTSCoalgebraV27.Forward r q f ∧ LTSCoalgebraV27.Back r q f := by
  rw [← LTSCoalgebraV27.hom_iff]
  constructor
  · rintro ⟨h,rfl⟩
    intro s; funext p
    exact congrFun (h.property s) p
  · intro h
    exact ⟨⟨f,fun s => h s⟩,rfl⟩
end SetCoalgebraV27
