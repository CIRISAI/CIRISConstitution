# `formal/kernel_lib` — the functions the checked models share

**The point.** Each small model in this folder wrote its own fold. Most of those folds are the same few
functions under other names. This package states them once and shows that the models' decisions, written
again with these functions alone, agree with the originals on the originals' own cases.

**The five functions** (`kernel_lib.py`).

| | |
|---|---|
| `sel` | the rows that match a pattern and were first held before an instant |
| `group` | group rows by a field and reduce each group: the least row, the greatest row, the one distinct value, or the count of distinct values |
| `in_range` | whether a value lies in an interval; an interval never opened holds nothing, and one not closed is still open |
| `rule` | the cell a typed table gives for a key |
| `fix` | repeat a step until nothing changes, to a bound |

| `ancestors`, `concurrent`, `frontier`, `past` | the closure over what rows name: what a row names and theirs, whether neither of two rows names the other, and the rows of a set that no other row of it has in its past |

`group` also sums, and gives the least or greatest value. Asked for the least or greatest row, it refuses a tie
between two different rows, so no answer depends on the order of a list.

None of them knows a family, a model or a rule.

**What is checked** (`kernel_lib_check.py`). Six decisions are re-expressed in `reexpress.py`: the takedown
fold, the deletion fold, the owner of a key, the guardianship fold, the ranked count and the set item. Each
is compared with the original on every case the original runs, then put in the original's place under the
original's own property check. 400,300 comparisons, none disagree; every property of the six still holds.
With `--ablate` each function is removed in turn and the models that break are listed.

**What this does not show.**

- Five is a low count. `group` is four reducers under one name, `fix` takes any step, and the join inside
  "an opener no closer answers" is written by hand at each use. A strict count is eight or nine.
- The key plane and the signer gate are not re-expressed. The key plane keeps a writer's running state over
  an order of acts. The signer gate checks the tables against each other and decides nothing over rows.
- There is no sum, no signature check and no delegation chain run against a model.
- The guardianship bands are a table inside `reexpress.py`, not yet read from a manifest.

`formal/derivation/basis/` holds four independent proposals for the smallest set of primitives, each with
the same 150 decision sites written as expressions over it.

Run: `python3 -I formal/kernel_lib/kernel_lib_check.py --check`
