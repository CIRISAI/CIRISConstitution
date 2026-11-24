#!/usr/bin/env python3
"""
check_binding_carriage.py: one command, exit 0 or 1.

    python3 -I formal/binding_carriage/check_binding_carriage.py

One process, capped at 2 GiB of address space. Every enumeration is bounded and its bound is printed. Every verdict
is symbolic (model.py), and a run is a run over that bound, never a proof.

  1  authenticity inside        no coalition that lacks P's binding key makes A take a room key to be P's
  2  deniability outside        what A ends up holding convinces nobody that P took part; A can show that R's holder named P
  3  no signature without the binding   the carriage in every delivery order, with loss, repeats and a wiped network
  4  every flow restarts        from every reachable state the admission can still be signed
  5  a second voice             who has to fail to check before one person holds two voices
  6  a count of persons waits   two nodes with the same rows never conclude different counts
  7  what a relay learns        neither the room, nor the person from an envelope addressed to a room key
  8  against formal/causal_kernel/roomkey.py   the answers the two models share

Each property is followed by its planted breaks, which the same check must catch, and by the states it says are
reached. A line marked FINDING is a place where the rule as given does not do what its sentence says: the check
requires the finding to be reproduced, so that a change to the model that hides it fails here.
"""
import itertools
import os
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import model as M   # noqa: E402

OK = True
N = {"properties": 0, "plants": 0, "witnesses": 0, "findings": 0}


def line(good, text, kind="properties"):
    global OK
    OK &= bool(good)
    N[kind] += 1
    tag = {"properties": "holds ", "plants": "caught", "witnesses": "reached", "findings": "FINDING"}[kind]
    print("   %-7s %s" % (tag if good else "FAIL", text))


