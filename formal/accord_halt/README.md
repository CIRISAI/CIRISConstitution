# `formal/accord_halt` — the halt's fire path, two ways

**Why.** Could a halt be seen in flight and interrupted? An earlier form of the text gave the
halt three thresholds (CC 4.2.1.1: two of three signatures; CC 4.2.6: a floor
of one over a live set; the safety page: "2-of-3 live-quorum") and one mechanism — a server-issued
proposal, a participation window, a decision — that is visible before any signature exists.

**What it models.** Three holders, one subscribed node and one not, an adversary that can coerce
one holder, jam the channels, kill the server, and steal a pre-signed row; resumption by two of
three. `Mode = "proposal"` is that earlier path; `Mode = "row"` is CC 4.2.1.1's: a halt is one
self-contained signed row by any holder, pre-signable offline, fired on receipt and latched.

| Config | Result |
|---|---|
| `AccordHalt_proposal_window.cfg` | `Inv_NoWindow` violated in 3 steps: intend, open proposal — the adversary sees a halt attempt that has not landed |
| `AccordHalt_proposal_stuck.cfg` | `NotStuck` violated in 4 steps: intend, open proposal, jam — an honest holder wants to halt and nothing lands |
| `AccordHalt_proposal.cfg` | the remaining properties hold (2,352 states): a halt binds subscribers only; a coerced holder alone cannot resume |
| `AccordHalt_row.cfg` | every property holds (19,408 states): no window; firing is enabled by intent and a channel alone, never by the server or another holder; a stolen sealed row is a false halt and nothing more; resumption needs an honest signature |

**The fuse (`AccordHaltFuse.tla`, CC 4.2.1.1).** The one-row halt plus: a lone
halt lapses after `Fuse` ticks unless a strict majority of the standing roster confirms it; a
confirmed halt ends only by a majority resumption. `AccordHaltFuse.cfg` closes at 319,090 states: `Inv_LoneBounded` (a lone pause never outlives the fuse), `Inv_FireEnabled` (the stop
needs only the firer and a channel), `Inv_ConfirmNeedsHonest` / `Inv_ResumeNeedsHonest` (a
coerced holder alone does neither), `Inv_MajorityCanConfirm` (two honest reachable holders can
always confirm before the fuse runs), `Prop_ConfirmedPersists` (a confirmed pause ends only by
resumption), `Inv_MajorityCanResume` (a majority can end an unconfirmed pause before the fuse: a
stolen sealed row need not run its course). The fuse counts from receipt, as the model's `Stop`
does, never from the signer-chosen `asserted_at`. An unbounded lapse counter is not modelled: it made the chain infinite and carried
no information.

**What it does not cover.** An adversary that jams every channel to every node *before* any holder
intends to halt (the row path is not immune to that; nothing is), and an AI that acts faster
than a row propagates (answered only by agents checking the latch before every effectful act).

Run: `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config AccordHalt_<cfg>.cfg AccordHalt.tla` (TLA+ tools 1.7.4; each finishes in seconds).
