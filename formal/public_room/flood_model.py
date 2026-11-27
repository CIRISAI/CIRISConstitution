#!/usr/bin/env python3
"""A flood against a public room, by where it can land. A work in progress, not yet a gated model.

The rule the text gives (CC 4.4.3.34, CC 1.13, CC 3.2): a node carries and shows a row only where its author is in the
node's trust set, and the receiver checks its rates before any cryptography (per sender key, per link, node-wide).
So a flood has four places to land, and this file prices each: the wire, the rate check, the signature check, the store.

Every number below is a PARAMETER. Those marked `assumed` are not fixed by the text; the result is stated as a
function of them, and --check asserts only what holds for every value tried.
  python3 formal/public_room/flood_model.py            prints the tables
  python3 formal/public_room/flood_model.py --check    asserts the findings
"""
import sys

P = dict(
    row_bytes=3900,            # one signed row: the Appendix B.3 statement is 3,864 bytes
    sign_per_core_s=3000,      # assumed: composite signatures one attacker core makes a second
    verify_per_core_s=5000,    # assumed: composite verifications one defender core does a second
    drop_per_core_s=2_000_000, # assumed: frames a core refuses at the rate check, before any cryptography
    node_ingress_bps=1e9,      # assumed: one holder's inbound link
    node_verify_budget_s=200,  # assumed: the node-wide ceiling of rows a node lets through to the signature check each second
    per_sender_budget_s=2,     # assumed: rows a second one sender key is let through
)


def attacker_cost(rows, p=P):
    """What minting and sending `rows` signed rows costs."""
    return {"core_hours": rows / p["sign_per_core_s"] / 3600, "bytes": rows * p["row_bytes"]}


def outsider_flood(rows_per_s, seconds, keys, p=P):
    """Rows by keys outside the node's trust set, aimed at one node."""
    wire = min(rows_per_s, p["node_ingress_bps"] / 8 / p["row_bytes"])            # what the link can deliver
    to_crypto = min(wire, p["node_verify_budget_s"], keys * p["per_sender_budget_s"])
    return {
        "arrive_per_s": wire,
        "saturates_link": rows_per_s >= p["node_ingress_bps"] / 8 / p["row_bytes"],
        "drop_cores": (wire - to_crypto) / p["drop_per_core_s"],
        "verify_cores": to_crypto / p["verify_per_core_s"],
        "stored_rows": 0,                                                         # the author is in no trust set: carried for nobody
        "shown_rows": 0,
        # an honest stranger's first row competes for the same node-wide ceiling (CC 5.4.6: "about the budget over the flood's rate")
        "stranger_through": min(1.0, p["node_verify_budget_s"] / max(wire, 1e-9)),
    }


def insider_flood(rows_per_s, seconds_until_cut, readers, p=P):
    """Rows by a key INSIDE a room (a vouched member), until the room removes it or readers cut the edge it came through."""
    through = min(rows_per_s, p["per_sender_budget_s"])
    rows = through * seconds_until_cut
    return {"rows_stored_per_node": rows, "bytes_per_node": rows * p["row_bytes"], "bytes_all": rows * p["row_bytes"] * readers,
            "after_cut_per_s": 0}                                                 # one removal or one edge withdrawn: nothing more is carried


def serve_through(flood_bps, holders_on_roster, off_roster_holders, p=P):
    """A bandwidth flood aimed at the holders an attacker can name. A public room's roster is public, so every member
    node is a target; a holder that is on no roster (a serve node or a cache holding self-authenticating rows) is not."""
    per_target = flood_bps / max(holders_on_roster, 1)
    roster_up = per_target < p["node_ingress_bps"]
    return {"per_target_bps": per_target, "roster_holders_reachable": roster_up,
            "room_readable": roster_up or off_roster_holders > 0,
            "aggregate_needed_bps": flood_bps}


