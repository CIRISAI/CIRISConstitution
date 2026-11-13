Title: v62 signed object: what the rc19 kernel needs from COSE, beyond #326

#326 owns the encoding and stays as it is: one COSE_Sign1 for each signer, the composite algorithm, deterministic CBOR, the statement id, the known-answer vectors. This issue lists what the constitution's kernel work on branch rc19 adds to it or changes in it. It is put here first because verify computes the bytes everyone else pins, and the constitution writes no wire text for CC 2.6.1.8 until verify has said what shape it wants.

Source: CIRISConstitution rc19 at aaf55fe. The kernel is one page, `formal/KERNEL.md`; the proofs are in `formal/causal_order` (Lean, sixteen files, built on every commit); the running models are in `formal/causal_kernel`. A proposed schema is at `handoff/verify/signed_object_v2.proposed.cddl` in that branch. It is a proposal to react to, not a ruling.

Nothing here touches edition 1. Every row signed under the earlier form verifies as itself.

## What the kernel requires

**1. A row is named by one digest, and nothing else names a row.**
The kernel's only order is what rows name (KERNEL 2). That is well founded only if a name is a digest of bytes that exist. An attestation id is chosen before the bytes exist, so two rows can name each other by it and two signers can choose one id.
- The statement id of #326 covers the protected header, so it differs for each voice of a counted row. It names a statement, not a row.
- The quorum key covers the payload alone. It omits the content type and the subject, which ride only the protected header, so two different rows can share one key.
- Needed: a **row id** shared by every voice of one row, unchanged when a voice, a receipt or a disclosure is added, and committing to every member a conclusion reads. Proposed: SHA-256 over the deterministic encoding of `["CEG-row/2", cty, sub, author-or-null, payload]`, where the author is the signer for an authored family and null for a counted one.
- Needed: every row a row names, in ONE member (`refs` in the proposal), by row id, so any holder computes what a row names without knowing its family. A row of this edition names an edition-1 row by the digest of its signing input, never by its attestation id.
- Verify's part: the row id and its vectors; a decoder that returns the named set from `refs` alone; refusing a payload that is not in deterministic encoding, since a second encoding would be a second row.

**2. Verification has three answers, not two.**
A row waits for what it names and is never refused for another row (KERNEL 3; `Causal.kept_is_least`, `door_any_order`). Checking a signature reads the key record, which is another row. So for a statement whose key is not held, the answer is neither valid nor invalid: it is **waiting, with the missing key named**. An API that returns an error there makes every caller judge on arrival, which is the fault the kernel removes. The transport's next release holds such rows inert and releases them when the key lands, and it needs this answer from verify.
- Verify's part: a verification result of valid, invalid, or waiting on a named key; the same for a statement whose composite key record is held in part.

**3. The voices of a counted row are signatures on the row.**
A body consents by its members' signatures on the row. A count once met is final against every later row, and one signature never removes (`Consent.count_is_final_against_members`, `RosterHead.one_signature_never_removes`). In COSE terms a counted row is several statements over the same payload, found by the row id.
- Each voice signs the whole payload, and so the roster head the row is counted over. A voice stands for that head only (`Harden.F3.no_replay`). The head therefore rides the payload (`refs.head`), not a header a voice could vary.
- A roster version names the head it extends and may name further heads beside it (`refs.further_heads`), so one version can join tips that wait. The store has agreed this shape.
- One acknowledgement names a head of a scope and states that its signer holds every row beneath it. It replaces one acknowledgement for each row.
- Verify's part: cosign vectors as N statements with one row id; an accessor for the head or heads a row names.

**4. Integers, not floats.**
A derived answer is a function of the set of rows (KERNEL 3), and a sum must be the same in every order. Binary floating-point addition is not associative. This agrees with verify's own preference on gap (a) in #326. The constitution will state scores, confidences and weights as integers at a fixed scale; the scale is verify's to propose (it proposed 10^6).

**5. Time: a statement's own stated end, and nothing ranked by `iat`.**
- A row's own end (`exp`) is read from the statement alone against now, with any bound on it read from the statement's own members. No arrival-clock check is applied to a replicated statement.
- No rule ranks statements of different issuers by `iat` or by a digest. Seven places in the text that did were corrected (rc19 ef7275a). In particular every admitted revocation stands and a key's bound is the minimum over all of them (CC 5.3.2.3, CC 2.4.1.1). So the signed revocation snapshot of gap (e) is a set and has no winner. Ordering one signer's own snapshots by that signer's revision is fine: one voice may order its own rows.
- Verify's part: no helper that picks "the latest" across issuers; the snapshot format as a set.

**6. A private room's keys.**
In a private room the roster seats a voice, a small roster of room keys, and no row of the room names or proves a person (CC 3.1.3.2). The store's v62 wire is agreed.
- A statement signed under a room key carries that room key's own thumbprint as `iss`, never the person's genesis key.
- The seat row of a room key carries a commitment to its person. The binding that opens it is two KEM encapsulations and no signature, made for one addressee, under a key pair kept for bindings and never the content-KEM pair.
- Statements of a private room are not registered with any outside service.
- Verify's part: the `iss` form for a room key; the commitment and binding constructions with vectors.

**7. The second consent.**
A `delegates_to` that carries a scope seats its delegate only with the delegate's own signature, on that row or by a row of its own naming it (CC 4.4.3.4.3, rc19 e9e1928). An owner-binding counts only with the node's own key on it. In this edition that is a second statement over the same payload, found by the row id. This touches the open #300 (the grant producer's shape).
- How the second signature travels, and from when a delegation without one stops seating, are deliberately left to the implementers. Verify's preference is wanted.

## The five gaps of #326, as they stand
- (a) scores: integers, as above.
- (b) `external_aad` and the `typ` list for objects that are not rows: unchanged; the constitution writes the list once verify confirms its set.
- (c) an earlier-form object and the cutover: proposed as "in the past of the ceremony row", a chain of named rows, with no instant and no log position compared; an object outside that past is signed again by its own signer.
- (d) FedCode key ids against composite thumbprints: unchanged, verify's proposal stands.
- (e) the revocation snapshot: a set, as above.

## Coming, not yet text
An identity key with no owner will be required to state its own end, so that its rows stop counting on their own clock at every node alike. It is being modelled and is not in the text. If it lands, a key record carries `exp` under a ceiling read from the record itself.

## Order of work
1. Verify answers here: the row id structure, `refs`, the three-valued result, the integer scale, the second consent's shape.
2. The constitution lands CC 2.6.1.8 and `manifests/signed_object_v2.cddl` to match, with the kernel's reasons.
3. Verify publishes the vectors; the store and the transport pin them.

No verify build writes edition 2 before the ceremony. Sequencing against the releases in flight is the owner's.
