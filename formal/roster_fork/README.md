# `formal/roster_fork` — two versions of one roster head

**The question.** A roster version names the head it extends and is counted over that head's members. Two
versions may name one head, by honest concurrency or by a faction. A rule under which the first version a
node sees wins is not a function of the rows a node holds. The rule of
[CC 3.2](../../constitution/part_3_the_namespace.md) T6 is the one this model checked: tips wait.

**The model** (`fork.py`). Every set of at most K versions that can exist when an adversary holds some keys and
signs anything, naming any head, and an honest key signs only what it accepts. Nothing is assumed about when a
key signed, so a version signed long ago and completed late is in the enumeration, and so is every withholding
of rows. Nine rules are run over those sets under eight counting protocols.

**The rule that holds: tips wait.** With one tip the roster is its roster. With several it is the members
common to all of them. A version that names the tips, counted over the members common to them, makes one head
again. A removal reaches the rows of the removed key that no concurrent head has in its past.

While the adversary is below the count, over every set at K = 3:

| Property | Tips wait | First seen wins |
|---|---|---|
| the roster is a function of the set | holds | fails at two versions |
| no removed key is listed | holds | fails |
| the adversary alone signs no valid version | holds | holds |
| a removal naming an old head voids nothing more | holds | fails |
| the honest members can sign back to one head | holds | fails |

**What it costs.** A member added on one tip is not listed until a version names both tips. A version stays
valid on a voice that a sibling version removes, since the voice was good at the head it named.

**What no rule here survives.** An adversary holding the count of an old head signs a valid version alone.
That is the case a witnessed lineage answers (CC 3.2 T6), and it is each reader's own trust that decides whose
witnesses count.

**What a roster version must carry.** The heads it extends, as a list. Today it names one.

Run: `python3 -I formal/roster_fork/fork_check.py --check`
