# The Reader's Policies

**What this is.** How a consumer decides whom to trust: the anti-patterns that a composition must not fall into (4.1), and the composition and delegation policies of 4.4, Policies A to M and the aggregation rules, with the delegation graph's depth cap, cycle rejection and weight cap.

**Whom it binds.** Every CEG-Conforming Consumer that composes rows into a verdict, and every reader who wants to know what a score about them will be turned into. A consumer may add policies of its own; it may not skip the ones marked normative.

**What it promises.** That a verdict is a function of signed rows and declared policy, reproducible by anyone holding the same rows; that one human voice counts once (1.13.2, with the effective count of 6.1.2.1.2); that delegation is scoped, attenuated and revocable per link, that a hierarchy delegation ends within a year (4.4.3.2.8) and an act-on-behalf delegation ends at its stated `delegation_valid_until`; that a licence and a grant never chain.

**What it leaves out.** The rows themselves, which are *The Wire* and *The Dictionary*; the authorities whose rows a reader chooses to trust, which is *The Constitution*; and the mathematics of coherence under which the aggregation is analysed, which is *The Mathematics*.

**Where the rest lives.** Each policy's section states its inputs and its output in prose.
