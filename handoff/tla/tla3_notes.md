# tla3.diff: supersedes handoff/tla/tla.diff (apply tla3.diff to the base instead of it). Not run (no TLC).

## formal/membership (Membership.tla, 12 cfgs, README.md)
As tla.diff: GroupKind ("family" | "community"); founder_only only in a family (CC 3.2); in a community a count
needs two voices where the roster has two or more (CC 4.5.13). Correction: `unanimous_two` (a community) no longer
fails: the floor refuses the one-voice removal, so Inv_CoercedCannotRemoveHonest holds. README row and cfg comment
say so; its expected entry becomes "closes". The "every other member" reading still fails in a family; no cfg runs
that (open: add a family twin if the bound is wanted).
Should hold: every listed invariant/property; founder_only_coerced and stale_founder still fail theirs.
Run: java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config Membership_<cfg>.cfg Membership.tla
(README: about five minutes a closing cfg with -Xmx3g; a twin in seconds.)

## formal/mesh_life (MeshLife.tla, 14 cfgs)
Locked == founded /\ moderator = "-" (CC 4.5.4 (v)). Propose, Accept and Write refused while Locked (read-only).
NameModerator / NameAgentModerator: any member, while Locked, no size bar. CC 4.5.13: "The floor in a small room is
the smaller of two voices and the roster's size, so a room of one elects itself by its own ballot and no room is
locked beyond its members' reach." So no liveness property is restated. Recall (CC 4.5.13 moderator_recall, any
duty holder, floor two voices, abstracted to two members or more; gated on the moderation family) clears the
moderator and the room locks.
Should hold: all listed invariants and properties, and Act_LockedAdmitsNobody, Act_LockLiftsByTheCount,
Act_LockedReadOnly, Act_RecallNeedsTwo (added to the 14 cfgs).
Expected entries that move: README "Where it bubbled" distinct-state counts; the mesh_life job's state counts.
Run: java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock -config MeshLife.cfg MeshLife.tla, and each twin
(README: the liveness run wants a few cores and ten minutes; the full set has taken about two hours).
