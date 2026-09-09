# Evidence layout

Start with [CORE](CORE.md). The [outcome review](review/outcome/REVIEW.json) is the
current result authority; earlier source reviews remain scoped to source readiness.

- [RESULT](records/result/RESULT.json): all 76 rows plus retained prior costs.
- [RAW.zip](RAW.zip): every new SCREEN output, full wiring/control histories,
  process records, source/outcome reviews and both binder generations.
- [RAW-MEMBERS](RAW-MEMBERS.json): each archived member's original path and digest.
- [COPY-MANIFEST](COPY-MANIFEST.json): exact direct copies; [FILES](FILES.json):
  every public file except FILES itself.
- [UPSTREAM](UPSTREAM.json): immutable PR164/166/188/190 archive and member pins for
  unchanged P1, prior outcomes, cache modules, Lark runtime/license and reviews.

No giant prior input/runtime tree or stdlib sources are duplicated. The ten
inherited current module paths map to byte-identical published PR190 members.
RAW retains original paths/layout labels as evidence; it does not rewrite source
imports or historical receipts for a new environment. Executing this capsule
would require a separately authorized exact reconstruction, not implied by delivery.
