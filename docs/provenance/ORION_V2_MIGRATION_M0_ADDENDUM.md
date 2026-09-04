# M0 dependency-closure addendum to ORION-V2 → ORION-OCM migration

The canonical historical source remains `SzeChunYiu/ORION-V2@42b1b0d1ab5920a69036e1c782c6b84c92c3b4d3`. The previously migrated `research/orion-machine/**` tree remains byte-frozen; M0 does not edit it.

M0 additionally materializes only dependencies needed to replay inherited controlled OCM evidence without an ORION-V2 checkout:

- exact frozen ORION-V2 modules required by inherited ME-X1/M4 controls as a minimal **PARENT_OWNED compatibility subset**, not active OCM architecture;
- frozen ME-X1 Python support modules required by M1/M2 historical replay;
- frozen protected ME-X3 Lean receipt consumed by M6a, without rerunning the protected campaign;
- byte-identical ORION-V2 `jump.py` in `src/ocm/kso/jump.py`, checked against the PARENT_OWNED copy.

The active package is `src/ocm/**`. The parent subset exists only for dependency closure and equivalence; it does not become OCM authority.

Scientific boundaries remain unchanged: M2 `PARENT_SUFFICIENT` stays `PARENT_SUFFICIENT`; M5 remains controlled codec chat; M6a remains verifier-channel integration with upstream `PARENT_SUFFICIENT`; recursive/language/wisdom/method objects remain candidate organizations; general novelty/superiority remains `NOT_ESTABLISHED`.
