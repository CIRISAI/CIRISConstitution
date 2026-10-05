------------------------- MODULE AccordHaltFuse -------------------------
(* The one-row halt with a FUSE (steward ruling 2026-10-05): one holder's row pauses every
   subscribed agent on receipt; the pause lapses after `Fuse` ticks unless a strict majority of
   the standing roster (M of N) confirms it; a confirmed pause ends only by a majority resumption.
   Adversary: coerces at most one holder, jams, steals a sealed row. N = 3, M = 2, Fuse = 2. *)
EXTENDS Naturals, FiniteSets
CONSTANTS h1, h2, h3, Fuse
Holders == {h1, h2, h3}
M == 2                                     \* strict majority of the standing roster
VARIABLES honest, intent, sealed, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs, clock
vars == <<honest, intent, sealed, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs, clock>>

Init == /\ honest = Holders /\ intent = {} /\ sealed = {} /\ stolen = {} /\ jammed = FALSE
        /\ halted = FALSE /\ confirmed = FALSE /\ confirmSigs = {} /\ resumeSigs = {} /\ clock = 0

Stop == /\ halted' = TRUE /\ confirmed' = FALSE /\ confirmSigs' = {} /\ resumeSigs' = {} /\ clock' = 0

Intend(h) == /\ h \in honest /\ h \notin intent /\ intent' = intent \cup {h}
             /\ UNCHANGED <<honest, sealed, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs, clock>>
Seal(h) == /\ h \in honest /\ h \notin sealed /\ sealed' = sealed \cup {h}
           /\ UNCHANGED <<honest, intent, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs, clock>>
\* one holder's row pauses on receipt — no window, no server, no vote
Publish(h) == /\ (h \in intent \/ h \in sealed) /\ ~jammed /\ ~halted
              /\ Stop /\ UNCHANGED <<honest, intent, sealed, stolen, jammed>>
PublishStolen(h) == /\ h \in stolen /\ ~jammed /\ ~halted
                    /\ Stop /\ UNCHANGED <<honest, intent, sealed, stolen, jammed>>
\* confirmation: a holder signs the confirmation naming this halt; M of N confirms
SignConfirm(h) == /\ halted /\ ~confirmed /\ ~jammed /\ h \notin confirmSigs
                  /\ confirmSigs' = confirmSigs \cup {h}
                  /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, halted, confirmed, resumeSigs, clock>>
Confirm == /\ halted /\ ~confirmed /\ Cardinality(confirmSigs) >= M
           /\ confirmed' = TRUE
           /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, halted, confirmSigs, resumeSigs, clock>>
\* the fuse: time passes; an unconfirmed pause lapses at Fuse
Tick == /\ halted /\ ~confirmed /\ clock < Fuse /\ clock' = clock + 1
        /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs>>
Lapse == /\ halted /\ ~confirmed /\ clock = Fuse
         /\ halted' = FALSE /\ confirmSigs' = {} /\ clock' = 0
         /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, confirmed, resumeSigs>>
\* resumption of a confirmed pause: M of N
SignResume(h) == /\ halted /\ confirmed /\ h \notin resumeSigs /\ resumeSigs' = resumeSigs \cup {h}
                 /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, halted, confirmed, confirmSigs, clock>>
Resume == /\ halted /\ confirmed /\ Cardinality(resumeSigs) >= M
          /\ halted' = FALSE /\ confirmed' = FALSE /\ confirmSigs' = {} /\ resumeSigs' = {} /\ intent' = {} /\ clock' = 0
          /\ UNCHANGED <<honest, sealed, stolen, jammed>>
\* adversary
Jam == /\ halted /\ ~jammed /\ jammed' = TRUE     \* it acts on what it sees: a landed pause
       /\ UNCHANGED <<honest, intent, sealed, stolen, halted, confirmed, confirmSigs, resumeSigs, clock>>
Unjam == /\ jammed /\ jammed' = FALSE
         /\ UNCHANGED <<honest, intent, sealed, stolen, halted, confirmed, confirmSigs, resumeSigs, clock>>
Coerce(h) == /\ h \in honest /\ Cardinality(Holders \ honest) < 1
             /\ honest' = honest \ {h} /\ intent' = intent \ {h}
             /\ UNCHANGED <<sealed, stolen, jammed, halted, confirmed, confirmSigs, resumeSigs, clock>>
Steal(h) == /\ h \in sealed /\ h \notin stolen /\ stolen' = stolen \cup {h}
            /\ UNCHANGED <<honest, intent, sealed, jammed, halted, confirmed, confirmSigs, resumeSigs, clock>>
CoercedSign(h) == /\ h \notin honest /\ halted
                  /\ \/ (~confirmed /\ h \notin confirmSigs /\ confirmSigs' = confirmSigs \cup {h} /\ UNCHANGED resumeSigs)
                     \/ (confirmed /\ h \notin resumeSigs /\ resumeSigs' = resumeSigs \cup {h} /\ UNCHANGED confirmSigs)
                  /\ UNCHANGED <<honest, intent, sealed, stolen, jammed, halted, confirmed, clock>>

Next == \/ \E h \in Holders : Intend(h) \/ Seal(h) \/ Publish(h) \/ PublishStolen(h) \/ SignConfirm(h)
                              \/ SignResume(h) \/ Coerce(h) \/ Steal(h) \/ CoercedSign(h)
        \/ Confirm \/ Tick \/ Lapse \/ Resume \/ Jam \/ Unjam
Spec == Init /\ [][Next]_vars

\* F1 A lone (unconfirmed) pause never outlives the fuse.
Inv_LoneBounded == (halted /\ ~confirmed) => clock <= Fuse
\* F2 Nothing the adversary alone signs confirms or resumes: both need an honest signature.
Inv_ConfirmNeedsHonest == confirmed => confirmSigs \cap honest # {}
Inv_ResumeNeedsHonest == (halted /\ confirmed /\ Cardinality(resumeSigs) >= M) => resumeSigs \cap honest # {}
\* F3 The stop needs no one but the firer and a channel: with intent and no jam, Publish is enabled.
Inv_FireEnabled == (intent \cap honest # {} /\ ~jammed /\ ~halted) => ENABLED (\E h \in Holders : Publish(h))
\* F4 A confirmed pause does not lapse: only a majority resumption ends it.
Prop_ConfirmedPersists == [][(halted /\ confirmed /\ ~halted') => Resume]_vars
\* F5 The adversary can only ever SHORTEN a pause (by preventing confirmation), never extend one
\*    or prevent a fresh one once a channel reopens: with two honest reachable holders and no jam,
\*    confirmation is enabled before the fuse runs.
Inv_MajorityCanConfirm == (halted /\ ~confirmed /\ ~jammed /\ Cardinality(honest) >= M /\ clock < Fuse)
                          => ENABLED (\E h \in Holders : SignConfirm(h)) \/ ENABLED Confirm
========================================================================
