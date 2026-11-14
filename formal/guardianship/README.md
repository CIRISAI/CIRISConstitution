# `formal/guardianship` — a minor's guardianship when it is contested

**The point.** A node decides no custody. A court's order naming a new guardian is attested by the people it
binds, and nobody else can speak for a court (CC 3.2). So the rule has to do two things at once: never let a
newcomer take a child by their own signature, and never let a dispute cut the child off or leave them unheard.
This model states the rule as a fold over the rows a node holds and checks both.

**The model.** `guardianship_model.py`. One minor, a current guardian, an order naming a new one. The rows are
the three attestations of the order (the minor's, the displaced guardian's, the named guardian's), the minor's
refusal, the current guardian's step-down, the named guardian's binding, and a new act of either guardian
offered at the door. The band on record is `under_13`, `13_15`, `16_17` or none. The fold gives who the guardian
is, whether a contest stands, the minor's mode, whether the safeguarding report is raised, and which acts are
admitted.

**What is checked**, over every set of rows at every band (1,024 cases):

| | Property |
|---|---|
| G1 | there is at most one guardian, and it changes only by a step-down or an admitted order |
| G2 | the named guardian's own rows never displace the current guardian alone |
| G3 | the minor's word opens a contest at every band and where no band is on record |
| G4 | below 13, and with no band, the minor's word never counts toward admitting the order |
| G5 | from 13 the minor's word with the named guardian's admits the order |
| G6 | at 16 and 17 the minor's refusal blocks an order the two guardians attest |
| G7 | a contest never stops the minor: the mode under a contest is the floor of CC 3.4.13 |
| G8 | while a contest stands no new act of either guardian is admitted |
| G9 | a contest raises the report |
| G10 | with no attestation of an order there is no contest and nothing is frozen |
| G11 | the verdict depends only on the rows held and the band |

Each property fails when the line of the fold that carries it is changed.

**What the model made plain.** An admitted order moves nothing until the named guardian's own binding is held:
the order opens the way and the guardian still signs. A step-down with no successor leaves the minor with no
guardian, which is the standing rule against operating without one and is not softened here. A child under 13
whose guardian will not step down stays with that guardian on the wire, under the floor, with the report raised;
the court's power to compel the step-down is the only remedy, and the text says so.

**What it does not model.** How the band came to be on record (`formal/age_assurance`); the family that carries
an attestation of an order, which is not yet registered; an adult under incapacity (CC 3.4.12), where the same
question stands and is not settled; whether a community goes on recognising a guardian, which is each
community's own decision.

Run: `python3 formal/guardianship/guardianship_model.py --check`
