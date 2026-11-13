# tla.diff: not run (no TLC). Apply with git apply; then run as below.

## formal/membership (Membership.tla + all 12 cfgs)
Change: CONSTANT GroupKind ("family" | "community"); ASSUME founder_only => family (CC 3.2: founder_only is a
family's / publication's kind; a community has no founder tier, CC 4.5.4); in a community ProtocolMet also needs
two voices where the roster has two or more (CC 4.5.13). founder_only, founder_only_coerced, founding_unsigned,
stale_founder cfgs set GroupKind = "family"; the other eight "community".
Should still hold: every invariant and property each cfg lists; each must-fail twin still fails its named one.
Expected entries that may move: README table "TLC verdict" state counts for the eight community cfgs (the floor
only removes behaviours the strict majority / quorum M=2 already refuse, so no verdict should move).
Run: java -cp tla2tools.jar tlc2.TLC -workers auto -metadir /tmp/tlc -deadlock -config Membership_<cfg>.cfg Membership.tla
(README: about five minutes a closing cfg with -Xmx3g; a twin in seconds.)

## formal/mesh_life (MeshLife.tla + 14 cfgs)
Change: Locked == founded /\ moderator = "-" (CC 4.5.4 (v)); Propose refused while Locked; NameModerator and
NameAgentModerator only while Locked and with two members or more (the members' count, never fewer than two
voices); new action properties Act_LockedAdmitsNobody, Act_LockLiftsByTheCount added to every cfg with
Act_MuteChangesNoRow.
Should still hold: Inv_ModeratorIsMember, Inv_AgentModeratorIsBonded and every listed invariant/property; the two
new ones. Risk to watch: a room left with one member now stays locked for good; any progress property that
assumed a moderator could always be named would fail there.
Expected entries that move: README "Where it bubbled" distinct-state counts (3.2 million) and the mesh_life
job's state counts in formal.yml output.
Run: java -cp tla2tools.jar tlc2.TLC -workers auto -deadlock -config MeshLife.cfg MeshLife.tla, and the same per
twin (README: the liveness run wants a few cores and ten minutes; the full set has taken about two hours).
