# The Mathematics

**What this is.** Part 6: the canonicalisation boundary and the 1+4 line, the coherence mathematics, the capacity analysis of the degradable substrate, and the theorems with the Lean proofs behind them.

**Whom it binds.** Nobody directly. A theorem binds by being true. What binds implementers is stated in *The Wire*; what this volume adds is the argument that the wire's guarantees hold under the stated assumptions, and the named places where the argument is weaker than its statement.

**What it promises.** That every theorem printed here names its mechanised witness or says that it has none; that the collapse bound and the decay law are stated with their conditions; and that the substrate's measured constants are cited from the repository that measured them, on the population they were measured on.

**What it leaves out.** The engineering: codec choices, chunk sizes and endpoint shapes are in *The Wire*. The ethics the mathematics serves are in *The Charter*.

**Where the rest lives.** The Lean sources are in the coherence-ratchet repository at the pin named in `constitution/evidence_pins.tsv`; the register's `lean` rows name each theorem. A reviewer who wants to kill a theorem should start from the register row, not from the prose.
