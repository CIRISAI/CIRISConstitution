# The Threat Model

**What this is.** What is trusted, why, and what happens when it is wrong: the adversary model of 1.13.3 with its conditioned cases, the transport, custody and privacy rules of Part 5 that answer it, the concerns ledger and the interoperability profiles of Part 8, and the trust assumptions a reviewer should attack first: the out-of-band anchor, the witness directory, the single-signer transparency logs.

**Whom it binds.** Security reviewers and red teams by invitation; implementers by consequence, because every assumption named here is a rule somewhere in *The Wire* or *The Constitution*.

**What it promises.** That assumptions are named rather than implied; that each failure mode says what the record would show afterwards; that where a defence is a rule with no code yet, the register says so; and that the record of what was attacked and found is kept, including the attacks that succeeded.

**What it leaves out.** The ethics, which are *The Charter*, and the composition policies that a consumer applies after the adversary has been accounted for, which are *The Reader's Policies*.

**Where the rest lives.** The conditioned adversary table the rc8 review asked for is an rc9 item. The formal models under `formal/` are the mechanised half of this volume: each names the property it checks and the configurations under which it fails.
