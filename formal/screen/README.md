# `formal/screen` — the screen, composed with the kernel

**The point.** CC 4.5.13 says the queue is the door run forwards: a person is offered exactly what the door would
admit, and an item that widens or has no way back is confirmed before it is signed. `formal/event_lifecycle`
proves that over one abstract family. This model runs it over the repository's own tables and the kernel's own
rows: a screen is a function of the rows a node holds, the viewer's key and now.

**The model** (`screen.py`). The node's rows go through the kernel (`formal/causal_kernel`): a row whose named
rows are not all held waits, every kept row is concluded against its own past, and the live seats are derived by
`seat.py`. An act on an object concludes only if the door admits it for its signer at that act's past. For one
viewer the screen draws:

| Part | What is drawn | Read from |
|---|---|---|
| objects | every object row in the viewer's audience, in its state | `route.audience` (the closed rule of CC 5.2); the state folds the concluded acts (CC 3.5.1) |
| items | on each object, and on each slot the viewer opened, exactly the transitions `may` admits, each with a ConfirmSheet or one step, and the policy row it runs under with that row's window | `manifests/transitions.json`, `manifests/governance_policy.json` |
| facts | `wire` and `by_rule` facts with their value, a `not_sent` fact as not sent | `manifests/choice_item.cddl` |
| waiting | every held row the viewer may see that is not kept, with the rows it waits on | `causal_kernel.kept`, `route.needs` |
| inert | every kept object or act that concludes nothing, as counting for nothing | the conclusion layer |

Standing over an object is read from the rows: `author` and `subject` off the row, `member` and the four duty
scopes from the live seats over its room (CC 4.5.4), `self` on the viewer's own slots, `registered` for every
key. `now` is read only against a row's own stated end, which draws an admitted object as lapsed.
`manifests/ui_primitives.json` gives the state names the screen draws in.

**The properties** (`check_screen.py`), each with deliberate breaks that must be caught:

| # | Property | Breaks |
|---|---|---|
| 1 | nothing drawn that the door refuses | `draw_all` |
| 2 | nothing admitted undrawn, unless the manifest lists it as not surfaced with its reason | `drop_exits` |
| 3 | a ConfirmSheet exactly when the rows widen at the scope signed or have no way back, computed from the widens and undo cells and not from the confirm cell; an exit is always one step | `confirm_exit`, `confirm_ignores_when`, `confirm_none` |
| 4 | the view is the rows: every arrival order draws the same screen, a row outside the viewer's audience changes nothing drawn, and now moves only a lapsed state | `first_held`, `ignore_audience` |
| 5 | a fact not sent is never drawn as sent | `not_sent_as_value` |
| 6 | waiting is drawn as waiting, with what it waits on, never as refused and never as done | `waiting_as_refused`, `waiting_as_done`, `waiting_unnamed` |

They run over three sets of worlds. **story**: the (view, standing) pairs of `manifests/mesh_story_trace.json`,
where the items drawn must equal the queue the story served. **grid**: every family, lifecycle state, standing
(no role, each role token alone, every token) and scope (self, community), where `may` must also equal the door
as `tools/mesh_story.py` runs it. **worlds**: generated rows at a small bound, a room founded by two duty holders,
a third key admitted or not and removed or not, one object of one of six families at self or community scope, a
subset of acts on it, and a row that waits or not, seen by the two holders, the third key and a stranger.
`screen_expected.tsv` records the verdict of every break and the counts.

**Measured.** 25 transitions have a way back that the text states (CC 2.4.1.1 rules 0 and 1) and that no
transition of the table offers, because the registry's verbs column lists no `withdraw` for their families. No
screen built from the table can draw those ways back. The check prints the count.

**Not modelled.** Signatures, layout and wording; a supersede that promotes its scope (the check reads it only
at the scope it replaces); more than one object per world; standings that come from seats other than membership
and the duties (`holder`, `owner`, `wa` and the others come in only through the story and the grid);
`manifests/reactions.json`, whose verdicts the screen would draw through `formal/derivation/verdict_state.tsv`.

  python3 formal/screen/check_screen.py            # exit 1 on a breach, a break not caught or a changed verdict
  python3 formal/screen/check_screen.py --write    # rewrite screen_expected.tsv
