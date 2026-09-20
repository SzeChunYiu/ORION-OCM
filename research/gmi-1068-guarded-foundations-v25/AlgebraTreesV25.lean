import TreeTransportV25
namespace AlgebraTreesV25
open PartialUnitsV19 BracketV25 BundledCategoryV19 ArrowRoundtripV19
universe u
variable {A : Type u} (P : Algebra A)
noncomputable def observer : Tree P.Unit A → Option A :=
  eval P.mul some (fun e => some e.val)
theorem unpack_identity (e : P.Unit) :
    unpack P (identity (ReconstructedV19.category P) e) = e.val := rfl
theorem unpack_response (t : Tree P.Unit (Bundled P)) :
    observer P (t.map id (unpack P)) =
    (CategoryTreesV25.observer (ReconstructedV19.category P) t).map (unpack P) :=
  TreeTransportV25.eval_transport (RoundtripResponsesV19.arrowIso P).symm id
    (identity (ReconstructedV19.category P)) Subtype.val (fun _ => rfl) t
theorem pack_identity (e : P.Unit) :
    identity (ReconstructedV19.category P) e = pack P e.val := by
  apply unpack_injective
  rfl
theorem pack_response (t : Tree P.Unit A) :
    CategoryTreesV25.observer (ReconstructedV19.category P) (t.map id (pack P)) =
    (observer P t).map (pack P) :=
  TreeTransportV25.eval_transport (RoundtripResponsesV19.arrowIso P) id
    Subtype.val (identity (ReconstructedV19.category P)) (pack_identity P) t
theorem raw_bridge (t : Tree P.Unit A) :
    observer P t =
    RawObserversV25.observer (PresentedUnitsV25.full P) (t.map Subtype.val id) := by
  rw [RawObserversV25.full_observer]
  induction t with
  | arrow a => rfl
  | empty e => simp [observer,eval,Tree.map,e.property]
  | seq l r hl hr =>
    simp only [observer,eval,Tree.map] at *
    rw [hl,hr]
theorem unpack_raw (t : Tree P.Unit (Bundled P)) :
    RawObserversV25.observer (PresentedUnitsV25.full P)
      ((t.map id (unpack P)).map Subtype.val id) =
    (CategoryTreesV25.observer (ReconstructedV19.category P) t).map (unpack P) := by
  rw [← raw_bridge,unpack_response]
theorem both_query_inverses (t : Tree P.Unit A) (q : Tree P.Unit (Bundled P)) :
    (t.map id (pack P)).map id (unpack P) = t ∧
    (q.map id (unpack P)).map id (pack P) = q :=
  ⟨map_map _ _ _ _ (fun _ => rfl) (unpack_pack P) t,
   map_map _ _ _ _ (fun _ => rfl) (pack_unpack P) q⟩
theorem same_guarded_word (s t : Tree P.Unit A)
    (h : flatten Subtype.val s = flatten Subtype.val t) :
    observer P s = observer P t := by
  rw [observer,OptionFoldV25.flatten_eval _ P.assoc,
    OptionFoldV25.flatten_eval _ P.assoc,h]
end AlgebraTreesV25
