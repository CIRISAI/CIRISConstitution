# `formal/age_assurance` — the band a person is read at

**The rule (CC 3.4.11, CC 3.4.13).** Rows about one identity come at three levels: the person's
own declaration, and a witness's attestation at the provider or the government rung. A reader
unions them and takes the highest level on record. With no witness row on record the person is
read at the most protective band, under 13 with a guardian's co-sign, whatever they declare.
A declaration can lower the band and never raise it. The band belongs to the identity, so a
signal obtained on one device of a self roster is read by every key of that roster.

**The model** (`AgeBand.lean`, Lean 4 core, no Mathlib). `resolve` is the fold from the rows on
record to a band.

**Proved.** `absent_is_under13`: no row reads as under 13. `self_alone_is_under13`: any number
of declarations and no witness row still reads as under 13. `self_never_raises`: with a
declaration on record the band is at most the band the witness rows give. `adult_needs_witness`:
adult is read only where a witness row is on record. `device_independent`: the band is a
function of the rows about the identity and of no device. Five worked cases, among them a
desktop with nothing on record, and the same person after a phone joins the roster and its
platform signal is attested at the provider rung.

**What it does not model.** Who may be a witness and how a platform signal is attested (CC 3.4.11,
the reserved prefix); the capability envelope of each band (CC 3.4.13); guardianship; whether
the roster's devices are one person's (CC 3.3.6.4), on which the roster rule rests.

**Run.** `lean AgeBand.lean` (exit 0, no `sorry`).
