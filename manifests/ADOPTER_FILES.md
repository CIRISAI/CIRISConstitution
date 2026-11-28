# Files an implementer pins

Five flat files, each generated from the repository's own tables by one tool, so that an implementation loads the law as data and authors no table of its own. Rebuild them with:

    python3 tools/build_adopter_files.py

and check that the committed copies are current with:

    python3 tools/build_adopter_files.py --check

The gate (`tools/gates.sh`) and the consistency workflow run the check.

| File | What it holds | Built from |
|---|---|---|
| `family_placement.tsv` | One line per family: where its rows are placed, what the placement follows, its verbs, whether its act is counted, its fold, and the section that states the placement. | `manifests/family_model.json` |
| `refusal_tokens_delta_rc22.tsv` | The refusal tokens added, renamed and retired since the tag `v1.0-rc22`, and every token whose position in `refusal_tokens.tsv` moved, with its old and new position. | `manifests/refusal_tokens.tsv`, now and at the tag |
| `claims_delta_rc22.tsv` | The claim ids added, renamed and withdrawn since `v1.0-rc22`. | `constitution/claims.tsv`, now and at the tag |
| `retired_rc22.tsv` | Families, verbs, role tokens, protocol kinds, refusal tokens, envelope members and policy rows present at `v1.0-rc22` and absent now, with where each was. | the same tables, now and at the tag |
| `shape_delta_rc22.tsv` | Every member of the signed object's table and the family payload tables added, changed or removed since `v1.0-rc22`. | `constitution/signed_object_v2.tsv`, now and at the tag |

`refusal_tokens.tsv` is sorted by token, so a token added earlier in the alphabet moves every later token by one place. Pin a token by its name; its position is not stable across editions.

A rename is read only where a retired entry and an added entry stand in the same section with the same words once the name is taken out. Any other change reads as an addition and a retirement.

The policy table's explicit columns (who opens a window, what the opening act counts as, who lands it, the words a landing may state, a base stated as a number) are in `governance_policy.json`. The mesh configuration keys are in `constitution/mesh_config_keys.tsv`.
