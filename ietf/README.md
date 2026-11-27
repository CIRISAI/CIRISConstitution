# The CIRIS SCITT drafts

Three Internet-Drafts describe CIRIS for the IETF SCITT working group, and they are released together, one suite at one Constitution tag. [`SUITE.tsv`](SUITE.tsv) lists them, the revision this tree releases, and which draft each depends on.

| Draft | What it specifies | Depends on |
|---|---|---|
| `draft-moore-scitt-ciris-ceg` | the signed row: its encoding, the names rows give each other, the composite signature, admission, and how the rows relate to SCITT | — |
| `draft-moore-scitt-ciris-trace` | the CIRIS agent's reasoning trace: its components, levels, signing, `run_kind` and the action it anchors to | ciris-ceg |
| `draft-moore-scitt-ciris-trace-context` | the context manifest of each model call within the trace: where each part of a prompt came from, under which policy | ciris-trace, ciris-ceg |

A draft cites the drafts below it normatively and those above it informatively, each by the revision the suite releases. A draft published before a sibling's newer revision keeps citing the older one until its own next revision. A draft pins the Constitution tag of the drafts it depends on; one published before they moved to a newer tag keeps the older tag until its own next revision, and none pins a later tag than a draft it depends on.

**Building.** `python3 tools/build_ietf_draft.py` builds ciris-ceg and `--check` rebuilds the released revision from its frozen source (`<name>.ietf-<rev>.md`). `python3 tools/build_ietf_companion.py <name>` does the same for the other two. `python3 tools/check_ietf_suite.py` checks the cross-references (consistency CI). With `--release` it also refuses a cut while any draft of the suite is still pending.

**Submitting.** The steward submits, in dependency order: ciris-ceg, then ciris-trace, then ciris-trace-context.

**A companion for a Transparency Service that takes pure ML-DSA.** [`scitt-companion-demo/`](scitt-companion-demo/) holds test artefacts made for the SCITT list: the statement of Appendix B.3 of ciris-ceg-04, a pure ML-DSA-65 companion of it in three forms (the statement id in the protected header; the id and a digest of the original's full bytes in the payload; both in the protected header), the registration key the companion is signed with, and the composite-signed statement by which the issuer vouches for that key. Every key is a test key from a public seed. The vouch and the companion's labels are proposals for discussion and are no part of any draft here. Its `README.txt` gives the checks a relying party makes, in order.
