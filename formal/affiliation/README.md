# `formal/affiliation` — the affiliation tier split in two, and the promises it maps to

The steward (2026-10-28): "I am a solo practitioner who wants the data protections — it just is; how do we protect that small-business scenario while keeping the protection? The second protection is for people; we don't want affiliations to become where despots despot."

**The split.** An affiliation bundles two things the text can hold apart. The **data regime** (CC 4.4.3.2.8: classification, retention, legal hold, erasure policy, designated officials, disclosure, custody) attaches to the record and its subjects at any size, so a one-member affiliation exists, holds data and licenses under the limbs from creation. The **floors** (CC 4.5.13: no single vote admits, no single vote removes, a named moderator) bind power over *members*, and where the body has one deciding voice the second voice comes from outside the deciding seat: the designated official where that is a distinct key, or a review-holder of the body that conferred or oversees the affiliation. Appointment is the body's signature plus the appointee's own acceptance, two consents.

**The model** (`Affiliation.lean`, core Lean). A body has deciding seats, members, a designated official and overseers; an act names its kind (appoint, remove, quarantine, slash, takedown), its signers, an optional countersign and, for an appointment, the appointee's acceptance. `admitted` is the floor as the text states it.

| Theorem | What it says | Promise |
|---|---|---|
| `a1_data_regime_at_any_size` | the limbs bind the record whatever its size | 1, 8 |
| `a2_one_voice_appoints_with_acceptance`, `a2_no_appointment_without_acceptance` | a one-voice body appoints with the appointee's acceptance and never without it | 1, 2 |
| `a3_one_voice_removes_nobody_alone`, `a3_seat_cannot_countersign_itself`, `a3_outside_countersign_admits` | a one-voice body removes nobody alone, cannot be its own second voice, and acts with an outside countersign on the record | 6, 2 |
| `a4_no_power_act_on_one_voice` | the same for quarantine, slash and takedown | 4, 2 |
| `a5_two_voices_decide_as_a_community` | two or more voices decide under their own protocol, as a community does | 6 |
| `commitments_mapped` | every rule descends from a named promise and the five promises the split touches (1, 2, 4, 6, 8) are each carried by a rule | — |
| the worked world | the solo practitioner: hires with acceptance; cannot fire alone; cannot countersign herself; fires with the professional body's review-holder; the limbs bind from day one; a two-seat partnership decides as a community | — |

**What it does not model.** The reconsideration path a refused act falls into (CC 4.5.5); the protocol arithmetic of a multi-seat body (`formal/membership`, `formal/two_path`); the data limbs' own rules (CC 4.4.3.2.8 prose; Annex I). The wire door is CIRISPersist#1143.

**Running.** `lean Affiliation.lean`; the CI job `reciprocity` compiles it beside the cascade and the trust set.
