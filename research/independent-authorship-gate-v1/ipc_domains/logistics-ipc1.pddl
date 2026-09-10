;; PROVENANCE
;; domain:        Logistics
;; competition:   International Planning Competition, IPC-1 (1998) / IPC-2 (2000)
;; basis:         transcribed from the standard IPC domain description
;;                (packages/trucks within cities, airplanes between airports;
;;                actions load/unload for truck and plane, drive-truck,
;;                fly-airplane), structured by hand from the published
;;                semantics -- NOT verbatim IPC text. Predicate and parameter
;;                naming follows the all-positive STRIPS formulation (distinct
;;                truck-at/airplane-at/obj-at/obj-in predicates, city bound as
;;                an explicit drive-truck parameter) so that no negative
;;                precondition is required anywhere in the domain.
;; subset:        types, predicates, actions with delete/add effects only
;;                (no :derived, no :duration, no ADL, no conditional effects)
;; pipeline role: S1 external-authorship family domain (P1_PIPELINE_FREEZE_V1.json)

(define (domain logistics-strips)
  (:requirements :strips :typing)
  (:types truck airplane - vehicle
          package - physobj
          airport city - location
          location place physobj vehicle - object)
  (:predicates (in-city ?l - location ?c - city)
               (truck-at ?t - truck ?l - location)
               (airplane-at ?a - airplane ?l - airport)
               (obj-at ?p - package ?l - location)
               (obj-in ?p - package ?v - vehicle))
  (:action load-truck
     :parameters (?p - package ?t - truck ?l - location)
     :precondition (and (obj-at ?p ?l) (truck-at ?t ?l))
     :effect (and (not (obj-at ?p ?l))
                  (obj-in ?p ?t)))
  (:action unload-truck
     :parameters (?p - package ?t - truck ?l - location)
     :precondition (and (obj-in ?p ?t) (truck-at ?t ?l))
     :effect (and (not (obj-in ?p ?t))
                  (obj-at ?p ?l)))
  (:action load-plane
     :parameters (?p - package ?a - airplane ?l - airport)
     :precondition (and (obj-at ?p ?l) (airplane-at ?a ?l))
     :effect (and (not (obj-at ?p ?l))
                  (obj-in ?p ?a)))
  (:action unload-plane
     :parameters (?p - package ?a - airplane ?l - airport)
     :precondition (and (obj-in ?p ?a) (airplane-at ?a ?l))
     :effect (and (not (obj-in ?p ?a))
                  (obj-at ?p ?l)))
  (:action drive-truck
     :parameters (?t - truck ?from - location ?to - location ?c - city)
     :precondition (and (truck-at ?t ?from)
                        (in-city ?from ?c)
                        (in-city ?to ?c))
     :effect (and (not (truck-at ?t ?from))
                  (truck-at ?t ?to)))
  (:action fly-airplane
     :parameters (?a - airplane ?from - airport ?to - airport)
     :precondition (airplane-at ?a ?from)
     :effect (and (not (airplane-at ?a ?from))
                  (airplane-at ?a ?to))))