def main():
    t0 = time.time()

    # ---------------------------------------------------------------------------------------------------
    print("1  authenticity inside (five sessions of A, P answering every challenge the coalition can form, in two rooms)")
    goals, honest, tried = M.authenticity(M.TEXT)
    # Inv_AuthenticInside
    line(not goals, "the coalition holds every secret but P's binding key, P's roster key and A's own: of %d confirmations it can put "
         "before A, none makes A take a key to be P's that P did not prove to A (forged, misaddressed, stolen: %s)" % (tried, sorted(goals) or "none"))
    line(honest > 0, "P's own answer to A's own challenge is accepted (%d): the check is reached" % honest, "witnesses")
    for change, want, text in (
            ({"keyed": False}, "forged", "the confirmation is not keyed by the challenge's secret"),
            ({"challenge_to": "roomkey"}, "forged", "the challenge is made to the room key and not to the person's binding key"),
            ({"check_person": False}, "forged", "A does not check that the opened person is the one it challenged"),
            ({"check_commit": False}, "stolen", "A does not check the opening against the seat row's commitment"),
            ({"info": ("room", "pkB")}, "forged", "the info binds neither the room key nor its commitment, nor the addressee"),
            ({"info": ("room", "R", "commit", "pkB")}, "misaddressed", "the info does not bind the addressee's room key")):
        g, _, _ = M.authenticity(M.rule(**change))
        line(want in g, "%s: %s, e.g. %s; %s" % (text, want, g.get(want, ("-", "-"))[0], g.get(want, ("-", "-"))[1]), "plants")
    ab = M.info_ablation()
    as_stated = all((("forged" in g) == ({"R", "commit"} <= d)) and (("misaddressed" in g) == ("A" in d)) and "stolen" not in g for d, g in ab.items())
    # Inv_InfoBindsAddressee
    line(as_stated, "the info, with each of the %d subsets of its five members left out: a key is forged exactly when the room key and the "
         "commitment are both left out, and an answer is misaddressed exactly when the addressee is left out. Within this bound the room "
         "and the binding key's thumbprint bind nothing the commitment does not" % len(ab))
    g, _, _ = M.authenticity(M.TEXT, roster_key_leaked=True)
    line("forged" in g, "the stated edge of the property: a coalition that holds a roster key of P places an occurrence of P with a "
         "binding key of its own, A challenges that key, and the key is forged. The binding key is as good as the roster that states it", "witnesses")

    # ---------------------------------------------------------------------------------------------------
    print("2  deniability outside (one exchange, A's whole view, every secret of A handed over)")
    d = M.deniability(M.TEXT)
    # Inv_DeniableOutside
    line(d["from_a_and_r"], "every term A holds follows from A's own secrets and what a holder of R's secret says (the seat row and the opening)")
    line(d["without_p"] and not d["convinces"], "the same view, up to the fresh names, is made by A and a party that is not P; no term of it needs a key of P's identity")
    # Inv_HolderNamedPerson
    line(d["r_named_p"], "A can show that R's holder named P: the seat row cannot be made without R's secret, and the opening opens its commitment to P")
    d2 = M.deniability(M.rule(claim_signed=True))
    line(d2["convinces"] and not d2["without_p"], "the claim carries P's identity signature: a third party is then convinced that P took part", "plants")
    d3 = M.deniability(M.rule(commit_in_seat_row=False))
    line(not d3["r_named_p"], "the commitment travels beside the seat row and not inside what R signs: A can then show nothing about whom R's holder named", "plants")
    line(M.live_judge(), "the stated limit, as a run: a third party forms the challenge and A relays it. A cannot have keyed the confirmation, "
         "and the third party is convinced", "witnesses")

    # ---------------------------------------------------------------------------------------------------
    print("3  no signature without the binding, and 4  every flow restarts (the carriage as a state machine)")
    runs = {}
    for name in ("widening", "founding2", "founding3"):
        cfg = M.config(name)
        r = runs[name] = M.explore(cfg)
        n, bad = M.misdelivery(cfg)
        who = {"widening": "a joiner, the inviter, a second cosigner and the duty holder", "founding2": "two founders", "founding3": "three founders"}[name]
        bound = "%d exchanges, at most %d lost pending secrets and %d wipes of the network" % (len(cfg["ex"]), cfg["L"], cfg["W"])
        # Inv_NoSignatureWithoutBinding
        line(r["unsafe"] is None, "%s (%s; %s): %d states. In every one, a cosign, an acknowledgement or a founder's signature stands on a "
             "binding its signer checked against its own live challenge, and the admission stands on all of them" % (name, who, bound, r["states"]))
        # Inv_OpenedOnlyByAddressee
        line(bad == 0 and r["wrong_accepts"] == 0, "%s: %d pairs of a message and a party or a pending secret. A claim and a challenge are opened by the "
             "party they were made for and no other, and a confirmation is accepted against the challenge it answers and no other" % (name, n))
        # Inv_FlowRestarts
        line(r["stuck"] == 0, "%s: from every one of the %d states the admission can still be signed, using what the parties keep for good and "
             "the rows they can read" % (name, r["states"]))
    print("      planted breaks are run with one lost secret and one wipe")
    w, f2, f3 = runs["widening"]["facts"], runs["founding2"]["facts"], runs["founding3"]["facts"]
    for fact in ("admitted", "admitted after a lost secret", "admitted after the network lost everything", "a stale confirmation is dropped",
                 "a repeated confirmation changes nothing", "a pending challenge is sent again",
                 "every cosigner has signed, the duty holder holds no binding, and the admission waits"):
        line(w[fact], "widening: " + fact, "witnesses")
    line(f2["admitted"] and f2["admitted after a lost secret"] and f2["all but one signed and the admission waits"],
         "founding, two founders: founded; founded after a lost secret; one founder has signed and the record waits for the other", "witnesses")
    line(f3["admitted"] and f3["admitted after a lost secret"] and f3["all but one signed and the admission waits"],
         "founding, three founders: founded; founded after a lost secret; two have signed and the record waits for the third", "witnesses")
    for plant, cfgname, text in (
            ("sign_on_claim", "widening", "a cosigner signs once it has read the claim"),
            ("sign_on_claim", "founding2", "a founder signs once it has read the other's claim"),
            ("hearsay", "widening", "a cosigner takes the inviter's word that the binding is good"),
            ("final_without_ack", "widening", "the admission does not name the duty holder's acknowledgement"),
            ("confirm_not_keyed", "widening", "the confirmation is not keyed, so one that answers a lost challenge is accepted")):
        r = M.explore(M.config(cfgname, L=1, W=1), plant=plant, stop_at_unsafe=True)
        line(r["unsafe"] is not None, "property 3, %s (%s): %s" % (text, cfgname, " > ".join(r["unsafe"] or ["not caught"])), "plants")
    for plant, cfgname, text in (
            ("claim_once", "widening", "the joiner sends each claim once"),
            ("challenge_once", "widening", "an addressee never issues a second challenge"),
            ("challenge_once", "founding2", "a founder never issues a second challenge"),
            ("refuse_after_bad", "widening", "an addressee refuses a room key for good after a confirmation it cannot open")):
        r = M.explore(M.config(cfgname, L=1, W=1), plant=plant)
        line(r["stuck"] > 0 and r["unsafe"] is None, "property 4, %s (%s): %d states from which the admission is never signed, e.g. %s"
             % (text, cfgname, r["stuck"], " > ".join(r["stuck_path"] or ["not caught"])), "plants")

    # ---------------------------------------------------------------------------------------------------
    print("5  a second voice (a second admission of two to four signers and, where seated, a duty holder)")
    pres = M.presentable()
    line({k for k, v in pres.items() if v} == {("P", "P"), ("Z", "Z")} and pres[("P", "P")] == "P",
         "what P can make a checking member hold for its second room key, over nine pairs of the person committed and the person claimed: "
         "a binding that names P, and nothing that names an honest person. A binding that names an accomplice Z is one Z made")
    for reading in M.READINGS:
        for dh in (False, True):
            n, seated, with_checker = M.second_voice_sequential(reading, dh)
            # Inv_SecondVoiceOnlyUnchecked
            line(seated > 0 and with_checker == 0 and seated < n,
                 "reading '%s', %s, the first seat held with its binding by every signer: of %d second admissions, %d are seated, and none of those has a signer who checked"
                 % (reading, "a duty holder seated" if dh else "no duty holder", n, seated))
    n, seated, with_checker = M.second_voice_sequential("as written", True)
    line(seated > 0, "the stated cost: a second voice is seated where every signer, and the duty holder, did not check (%d cases)" % seated, "witnesses")
    n, seated, with_checker = M.second_voice_sequential("as written", True, plant="ignore_seated")
    line(with_checker > 0, "a checking member signs although the binding names a person it holds as seated: %d second voices with a checker among the signers" % with_checker, "plants")
    sv = {(rd, dh): M.second_voice(rd, dh) for rd in M.READINGS for dh in (False, True)}
    a, s, hd = "as written", "as written, strict", "held"
    lost, late = "a checker without the first binding", "a checker the first seat had not reached"
    line(sv[(a, False)]["classes"][lost] > 0 and sv[(a, True)]["classes"][lost] > 0,
         "as written (CC 3.1.3.2: 'MUST NOT cosign one whose binding names a person already seated'), a checking signer that sees the first seat and "
         "lacks its binding cannot tell, and signs: %d of %d second admissions are seated this way with no duty holder, %d of %d with one. "
         "Under the strict reading (it waits until it holds the binding of every seated key) there are %d"
         % (sv[(a, False)]["classes"][lost], sv[(a, False)]["cases"], sv[(a, True)]["classes"][lost], sv[(a, True)]["cases"],
            sv[(s, False)]["classes"][lost] + sv[(s, True)]["classes"][lost]), "findings")
    line(sv[(s, False)]["classes"][lost] == 0 and sv[(s, True)]["classes"][lost] == 0, "the strict reading closes that case in every second admission run")
    line(sv[(s, True)]["classes"][late] > 0 and sv[(s, True)]["seated with a checking duty holder"] > 0,
         "two admissions of one person at once: every signer checks, the first seat has reached none of them, and both are seated. "
         "Under either reading of the text %d second admissions are seated with a checker among the signers, %d of them with a checking duty holder. "
         "The sentence 'a person gains a second voice only where every signer of that admission failed to check' does not hold for two admissions at once"
         % (sv[(s, True)]["classes"][late], sv[(s, True)]["seated with a checking duty holder"]), "findings")
    line(sv[(hd, True)]["seated with a checking duty holder"] == 0 and sv[(hd, False)]["classes"][late] > 0,
         "a reading the text does not state ('held': a checker refuses a person it holds another binding of, seated or not): with a checking duty "
         "holder, who holds every binding, no second voice is seated in %d cases; with no duty holder, two admissions at once whose checking "
         "signers share no binding still seat one (%d)" % (sv[(hd, True)]["cases"], sv[(hd, False)]["classes"][late]))

    # ---------------------------------------------------------------------------------------------------
    print("6  a count of persons waits (five seated room keys, one shared by two colluders; two nodes with the same rows)")
    c = M.count_world()
    # Inv_StallNotFork
    line(c["fork"] == 0 and c["differ and neither waits"] == 0 and c["missing not as stated"] == 0,
         "%d pairs of holdings over %d ways to vote: two nodes that both count agree (%d pairs, %d differ); two nodes that hold different "
         "bindings never both count (%d); a node that waits names exactly the keys it lacks"
         % (c["pairs"], 3 ** len(M.COUNT_KEYS), c["both counted"], c["fork"], c["differ and neither waits"]))
    line(c["both counted"] > 0 and c["one waits"] > 0 and c["both wait"] > 0, "both count (%d pairs), one counts and one waits (%d), both wait (%d)"
         % (c["both counted"], c["one waits"], c["both wait"]), "witnesses")
    p = M.count_world(r=M.rule(check_commit=False))
    line(p["fork"] > 0, "no check of the opening against the commitment: two nodes that each hold every binding count differently in %d pairs, e.g. %s against %s"
         % (p["fork"], p["first fork"][2], p["first fork"][4]), "plants")
    p = M.count_world(count_bound_only=True)
    line(p["fork"] > 0 and p["differ and neither waits"] > 0, "a node counts over the bindings it has and does not wait: %d pairs count differently" % p["fork"], "plants")
    e = M.count_world(equivocate=True, two_rows="any")
    line(e["fork"] > 0, "the shared key has TWO seat rows, one committed to each colluder, and both nodes hold both rows. If a binding is taken when it "
         "opens either commitment, two nodes that each hold every binding count differently in %d pairs. The text says the seat row carries 'a commitment' "
         "and does not say what a second seat row of one room key does" % e["fork"], "findings")
    v = M.count_world(equivocate=True, two_rows="void")
    line(v["fork"] == 0 and v["both counted"] == 0 and not v["a full holding exists"],
         "if a room key with two different commitments takes no binding at all, no pair forks, and no node ever counts (%d pairs, all waiting): "
         "a stall at every node, which the holder of that key can cause alone" % v["pairs"])

    # ---------------------------------------------------------------------------------------------------
    print("7  what a relay learns (the ten envelopes of one widening; the relay holds no row of the room and no secret)")
    each, whole = M.relay()
    rk = {k: x for k, x in each.items() if k != "the invitation"}
    # Inv_RelayLearnsNeither
    line(not whole[1] and not whole[2] and all(not x[0] and not x[1] for x in rk.values()),
         "from all %d envelopes together the relay derives neither the room nor any nonce or challenge secret; from the %d envelopes addressed to "
         "a room key it derives no person" % (len(each), len(rk)))
    line(each["the invitation"][0] == frozenset({"P"}) and not each["the invitation"][1],
         "the invitation is sealed to the invitee's identity key, since no room key of theirs exists yet. Unless the key exchange hides the key a "
         "seal was made to, the relay learns that this person was sent a sealed envelope, and nothing of which room", "findings")
    each2, whole2 = M.relay(key_private=True)
    line(not whole2[0] and not whole2[1], "if the key exchange hides the key a seal was made to (assumed, not checked), the relay derives no person from any envelope")
    for plant, text, want in (("claim_in_clear", "the claim travels outside the seal", (True, True)),
                              ("challenge_bare", "the challenge travels outside an envelope", (True, False)),
                              ("info_in_header", "the confirmation's info travels beside it", (True, True)),
                              ("address_by_record", "an envelope is addressed by the room key's record, which names its room", (False, True))):
        e, _ = M.relay(plant)
        got = (any(x[0] for k, x in e.items() if k != "the invitation"), any(x[1] for x in e.values()))
        line(got == want, "%s: the relay learns %s" % (text, " and ".join(n for n, g in zip(("the person", "the room"), got) if g)), "plants")

    # ---------------------------------------------------------------------------------------------------
    print("8  against formal/causal_kernel/roomkey.py, which takes a binding as a given fact")
    sys.path.insert(0, os.path.join(HERE, "..", "causal_kernel"))
    import roomkey as RK   # noqa: E402
    grid = [(r_, k, p_, n_) for r_ in ("g", "g2") for k in ("a", "b") for p_ in ("P", "Q") for n_ in ("n1", "n2")]
    same = sum((RK.commit(*x) == RK.commit(*y)) == (M.commitment(*x) == M.commitment(*y)) for x in grid for y in grid)
    line(same == len(grid) ** 2, "the commitment: equal in one model exactly when equal in the other, over %d pairs of (room, key, person, nonce)" % len(grid) ** 2)
    forged, cases, _ = RK.authentic_inside("two_encap", ("A", "B", "C", "J"))
    den = RK.deniable_outside("two_encap")
    line(forged == 0 and not goals and den["prove something"] == 0 and not d["convinces"] and RK.EXPECT["two_encap"] == (True, True),
         "the planned binding: roomkey.py says who can make it (0 of %d coalitions forge, 0 of %d prove something); here the same two answers follow from the terms" % (cases, den["coalitions"]))
    line(RK.EXPECT["identity_sig"] == (True, False) and d2["convinces"] and not M.authenticity(M.rule(claim_signed=True))[0],
         "an identity signature: authentic and not deniable in both")
    n = bad = 0
    truth = {"k:A0": "A", "k:A1": "A", "k:B0": "B", "k:C0": "C"}
    keys = list(truth)
    subsets = [frozenset(x) for k in range(len(keys) + 1) for x in itertools.combinations(keys, k)]
    for votes in itertools.product(("yes", "no", None), repeat=len(keys)):
        S, pr = RK._fold_world(keys, votes)
        for hset in subsets:
            held = {k: truth[k] for k in hset}
            theirs = RK.person_tally(S, pr, held)
            mine = M.person_count(dict(zip(keys, votes)), held, keys=tuple(keys))
            n += 1
            bad += (theirs[0] == "missing") != (mine[0] == "waits") or theirs[1:] != mine[1:]
    line(bad == 0, "a count of persons: roomkey.py's tally over the kernel's rows and this model's count give the same answer in %d cases "
         "(81 ways to vote, 16 sets of bindings held)" % n)
    col = RK.colluding_binders()
    line(col["the two honest nodes count differently"] > 0 and col["with the commitment, count differently"] == 0 and c["fork"] == 0,
         "two colluders and a shared key: a fork without the commitment and a wait with it, in both")
    n = bad = 0
    for members in (3, 4, 5, 6, 7):
        table = RK.second_voice(members)
        need = min(k for _, k, seated, _ in table if seated)      # the room's own count, read from the kernel
        for _, k, seated, _ in table:
            n += 1
            here = k >= need and M.decide("as written", 0, 1, 1) == "sign"     # `need` signers drawn from the k who do not check
            bad += here != seated or M.decide("as written", 1, 1, 1) != "refuse"
    line(bad == 0, "a second voice after the first is seated and held: seated in roomkey.py exactly when the members who do not check reach the room's count, "
         "and here a checking signer refuses (%d cases). roomkey.py runs no case where the first seat or its binding has not reached a signer" % n)

    print("RESULT: %s in %.0fs: %d properties, %d planted breaks caught, %d states reached as stated, %d findings reproduced"
          % ("ok" if OK else "FAILED", time.time() - t0, N["properties"], N["plants"], N["witnesses"], N["findings"]))
    return 0 if OK else 1


if __name__ == "__main__":
    sys.exit(main())
