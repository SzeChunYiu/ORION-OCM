;; PROVENANCE
;; domain:        Gripper
;; competition:   International Planning Competition, IPC-1 (1998), "Gripper"
;; basis:         transcribed from the standard IPC domain description
;;                (robot with two grippers moving balls between rooms; actions
;;                move/pick/drop, grippers as constants), structured by hand
;;                from the published semantics -- NOT verbatim IPC text.
;; subset:        types, constants, predicates, actions with delete/add effects
;;                only (no :derived, no :duration, no ADL, no conditional effects)
;; pipeline role: S1 external-authorship family domain (P1_PIPELINE_FREEZE_V1.json)

(define (domain gripper-strips)
  (:requirements :strips :typing)
  (:types location object gripper)
  (:constants left right - gripper)
  (:predicates (at-robby ?x - location)
               (at ?y - object ?x - location)
               (free ?g - gripper)
               (carry ?o - object ?g - gripper))
  (:action move
     :parameters (?l - location ?m - location)
     :precondition (at-robby ?l)
     :effect (and (at-robby ?m)
                  (not (at-robby ?l))))
  (:action pick
     :parameters (?o - object ?l - location ?g - gripper)
     :precondition (and (at ?o ?l) (at-robby ?l) (free ?g))
     :effect (and (carry ?o ?g)
                  (not (at ?o ?l))
                  (not (free ?g))))
  (:action drop
     :parameters (?o - object ?l - location ?g - gripper)
     :precondition (and (carry ?o ?g) (at-robby ?l))
     :effect (and (at ?o ?l)
                  (free ?g)
                  (not (carry ?o ?g)))))
