# `formal/set_item` — a set of rows as one item, and the law that admits it

**The point.** Signing is most of what a small row costs. Many rows by one signer at one instant in one family
could travel as one item: a header the signer signs once over a digest of the leaves, and the leaves, each with a
proof that it belongs. Sets are where a rule system goes wrong, so an item is admitted on one condition.

**The law.** What a node concludes from the item equals what it would conclude from the same leaves held as
separately signed rows. If that holds, an item changes the bytes and never a conclusion.

An item is also flat (no leaf is an item), enumerated (it lists its leaves and never says "all who"), of one
signer, one signed instant and one family, and each leaf's verdict stands apart from its siblings.

**The model.** `set_item_model.py`. Both sides are folds over what a node holds and when it first held each
part. A row counts when held within the freshness window of its signed instant. A leaf counts when the node holds
the header and the leaf, the proof is good, the header is not forked, and the leaf is fresh.

**What is checked**, over every set of parts at every arrival instant (16,807 cases):

| | Property |
|---|---|
| S1 | the law: a leaf counts exactly when its row would, the row being first held when the node first held both header and leaf |
| S2 | a leaf's verdict does not depend on which other leaves are held |
| S3 | a leaf held before its header counts as soon as the header is held, as if they had come together |
| S4 | a header alone counts for nothing |
| S5 | a leaf whose proof does not match the header never counts |
| S6 | under a forked header no leaf counts, whichever header came first |
| S7 | the verdict is a function of the parts held and their first-held instants |

**What it found.** The law decides a question that looks like a detail: when is a leaf first held? Three readings
were run. Only one holds the law: a leaf is first held at the later of its own instant and its header's. Judged by
the leaf's own instant, a leaf that waited for a late header counts where its row would be stale. Judged by the
header's instant, a leaf that reaches a node long after the header counts where its row would be stale. The check
requires the first reading to hold everything and each of the others to break the law.

**What it does not model.** The proof itself and the digest; a chained item, whose links are bounded by a full
item at a stated interval; which families may travel this way, which is each family's own law to pass.

Run: `python3 formal/set_item/set_item_model.py --check`
