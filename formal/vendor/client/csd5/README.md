# `formal/csd5/` — one TLA+ module per CSD/5 card

**GENERATED.** `python3 packaging/check_csd5.py --write-tla` writes
`<card>.tla`, `<card>.cfg` and `<card>.join.json` from the card's `csd:inputs`, `csd:view` and
`csd:acts` blocks. Edit the card, not these files: the gate regenerates each
module in memory on every run and fails if the committed one differs.

The standard is `FSD/CSD5.md`. The registry and its twelve laws are
`packaging/csd5/ui_primitives.json`.

## What is here

| module | card | distinct states, explorer | distinct states, TLC | invariants |
|---|---|---|---|---|
| `CSD070.tla` | CSD-070 Commons | 134,928 | 134,928 | 11 |

`CSD070.join.json` is the same card as data (`FSD/CSD5.md` §7.0): each write
with its row, its confirm, what it sends and shows and who may send it, and each
drawn instance with what it is bound to. It is for the model that joins a card to
CIRISConstitution `formal/event_lifecycle`, which CC plans and has not built.

## What has been run

* **The Python explorer** in `packaging/check_csd5.py`. It walks every
  reachable state of the card and checks every law in each one. Its count is
  the number in the table and in the module's header.
* **TLC** 2.19 (`tla2tools.jar` v1.7.4, sha256
  `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`), on the
  committed module:

  ```
  Model checking completed. No error has been found.
  1414922 states generated, 134928 distinct states found, 0 states left on queue.
  The depth of the complete state graph search is 21.
  ```

  The explorer reads the card's blocks directly; TLC reads the module generated
  from them. The same number of distinct states from both is the cross-check.
  A different number means the generator and the explorer disagree about the
  card, and that is a defect in `check_csd5.py`, not in the card.
* **`--self-test`**, which plants 30 defects and requires each to go red,
  including one that removes the L7 invariant from a generated module and
  requires the drift check to notice. It also plants one thing that must stay
  green: a one-step write sent by an Action with no sheet.
* **`--self-test --tlc`**, five more. Four modules are generated from the card
  with one defect planted each, and TLC must name an invariant of the broken
  law as violated:

  | planted | TLC must report |
  |---|---|
  | the grounds can be edited while the dry run stays held | an `Inv_L11_` invariant |
  | the dismissal can be submitted with no dry run held | an `Inv_L7_` invariant |
  | the grounds are off screen when the dismissal is confirmed | an `Inv_L12_` invariant |
  | `empty` and `populated` both hold | an `Inv_L2_` invariant |

  The fifth holds the clean module against a state count that is off by one
  and requires the comparison to fail.

CI runs `--self-test --tlc` and `--tlc` on every push (`build.yml`), fetching
the jar by its release URL and refusing it unless the sha256 above matches.

## Run it

```
python3 packaging/check_csd5.py --tlc tla2tools.jar
```

or TLC alone:

```
java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -config CSD070.cfg CSD070.tla
```

TLA+ tools 1.7.4, the version CIRISConstitution's `formal/` uses. The `.cfg`
sets `CHECK_DEADLOCK FALSE`: leaving the screen is a terminal state, not a
defect. `--tlc` runs TLC in a temporary copy, so no `states/` directory is left
here.

## How the module is laid out

* One variable, `st`, a record of strings. Field prefixes say what a field is:
  `x_` context, `l_` a local value, `r_` a read's outcome, `c_` what an answer
  carries, `p_` a preview, `q_` an input as it stood when an answer was taken
  over it, and `sheet`.
* One action per thing that can happen: `Edit_<field>`, `Pick_<choice>`,
  `Press_<act>`, `Answer_<read>`, `Confirm_<sheet>`, `Cancel_<sheet>`.
* One invariant per law instance, named `Inv_<law>_<instance>_<what>`. L2, L3,
  L4, L7, L11 and L12 have per-state invariants. L1, L5, L6, L8, L9 and L10 are
  checked on the card's structure or need the whole reachable set and have
  none; the explorer checks them.

## What the model does not say

`FSD/CSD5.md` §6. In short: no time, one element per collection, a text is
blank or filled, nothing about the Kotlin beyond the tags it shares with the
card, and nothing about whether a write's `confirm:` is the cell CC's manifest
holds.

## Relation to CIRISConstitution `formal/`

CC's `formal/event_lifecycle` proves `preview_is_execution`,
`confirm_is_lookup` and `exit_is_one_step` over the rows a node holds. L7 and
L6 here are the same properties stated over what a screen draws and sends, and
L12 is the screen's half of `answer.shown_digest`. The two are not composed:
nothing checks that this module's `issue` is that kernel's rewrite, or that a
card's `confirm:` is the manifest's cell. That is part of what moving the
standard to CC is for.
