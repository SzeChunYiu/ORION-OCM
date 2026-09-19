universe u v

structure ProcCat where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : (A : Obj) → Hom A A
  comp : {A B C : Obj} → Hom A B → Hom B C → Hom A C
  assoc :
    {A B C D : Obj} →
    (f : Hom A B) → (g : Hom B C) → (h : Hom C D) →
    comp (comp f g) h = comp f (comp g h)
  id_left :
    {A B : Obj} → (f : Hom A B) →
    comp (id A) f = f
  id_right :
    {A B : Obj} → (f : Hom A B) →
    comp f (id B) = f

namespace ProcCat

variable {C : ProcCat}

theorem history3_bracketing
    {A B C₁ D : C.Obj}
    (f : C.Hom A B) (g : C.Hom B C₁) (h : C.Hom C₁ D) :
    C.comp (C.comp f g) h = C.comp f (C.comp g h) :=
  C.assoc f g h

theorem prepend_no_change
    {A B : C.Obj} (f : C.Hom A B) :
    C.comp (C.id A) f = f :=
  C.id_left f

theorem append_no_change
    {A B : C.Obj} (f : C.Hom A B) :
    C.comp f (C.id B) = f :=
  C.id_right f

end ProcCat
