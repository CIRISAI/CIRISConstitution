# The Dictionary

**What this is.** The namespace: every dimension family a row may carry, who owns it, its polarity, whether it is reserved, and the rules of the version segment and the case rule (3.1); the subject kinds and their payload shapes (3.3); the reserved prefixes and who may emit under them (3.4); and the relation precedence (3.5).

**Whom it binds.** Every producer that names a dimension and every substrate that admits one. A family that is not in the registry is refused as unregistered; a reserved prefix emitted by the wrong key is refused by name.

**What it promises.** That the family count is generated, not asserted: `manifests/namespace_registry.json` is built from this volume's text, its hash is pinned by every ratifying repository, and the prose and the manifest cannot disagree without the build failing. A matcher and a vector set accompany it so two implementations resolve the same dimension the same way.

**What it leaves out.** Section 3.2, the trust root and its standing verdict, which prints in *The Constitution*; the envelope the dimension rides in, which is *The Wire*; the composition of scores into a verdict, which is *The Reader's Policies*; and the powers that some reserved families carry, which are explained in *The Constitution*.

**Where the rest lives.** The authoritative form of this volume is the generated registry and its match vectors. Read the prose for the reasons and the machine form for the rows; when they differ, the build is broken and the manifest is what shipped.
