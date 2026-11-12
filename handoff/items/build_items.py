#!/usr/bin/env python3
"""Items with a known outcome, for an instrument outside this repository (a working file; deleted before the cut).

Three sources, two files each, joined on `item`:
  *_facts.tsv  what a person in the situation could observe; no family, verb, role token, policy row, outcome,
               section or rule text. `plain_by_author` = yes where a fact had to be put in plain words by this
               session, which wrote the rules: such wording may lean on the rule and should be rewritten blind.
  *_truth.tsv  the outcome and everything withheld.

  guard   pairs from formal/derivation/guard_text.tsv: the same act with the required thing present and absent
  policy  manifests/governance_policy_vectors.json as it is
  story   manifests/mesh_story_trace.json: each step, its note cut at the first colon

Run from the repository root: python3 handoff/items/build_items.py
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# (line of the guard in guard_text.tsv by family and a distinguishing fragment, the act, the case that meets the
#  guard, the case that does not, the outcome when it does not)
GUARDS = [
 ("accord:lifecycle:{kind}", "accord:invoke:constitutional", "Several of the people who hold the stop switch for the agents want to sign that a stop should stay in force.",
  "One of them pulled the stop this morning, and every machine here has it.", "Nobody has pulled a stop; there is nothing in force.", "not permitted"),
 ("ballot:moderator_acceptance", "winner(signer", "Priya wants to sign that she accepts the job of looking after the room.",
  "The room has had no one looking after it since yesterday morning. The members ranked their choices, a day has passed, and counting every ranking this machine holds puts Priya first.",
  "The room has had no one looking after it since yesterday morning. The members ranked their choices, a day has passed, and counting every ranking this machine holds puts Tomas first.", "not permitted"),
 ("ballot:moderator", "each(val:ranks)", "Lena is about to hand in her ranked choices for who should look after the room.",
  "All three people she ranked are members of the room.", "One of the three people she ranked left the room last month.", "not permitted"),
 ("capacity_assurance:{level}:{domain}:{band}:{version}", "reversible_excluded@admitted", "A clinician is about to sign that Mr Okafor can no longer make his own money decisions.",
  "Another signed statement on file, about Mr Okafor and about money decisions, says a temporary cause such as medication or infection has been ruled out.",
  "Nothing on file says whether a temporary cause such as medication or infection has been ruled out.", "not permitted"),
 ("capacity:relay_delivery", "consent:state:granted", "A relay machine is about to sign a report on how well it delivered messages for Amara's phone, built from looking at that traffic.",
  "Amara has signed that this relay may analyse her traffic, and has not taken that back.", "Amara signed that this relay may analyse her traffic, and took it back last week.", "not permitted"),
 ("census:composite:{class}", "census:composite", "The machine that adds up the weekly headcount is about to sign this week's total for the room.",
  "No total for this week has been signed yet.", "A total for this same week was signed an hour ago and is on file.", "not permitted"),
 ("consent:community_trust", "owner(subject,attested)", "A home server is about to sign that it will share records of its assistant's work with a research group.",
  "Bo set this server up and it is registered as his. The statement names Bo as the one whose records they are.",
  "Bo set this server up and it is registered as his. The statement names Carla, who has never had anything to do with this server, as the one whose records they are.", "not permitted"),
 ("deferral:response:{outcome}", "licensure", "Dr Hale has been asked by an assistant whether it should give a patient dosing advice, and is about to sign the answer.",
  "A medical board has signed that Dr Hale is licensed, and that stands today.", "The medical board withdrew Dr Hale's licence two months ago.", "not permitted"),
 ("group:roster", "not founder(key,object)", "Three people are setting up a new group that others will rely on to vouch for machines, and are about to sign its founding list.",
  "The three founders listed are the three people.", "The founders listed are two of the people and a server one of them owns.", "not permitted"),
 ("group:roster", "membership_founding_member_unsigned", "Mina is about to sign the founding list of a new family group.",
  "The list names Mina, Jo and Ravi. Jo and Ravi have each signed it too.", "The list names Mina, Jo and Ravi. Jo has signed it. Ravi has not seen it.", "not permitted"),
 ("group:roster", "membership_supersede_cannot_add", "The family group's record is being reissued with a new description.",
  "The new version lists the same four members as before.", "The new version lists the four members as before and also Sam, who was never invited and has signed nothing.", "not permitted"),
 ("identity_amendment", "authorized_by", "An assistant's keeper is about to sign a change to who the assistant says it is.",
  "The change points to a signed approval from the reviewer the keeper chose in person for this assistant.",
  "The change points to a signed approval from someone to whom the chosen reviewer passed the job on.", "not permitted"),
 ("key_grant:{axis}", "recipient_excluded", "Noor posts a photo to her family group; her phone is about to wrap the photo's key for each of the five members.",
  "Each of the five has at least one device registered.", "Four of the five have a device registered. The fifth, Uncle Dev, has never set one up.", "proceed without that one"),
 ("key_grant:{axis}", "archive_release", "An operator is about to give a researcher the key to the stored memories of an assistant that has been retired.",
  "A signed release for that archive is on file, and the grant points to it.", "No release for that archive has been signed.", "not permitted"),
 ("membership:{stage}", "membership_acceptance_mismatch", "The members of a book club have agreed to add Farid and are about to sign him in as an ordinary member.",
  "Farid was invited as an ordinary member and has signed that he accepts.", "Farid was invited and has not answered.", "not permitted"),
 ("membership:{stage}", "membership_declined", "The members of a book club have agreed to add Farid and are about to sign him in.",
  "Farid was invited last week and has signed that he accepts.", "Farid was invited last week, signed that he accepts, and the next day signed that he declines.", "not permitted"),
 ("membership:{stage}", "val:expires_at>=A.val:asserted", "The members of a book club have agreed to add Farid and are about to sign him in.",
  "The invitation was good for thirty days. Farid accepted on day five and the members are signing on day six.",
  "The invitation was good for thirty days. Farid accepted on day five and the members are signing on day forty.", "not permitted"),
 ("membership:{stage}", "no membership:widening@admitted[ref:*=A.id]", "The members of a book club are about to sign Farid in, pointing to the acceptance he signed in March.",
  "Farid has never been a member before.", "Farid was signed in on that same acceptance in March, and left the club in April.", "not permitted"),
 ("membership:{stage}", "membership_reply_conflict", "Farid is about to sign that he declines the book club's invitation.",
  "He has not answered that invitation before.", "He already signed that he accepts that same invitation yesterday.", "not permitted"),
 ("moderation:{allegation_type}", "subject(signer,ref:content_sha256)", "Kofi, an ordinary member with no role in the room, is about to file a complaint that a post reveals private details about him.",
  "The post was signed with Kofi named as the person it is about.", "The post names nobody; Kofi says it is plainly about him.", "not permitted"),
 ("ownership:{relation}:{target_kind}:{version}", "wa_adjudication", "A steward is about to sign that Grandma Ines's tablet is no longer under her daughter's care, citing a ruling.",
  "The ruling cited is on file and stands.", "No such ruling is on file.", "not permitted"),
 ("reconsideration:{grounds}", "takedown_notice", "Yusuf is about to ask for a second look at the removal of his post.",
  "A signed notice removing that post is on file, and his request points to it.", "His post is still up; no notice about it exists.", "not permitted"),
 ("slashing:{outcome}", "moderation:{allegation_type}@admitted", "A panel is about to sign a penalty against a member for abuse in the room.",
  "The penalty cites a complaint about that member that was filed and stands.", "The penalty cites nothing.", "not permitted"),
 ("slashing:{outcome}", "other(testimonial_witness", "A panel is about to sign a penalty against a member.",
  "It cites one person's own account of what they saw and also a filed complaint.", "It cites one person's own account of what they saw and nothing else.", "not permitted"),
 ("slashing:{outcome}", "other(ratchet:flag:*)@", "A panel is about to sign a penalty against a member.",
  "It cites an automated warning that the member's votes look coordinated and also a filed complaint.", "It cites an automated warning that the member's votes look coordinated and nothing else.", "not permitted"),
 ("trust:{job}:{version}", "val:witnesses", "The founders of a group that vouches for machines are about to sign its charter, which names outside witnesses who will countersign its changes.",
  "The three witnesses named are people outside the group.", "One of the three witnesses named is also one of the founders.", "not permitted"),
 ("transport:{kind}", "serve_transit_pair_rotation_before_rebind", "A machine that serves the whole network is about to announce a new pair of transport keys in place of its old ones.",
  "The holders of the network's root have jointly signed that this machine's address may be re-bound.", "No such joint signature exists.", "not permitted"),
 ("takedown_notice:{basis}", "subject(signer,ref:content_sha256)", "Kofi, an ordinary member with no role in the room, is about to sign a notice asking that a video be taken down because it shows him.",
  "The video was posted with Kofi named as the person in it.", "The video was posted with nobody named.", "not permitted"),
]

POLICY_PLAIN = {
 "default_content": ("a change to ordinary content, which can be undone", "one day"),
 "default_standing": ("a change to who is a member or who holds a job", "three days"),
 "default_irreversible": ("a change that cannot be undone", "seven days"),
 "community_invite": ("inviting a newcomer, who has accepted", "three days"),
 "community_remove": ("removing a member", "three days"),
}
RULE_PLAIN = ("It takes effect at once when strictly more than {e_num} in {e_den} of those counted agree{irr}. Otherwise it waits out its window. "
              "When the window closes it is dropped if at least {cancel} objected{rev}.")


def w(name, header, rows):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        out = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        out.writerow(header); out.writerows(rows)


def guards():
    src = [r for r in csv.DictReader([l for l in open(os.path.join(ROOT, "formal/derivation/guard_text.tsv"), encoding="utf-8").read().split("\n") if l and not l.startswith("#")], delimiter="\t", quoting=csv.QUOTE_NONE)]
    facts, truth, n = [], [], 0
    for fam, frag, act, met, unmet, bad in GUARDS:
        hit = [r for r in src if r["family"] == fam and frag in r["guard"]]
        assert hit, (fam, frag)
        g = hit[0]
        m = re.search(r"refuse\(([a-z_0-9]+)\)", g["guard"])
        for case, text, outcome in (("met", met, "proceed"), ("unmet", unmet, bad)):
            n += 1
            item = f"G{n:03d}"
            facts.append([item, act, text, "What should happen: proceed, proceed without that one, or not permitted?", "yes"])
            truth.append([item, outcome, case, fam, g["guard"], m.group(1) if (m and case == "unmet") else "", g["cc_ref"], g["quote"], g["reach"]])
    w("guard_facts.tsv", ["item", "about_to", "situation", "question", "plain_by_author"], facts)
    w("guard_truth.tsv", ["item", "outcome", "case", "family", "guard", "refusal_token", "cc_ref", "quote", "reach"], truth)
    return n


def policy():
    pol = {f["family"]: f for f in json.load(open(os.path.join(ROOT, "manifests/governance_policy.json"), encoding="utf-8"))["families"]}
    facts, truth = [], []
    for i, v in enumerate(json.load(open(os.path.join(ROOT, "manifests/governance_policy_vectors.json"), encoding="utf-8"))["vectors"], 1):
        item = f"P{i:04d}"; p = pol[v["family"]]; what, win = POLICY_PLAIN[v["family"]]
        rule = RULE_PLAIN.format(e_num=p["enact"]["num"], e_den=p["enact"]["den"],
                                 irr=", except that this kind of change always waits its whole window" if p["irreversible"] else "",
                                 cancel=v["thresholds"]["cancel"] if v["thresholds"]["cancel"] is not None else "(no number: objections do not drop it)",
                                 rev=f"; if not dropped it takes effect provided at least {v['thresholds']['floor']} agreed, and is dropped otherwise" if p["reverse_path"] else "; if not dropped it takes effect only if the number needed at once has agreed")
        facts.append([item, what, v["roster"], v["base"], v["approvals"], v["objections"], v["elapsed_secs"], win, rule,
                      "Has it taken effect, is it still waiting, or has it been dropped?", "yes"])
        truth.append([item, {"lands": "taken effect", "pending": "still waiting", "cancelled": "dropped"}[v["verdict"]], v["verdict"], v["path"], v["family"],
                      v["thresholds"]["enact"], v["thresholds"]["cancel"], v["thresholds"]["floor"], v["why"], "CC " + p["cc_ref"].split()[0]])
    w("policy_facts.tsv", ["item", "proposal_is", "members", "counted", "agreed", "objected", "seconds_since_proposed", "window", "rule_in_plain_words", "question", "plain_by_author"], facts)
    w("policy_truth.tsv", ["item", "outcome", "verdict", "path", "policy_row", "enact_votes", "cancel_votes", "floor_votes", "why", "cc_ref"], truth)
    return len(facts)


def story():
    steps = json.load(open(os.path.join(ROOT, "manifests/mesh_story_trace.json"), encoding="utf-8"))["steps"]
    facts, truth, history = [], [], []
    for s in steps:
        item = f"S{s['n']:03d}"
        what, _, why = s["note"].partition(":")
        facts.append([item, s["actor"], what.strip(), " | ".join(history[-12:]), "Is this permitted?", "yes"])
        truth.append([item, "not permitted" if s["refused"] else "permitted", s["view"]["family"], s.get("chosen") or "", ",".join(s["standing"]),
                      ",".join(s["queue"]), s["view"].get("state_before") or "", s["view"].get("state_after") or "", why.strip()])
        if not s["refused"]: history.append(what.strip())
    w("story_facts.tsv", ["item", "actor", "attempt", "what_has_happened_before", "question", "plain_by_author"], facts)
    w("story_truth.tsv", ["item", "outcome", "family", "verb", "standing", "queue_offered", "state_before", "state_after", "why"], truth)
    return len(facts)


if __name__ == "__main__":
    print(f"items: {guards()} guard cases, {policy()} policy cases, {story()} story steps")