def read_demand(lookups_per_s, node_serves_per_s):
    return {"holders_needed": -(-lookups_per_s // node_serves_per_s)}


def main():
    B = 1_000_000_000
    c = attacker_cost(B)
    print("minting a billion rows: %.0f core-hours, %.1f TB" % (c["core_hours"], c["bytes"] / 1e12))
    print()
    print("OUTSIDER FLOOD at one node (rows by keys in no trust set)")
    print("%12s %10s | %10s %9s %10s %12s %7s %8s" % ("rows/s", "keys", "arrive/s", "link full", "drop cores", "verify cores", "stored", "stranger"))
    out = []
    for rate in (1e3, 1e5, 1e7):
        for keys in (1, 1e3, 1e9):
            o = outsider_flood(rate, 3600, keys); out.append((rate, keys, o))
            print("%12.0f %10.0f | %10.0f %9s %10.4f %12.4f %7d %8.4f" % (rate, keys, o["arrive_per_s"], o["saturates_link"], o["drop_cores"], o["verify_cores"], o["stored_rows"], o["stranger_through"]))
    print()
    print("INSIDER FLOOD (a vouched member), by how long until the cut; 1,000 readers")
    ins = []
    for secs, label in ((60, "1 minute"), (3600, "1 hour"), (259200, "72 hours")):
        i = insider_flood(1e6, secs, 1000); ins.append(i)
        print("%10s: %9.0f rows and %8.1f MB a node, %8.1f GB in all; after the cut %d/s" % (label, i["rows_stored_per_node"], i["bytes_per_node"] / 1e6, i["bytes_all"] / 1e9, i["after_cut_per_s"]))
    print()
    print("BANDWIDTH FLOOD at the room's named holders (1 Gbit/s each)")
    srv = []
    for flood in (1e9, 1e10, 1e11):
        for members, off in ((10, 0), (100, 0), (10, 3)):
            s = serve_through(flood, members, off); srv.append((flood, members, off, s))
            print("%6.0f Gbit/s at %3d member nodes, %d off-roster holders: member nodes %s, room %s" % (flood / 1e9, members, off, "up" if s["roster_holders_reachable"] else "saturated", "readable" if s["room_readable"] else "dark"))
    print()
    print("READ DEMAND: %d holders for 100,000 lookups/s at 2,000 a node" % read_demand(100_000, 2_000)["holders_needed"])
    if "--check" in sys.argv:
        # 1. An outsider flood stores and shows nothing at any rate and any number of keys.
        assert all(o["stored_rows"] == 0 and o["shown_rows"] == 0 for _, _, o in out)
        # 2. Its signature work is bounded by the node's own ceiling, whatever the flood: never more than the ceiling's cores.
        assert all(o["verify_cores"] <= P["node_verify_budget_s"] / P["verify_per_core_s"] + 1e-12 for _, _, o in out)
        # 3. One sender key gets through no more than its own budget, so a flood needs keys, and keys do not raise the node ceiling.
        assert outsider_flood(1e7, 1, 1)["verify_cores"] < outsider_flood(1e7, 1, 1e9)["verify_cores"] <= P["node_verify_budget_s"] / P["verify_per_core_s"]
        # 4. What is NOT bounded: an honest stranger's chance falls as the ceiling over the flood's rate.
        assert outsider_flood(1e7, 1, 1e9)["stranger_through"] < 0.01
        # 5. An insider's damage is its per-sender budget times the time to the cut, and nothing after it.
        assert ins[0]["rows_stored_per_node"] == P["per_sender_budget_s"] * 60 and all(i["after_cut_per_s"] == 0 for i in ins)
        # 6. A bandwidth flood is survived by aggregate ingress above it, or by one holder the attacker cannot name.
        get = lambda f, m, o: next(s for ff, mm, oo, s in srv if (ff, mm, oo) == (f, m, o))
        assert not get(1e11, 10, 0)["room_readable"] and get(1e11, 10, 3)["room_readable"] and get(1e10, 100, 0)["room_readable"]
        print("check: ok")


if __name__ == "__main__":
    main()
