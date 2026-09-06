# Attribution and primary licensing records

## EWT teacher data and public task excerpts

Source: [Universal Dependencies English Web Treebank r2.14](https://github.com/UniversalDependencies/UD_English-EWT/tree/r2.14), released 2024-05-15. The original [README](https://github.com/UniversalDependencies/UD_English-EWT/blob/r2.14/README.md) and license are retained unchanged as attribution/EWT-README.md and attribution/EWT-LICENSE.txt.

The README credits the annotation copyright to The Board of Trustees of The Leland Stanford Junior University, 2013–2021. It licenses annotations and database rights under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Preserve attribution, the license link and change notices when redistributing covered material; share-alike applies to shared adaptations within that license's scope.

The README separately identifies mixed underlying text copyrights, including original authors and Google, Yahoo, and the University of Pennsylvania. Do not describe the annotation license as a blanket grant over all underlying text. This capture includes selected public token forms and newly generated predictions, while excluding full TRAIN/DEV data. Predictions are generated annotations, not original gold annotations; their provenance and task transformations are explicit in the frozen manifest.

## Adopted software and external scorer

[UDPipe1](https://ufal.mff.cuni.cz/udpipe/1) and the included CoNLL18 evaluator use MPL 2.0. The source/LICENSE preserves the license; source/conll18_ud_eval.py preserves its UFAL/Charles University copyright and Milan Straka/Martin Popel authorship notice. Keep those notices and source-license terms when redistributing this file. No software executable or wheel is included in this Git capture; official package links and hashes remain in the acquisition record.

The underlying MorphoDiTa/Parsito mechanisms are adopted parents, not claimed ORION inventions. Software/source identities and configured non-Transformer execution path appear in prior-accounting.json and training-manifest.json.

## New model release attribution

The final model was trained here from EWT TRAIN only, without imported pretrained models, dictionaries or vectors. Its proposed release should carry its exact SHA256, training provenance, these data/software attributions and the original dataset notice. The primary records above do not themselves settle a legal classification or automatic license for newly learned model weights; the release owner must state its intended weight license explicitly. Do not borrow a license for official distributed pretrained UDPipe models and imply that one of those models was used.

Model: 11,631,918 bytes; SHA256 7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9. Public comparison, scientific claim authority and model-weight release terms are separate decisions.
