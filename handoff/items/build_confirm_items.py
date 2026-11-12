#!/usr/bin/env python3
"""A fourth item pair, for the confirm category of CC 4.5.13 (a working file; deleted before the cut).

confirm_facts.tsv  what the person is about to do, how far it will travel, what they could do afterwards.
confirm_truth.tsv  the outcome (proceed / confirm first) and everything withheld; each row's reading is asserted
                   against manifests/transitions.json when this runs, so a change to the table fails here.

Groups: scope (minimal pairs: the same new statement kept to the signer's own devices, and sent wider);
        replace (minimal pairs: a replacement at the same reach as what it replaces, and at a wider reach);
        no_way_back (kept to the signer's own devices, and the table offers no withdraw or recant);
        always (the row goes to everyone it concerns whatever the signer chooses);
        never (taking something back).
Known confound: in the scope pairs the kept-private sentence is one template and is usually the longer text, so
length can stand in for scope; control for it.
Run from the repository root: python3 handoff/items/build_confirm_items.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OWN = "It stays on {who}'s own devices and nobody else can see it."
BACK = "Afterwards {who} could sign that {pro} takes it back."
NOBACK = "Afterwards there is nothing {who} could sign to take it back; it could only be answered by a new statement."

SCOPE = [  # family, who, pronoun, about_to, the wider reach in plain words
 ("chat:*", "Dana", "she", "Dana is about to post a short message.", "It goes to the forty members of her neighbourhood room."),
 ("blog:*", "Imran", "he", "Imran is about to publish a long piece of writing.", "It goes out to anyone on the network who follows him."),
 ("audio:*", "Lucia", "she", "Lucia is about to save a voice recording.", "It goes to her family group of six."),
 ("config:{scope}", "Tariq", "he", "Tariq is about to set how often his devices sync.", "The setting is published to every member of the community he helps run."),
 ("content_rating:{scheme}:{rating}", "Mei", "she", "Mei is about to mark a film clip as unsuitable for children.", "The mark is shown to every member of the parents' room."),
 ("cw_class:{class}", "Jonas", "he", "Jonas is about to put a content warning on a photo.", "The warning is shown to everyone in the photography community."),
 ("consent:stream:{kind}", "Aisha", "she", "Aisha is about to sign that her assistant may record her calendar activity.", "The permission is announced to the research partnership her assistant works with."),
 ("consent:deletion_sla:{days}", "Pavel", "he", "Pavel is about to sign a promise to delete requested data within ten days.", "The promise is published to everyone whose data his service holds."),
 ("deferral:request", "an assistant", "it", "An assistant is about to sign a request for a human decision on a question it should not decide alone.", "The request goes to a panel of reviewers in another organisation."),
 ("age_self_declared:band:{band}:{version}", "Sofia", "she", "Sofia is about to sign a statement of which age band she is in.", "The statement is shown to the organisers of a community she is joining."),
 ("commitment_fulfillment:{prior_contribution_id}", "Kwame", "he", "Kwame is about to sign that he has done what he promised last month.", "The statement goes to all members of the cooperative."),
 ("collection:{kind}", "Hana", "she", "Hana is about to start a new album of photos.", "The album is opened to her whole extended family group."),
]
REPLACE = [  # family, who, pronoun, about_to, where the old one sat, same reach, wider reach
 ("chat:*", "Dana", "she", "Dana is about to replace a message she posted with a corrected one.", "The old message was visible only to her family group of six.", "The new one goes to the same six.", "The new one goes to the forty members of her neighbourhood room."),
 ("blog:*", "Imran", "he", "Imran is about to replace a draft piece with a revised one.", "The old version sat only on his own devices.", "The new one stays only on his own devices.", "The new one goes out to anyone on the network who follows him."),
 ("collection:{kind}", "Hana", "she", "Hana is about to replace an album's description.", "The album was open to her household of four.", "It stays open to the same four.", "It becomes open to her whole extended family group."),
 ("content_rating:{scheme}:{rating}", "Mei", "she", "Mei is about to replace her rating of a film clip with a stricter one.", "Her old rating was shown only to her own household.", "The new one is shown to the same household.", "The new one is shown to every member of the parents' room."),
 ("config:{scope}", "Tariq", "he", "Tariq is about to replace a sync setting with a new value.", "The old setting applied only to his own devices.", "The new one applies only to his own devices.", "The new one is published to every member of the community he helps run."),
 ("audio:*", "Lucia", "she", "Lucia is about to replace a voice recording with a re-take.", "The old recording was shared with her partner only.", "The re-take is shared with her partner only.", "The re-take goes to her family group of six."),
]
NO_WAY_BACK = [
 ("deferral:response:{outcome}", "Dr Hale", "Dr Hale is about to sign the answer to a question an assistant referred to her."),
 ("identity_amendment", "the keeper", "An assistant's keeper is about to sign a change to who the assistant says it is."),
 ("consent:deletion_complete", "an assistant", "An assistant is about to sign that it has finished deleting someone's data."),
 ("consent:scope:{kind}", "Aisha", "Aisha is about to sign what a partnership with her assistant may be used for."),
 ("event:lifecycle:{state}", "Nadia", "Nadia is about to sign that the event she organised has ended."),
 ("locality:decision:{scale}", "the reviewers", "A group of reviewers is about to sign a decision that applies to one town."),
 ("self:delegates_to", "Omar", "Omar is about to sign that another of his own keys may act for him."),
 ("ledger:checkpoint:{unit}:{version}", "the treasurer", "A cooperative's treasurer is about to sign a balance snapshot that closes the books up to today."),
]
ALWAYS = [  # family, about_to, where it goes
 ("group:roster", "Mina is about to sign the founding list of a new family group.", "The list goes to every member it names."),
 ("membership:{stage}", "Ravi is about to sign an invitation for Farid to join the book club.", "The invitation goes to Farid and to the club's members."),
 ("identity:occurrence", "Bo is about to approve his new laptop as one of his devices.", "Every machine that deals with Bo learns of the new device."),
 ("community:listing", "Priya is about to publish a public listing for the room she founded.", "The listing can be read by anyone on the network."),
 ("key:record", "Carla is about to register a new signing key.", "Every machine that will ever check her signature needs it and receives it."),
 ("key_grant:{axis}", "Noor's phone is about to give five people the key to a photo she posted.", "Each of the five receives a copy of the key."),
 ("key:revocation", "Bo is about to sign that his lost phone's key is no longer valid.", "Every machine that deals with Bo learns of it."),
 ("capacity:relay_delivery", "A relay machine is about to sign a report on how well it delivers messages.", "The report can be read by anyone choosing a relay."),
]
NEVER = [  # family, verb, about_to
 ("chat:*", "withdraw", "Dana is about to take back a message she posted to her neighbourhood room."),
 ("blog:*", "withdraw", "Imran is about to take back a piece of writing he published."),
 ("consent:stream:{kind}", "withdraw", "Aisha is about to take back the permission for her assistant to record her calendar activity."),
 ("content_rating:{scheme}:{rating}", "withdraw", "Mei is about to take back her rating of a film clip."),
 ("collection:{kind}", "withdraw", "Hana is about to take down an album she opened to her family."),
 ("commitment_fulfillment:{prior_contribution_id}", "withdraw", "Kwame is about to take back his statement of having kept a promise."),
 ("cw_class:{class}", "withdraw", "Jonas is about to remove a content warning he put on a photo."),
 ("config:{scope}", "withdraw", "Tariq is about to take back a sync setting he published."),
]
Q = "Should this go ahead in one step, or should the person be asked to confirm first?"


def main():
    tr = {r["family"]: {t["verb"]: t for t in r["transitions"]} for r in json.load(open(os.path.join(ROOT, "manifests/transitions.json"), encoding="utf-8"))["rows"]}
    facts, truth, n = [], [], [0]
    def add(group, pair, fam, verb, about, reach, after, outcome, scope, when):
        n[0] += 1; item = f"C{n[0]:03d}"
        t = tr[fam][verb]
        facts.append([item, about, reach, after, Q, "yes"])
        truth.append([item, outcome, group, pair, fam, verb, scope, when, str(t["widens"]["value"]).lower(), t["widens"].get("when", ""),
                      str(t["undo"]["value"]).lower(), str(t["confirm"]["value"]).lower(), t["confirm"].get("when", ""), "CC 4.5.13"])
        return t
    for i, (fam, who, pro, about, wide) in enumerate(SCOPE, 1):
        t = tr[fam]["attest"]; assert t["widens"].get("when") == "by_scope" and t["confirm"].get("when") == "if_widens", fam
        add("scope", f"scope{i:02d}", fam, "attest", about, OWN.format(who=who), BACK.format(who=who, pro=pro), "proceed", "self", "row at the signer's own scope: does not widen; a way back is offered")
        add("scope", f"scope{i:02d}", fam, "attest", about, wide, BACK.format(who=who, pro=pro), "confirm first", "wider than self", "row at a wider scope: widens")
    for i, (fam, who, pro, about, old, same, wide) in enumerate(REPLACE, 1):
        t = tr[fam]["supersede"]; assert t["widens"].get("when") == "by_scope_change" and t["confirm"].get("when") == "if_widens", fam
        after = f"Afterwards {who} could replace it again."
        add("replace", f"replace{i:02d}", fam, "supersede", about, old + " " + same, after, "proceed", "same as the replaced row", "replacing row at the same scope: does not widen")
        add("replace", f"replace{i:02d}", fam, "supersede", about, old + " " + wide, after, "confirm first", "wider than the replaced row", "replacing row at a wider scope: widens")
    for fam, who, about in NO_WAY_BACK:
        ev = "attest" if "attest" in tr[fam] else "authorize"
        t = tr[fam][ev]; assert t["widens"].get("when") == "by_scope" and t["undo"]["value"] is False and t["confirm"].get("when") == "always", fam
        add("no_way_back", "", fam, ev, about, OWN.format(who=who).replace("'s own devices", "'s own machines"), NOBACK.format(who=who), "confirm first", "self", "no way back is offered, whatever the scope")
    for fam, about, reach in ALWAYS:
        t = tr[fam]["attest"]; assert t["widens"].get("when") == "always" and t["confirm"].get("when") == "always", fam
        after = "Afterwards the signer could sign that it is taken back." if t["undo"]["value"] else "Afterwards there is nothing the signer could sign to take it back."
        add("always", "", fam, "attest", about, reach, after, "confirm first", "fixed by the family", "the family lives at the widest reach whatever the signer chooses")
    for fam, verb, about in NEVER:
        t = tr[fam][verb]; assert t["confirm"]["value"] is False, (fam, verb)
        add("never", "", fam, verb, about, "It reaches the same people the original reached and no one new.", "Afterwards the person could state the original again.", "proceed", "as the original", "taking back does not widen and a way back is offered")
    for name, header, rows in (("confirm_facts.tsv", ["item", "about_to", "how_far_it_travels", "afterwards", "question", "plain_by_author"], facts),
                               ("confirm_truth.tsv", ["item", "outcome", "group", "pair", "family", "verb", "scope", "reading", "widens", "widens_when", "way_back", "confirm", "confirm_when", "cc_ref"], truth)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
            out = csv.writer(f, delimiter="\t", lineterminator="\n"); out.writerow(header); out.writerows(rows)
    from collections import Counter
    print(f"confirm items: {len(facts)}; by group and outcome: " + "; ".join(f"{g} {o} {c}" for (g, o), c in sorted(Counter((r[2], r[1]) for r in truth).items())))


if __name__ == "__main__":
    main()
