;; PROVENANCE
;; domain:        BLOCKS (blocksworld)
;; competition:   International Planning Competition, IPC-2 (2000), "Blocks World"
;; basis:         transcribed from the standard IPC domain description
;;                (typed STRIPS blocks world; actions pick-up/put-down/stack/unstack),
;;                structured by hand from the published semantics -- NOT verbatim
;;                IPC text; no IPC file was copied byte-for-byte.
;; subset:        types, predicates, actions with delete/add effects only
;;                (no :derived, no :duration, no ADL, no conditional effects)
;; pipeline role: S1 external-authorship family domain (P1_PIPELINE_FREEZE_V1.json)

(define (domain blocks-strips)
  (:requirements :strips :typing)
  (:types block)
  (:predicates (on ?x - block ?y - block)
               (ontable ?x - block)
               (clear ?x - block)
               (handempty)
               (holding ?x - block))
  (:action pick-up
     :parameters (?x - block)
     :precondition (and (clear ?x) (ontable ?x) (handempty))
     :effect (and (not (ontable ?x))
                  (not (clear ?x))
                  (not (handempty))
                  (holding ?x)))
  (:action put-down
     :parameters (?x - block)
     :precondition (holding ?x)
     :effect (and (not (holding ?x))
                  (clear ?x)
                  (handempty)
                  (ontable ?x)))
  (:action stack
     :parameters (?x - block ?y - block)
     :precondition (and (holding ?x) (clear ?y))
     :effect (and (not (holding ?x))
                  (not (clear ?y))
                  (clear ?x)
                  (handempty)
                  (on ?x ?y)))
  (:action unstack
     :parameters (?x - block ?y - block)
     :precondition (and (on ?x ?y) (clear ?x) (handempty))
     :effect (and (holding ?x)
                  (clear ?y)
                  (not (on ?x ?y))
                  (not (clear ?x))
                  (not (handempty)))))
