#!/usr/bin/env python3
"""The shaped frame, A against B: the link MDU against a constant below it, at the same byte rate (CC 5.4.3).

Arm A is the frame as pinned: the link's channel payload MDU, 16,272 B on a TCP link. Arm B is a
constant of the Part, 1,400 B before the link seal with the frame header included, or the MDU where
that is smaller. Two sensitivity arms sit beside B at the two sizes the IETF names as floors: 1,280 B,
the smallest link MTU IPv6 permits (RFC 8200), and 1,200 B, the smallest datagram QUIC requires a path
to carry (RFC 9000). Every arm runs at the class byte rate of the fleet table, so the cost, the cover
volume and what an observer of the wire sees (one constant-size Poisson stream at rate λ) are the same
in every arm by construction; what differs is how often a frame leaves.

What is computed, per class and per arm:

  λ and the gap        frames a second, λ = rate ÷ frame; the mean gap 1/λ, which is the mean wait of a
                       row enqueued at a random instant, since the Poisson timer is memoryless
  first contact        k sequential waits, one per handshake step that crosses the shaped link, as an
                       Erlang-k: mean, 95th percentile, and the chance the shaped part fits the target;
                       k = 7 reproduces the ~40 s edge measured on a home-class peer of the canonical
  the ρ budget         real frames a window admits, ceil(ρ·λ·W), and the real bytes those frames carry
  rows                 frames per row, padding waste and transit time for a local-tier row, a
                       hybrid-signed federation row, an onion packet and the largest shaped row
  overhead and CPU     wire bytes per payload byte, and seals a second at the eight-link bound

`--check` asserts the readings the text will carry. Standard library only; nothing random.

  python3 -I formal/transport_tiers/frame_ab.py
  python3 -I formal/transport_tiers/frame_ab.py --check
"""
import math, sys

ARMS = {"A: MDU": 16_272, "B: 1,400": 1_400, "  1,280 (RFC 8200)": 1_280, "  1,200 (RFC 9000)": 1_200}
CLASSES = {"server": (7_000, 600), "home": (2_800, 600), "phone-wifi": (1_400, 600), "phone-cellular": (350, 3_600)}
RHO = 0.5
FRAME_HEADER_B = 8          # the shaped frame header, inside the 1,400
AEAD_TAG_B = 16             # the frame's own seal tag
LINK_SEAL_B = 25            # the E1 transit seal around the frame, on the wire and outside the constant
PACKET_HEADER_B = 107       # the transport packet's header and token around each frame (edge's measurement, 2026-11-08)
PROOF_B = 83                # the proof the receiver returns per packet
ROWS = {"local-tier row": 500, "federation row (hybrid-signed)": 4_000, "onion packet": 15_296, "largest shaped row": 65_536}
HANDSHAKE_STEPS = (2, 4, 7)
TARGET_S = 30.0             # Eric's first-contact target
UNSHAPED_BASE_S = 17.5      # request-seen with no shaping on the path, midpoint of the 15 to 20 s edge measured


def erlang_cdf(k, lam, t):
    if t <= 0:
        return 0.0
    x = lam * t
    s, term = 0.0, 1.0
    for i in range(k):
        if i:
            term *= x / i
        s += term
    return min(1.0, max(0.0, 1.0 - math.exp(-x) * s))


def erlang_quantile(k, lam, p):
    lo, hi = 0.0, 1.0
    while erlang_cdf(k, lam, hi) < p:
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if erlang_cdf(k, lam, mid) < p:
            lo = mid
        else:
            hi = mid
    return hi


def payload(frame):
    return frame - FRAME_HEADER_B - AEAD_TAG_B


def lam(rate, frame):
    return rate / frame


def fmt(x):
    return f"{x:,.2f}" if x < 10 else f"{x:,.1f}" if x < 1000 else f"{x:,.0f}"


def table(headers, rows):
    w = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    print("  " + "  ".join(str(h).rjust(w[i]) for i, h in enumerate(headers)))
    for r in rows:
        print("  " + "  ".join(str(c).rjust(w[i]) for i, c in enumerate(r)))


def section_gap():
    print("\n1. frames a second and the mean gap (the mean wait of one enqueued row)")
    rows = []
    for cls, (rate, _) in CLASSES.items():
        for arm, f in ARMS.items():
            l = lam(rate, f)
            rows.append([cls, arm, f"{rate:,}", f"{f:,}", fmt(l), fmt(1 / l) + " s"])
    table(["class", "arm", "B/s", "frame B", "λ /s", "gap"], rows)


def section_contact():
    print(f"\n2. first contact: k shaped waits as an Erlang-k; the shaped part against {TARGET_S:.0f} s "
          f"less the unshaped base of {UNSHAPED_BASE_S} s (k = 7 reproduces edge's +40 s at home)")
    room = TARGET_S - UNSHAPED_BASE_S
    rows = []
    for cls, (rate, _) in CLASSES.items():
        for arm, f in ARMS.items():
            l = lam(rate, f)
            cells = [cls, arm]
            for k in HANDSHAKE_STEPS:
                cells += [fmt(k / l) + " s", fmt(erlang_quantile(k, l, 0.95)) + " s", f"{100 * erlang_cdf(k, l, room):.0f}%"]
            rows.append(cells)
    table(["class", "arm"] + [h for k in HANDSHAKE_STEPS for h in (f"k={k} mean", "p95", f"fits {room:.1f} s")], rows)


def section_budget():
    print("\n3. the ρ budget per window: real frames admitted, and the real bytes they carry")
    rows = []
    for cls, (rate, w) in CLASSES.items():
        base = None
        for arm, f in ARMS.items():
            l = lam(rate, f)
            frames = math.ceil(RHO * l * w)
            by = frames * payload(f)
            base = base or by
            rows.append([cls, arm, f"{w:,} s", f"{frames:,}", f"{by / 1e6:.3f} MB", f"{100 * by / base - 100:+.1f}%"])
    table(["class", "arm", "W", "real frames", "real bytes", "vs A"], rows)


def section_rows():
    print("\n4. rows: frames per row, padding waste with one row per frame, and transit time at server and cellular class")
    rows = []
    for name, size in ROWS.items():
        for arm, f in ARMS.items():
            n = math.ceil(size / payload(f))
            waste = n * payload(f) - size
            ls = lam(CLASSES["server"][0], f)
            lc = lam(CLASSES["phone-cellular"][0], f)
            rows.append([name, arm, f"{size:,}", n, f"{waste:,}", fmt(n / ls) + " s", fmt(n / lc) + " s"])
    table(["row", "arm", "bytes", "frames", "pad B", "server", "cellular"], rows)
    print("  transit = frames ÷ λ: a volume of bytes takes the same time in every arm (bytes ÷ rate); the frame size moves the first byte only")


def section_overhead():
    print("\n5. overhead and CPU: wire bytes per payload byte (frame seal, packet header and proof), and seals a second at eight links")
    rows = []
    for arm, f in ARMS.items():
        wire = f + LINK_SEAL_B + PACKET_HEADER_B + PROOF_B
        eff = payload(f) / wire
        seals = [8 * lam(rate, f) for rate, _ in CLASSES.values()]
        rows.append([arm, f"{wire:,}", f"{payload(f):,}", f"{100 * (1 - eff):.1f}%"] + [fmt(s) for s in seals])
    table(["arm", "wire B", "payload B", "overhead"] + [f"{c} seals/s" for c in CLASSES], rows)
    print("  the budget is a rate of frame bytes; at 1,400 B the wire carries about a tenth more than the budget, at the MDU about one per cent more")
    print("  an observer sees, in every arm, the link, its endpoints and a constant-size frame stream at λ; never the real share")


def check():
    errs = []
    fa, fb = ARMS["A: MDU"], ARMS["B: 1,400"]
    room = TARGET_S - UNSHAPED_BASE_S
    for cls, (rate, w) in CLASSES.items():
        la, lb = lam(rate, fa), lam(rate, fb)
        if abs(lb / la - fa / fb) > 1e-9:
            errs.append(f"{cls}: λ ratio is not the frame ratio")
        ba = math.ceil(RHO * la * w) * payload(fa)
        bb = math.ceil(RHO * lb * w) * payload(fb)
        wa = (fa + LINK_SEAL_B + PACKET_HEADER_B + PROOF_B) / fa
        wb = (fb + LINK_SEAL_B + PACKET_HEADER_B + PROOF_B) / fb
        if cls == "server" and not (0.10 < wb - wa < 0.16):
            errs.append(f"wire bytes over budget at 1,400 B exceed the MDU's by {100 * (wb - wa):.1f}%, not about a tenth")
        if abs(bb / ba - 1) > 0.03:
            errs.append(f"{cls}: real bytes per window move by {100 * (bb / ba - 1):+.1f}% between arms")
        if cls != "phone-cellular" and erlang_cdf(7, lb, room) < 0.95:
            errs.append(f"{cls}: seven shaped waits at 1,400 B do not fit {room} s at the 95th percentile")
        if erlang_cdf(7, la, room) > 0.05 and cls != "server":
            errs.append(f"{cls}: seven shaped waits at the MDU fit {room} s more than one time in twenty")
    gaps_b = {cls: 1 / lam(rate, fb) for cls, (rate, _) in CLASSES.items()}
    stated = {"server": 0.2, "home": 0.5, "phone-wifi": 1.0, "phone-cellular": 4.0}
    for cls, g in gaps_b.items():
        if round(g, 1) != stated[cls]:
            errs.append(f"{cls}: the gap at 1,400 B is {g:.2f} s, the text says {stated[cls]} s")
    if math.ceil(ROWS["onion packet"] / payload(fb)) != 12:
        errs.append("an onion packet does not span twelve 1,400 B frames")
    if errs:
        print("frame A/B: FAIL"); [print("  " + e) for e in errs]
        return 1
    print("frame A/B: λ scales as the frame ratio; real bytes per window within 3% between arms; wire bytes about a tenth over the budget at 1,400 B; "
          "seven shaped waits at 1,400 B fit the contact target at p95 on server, home and phone-wifi and "
          "at the MDU on none but server below one in twenty; gaps 0.2 / 0.5 / 1.0 / 4.0 s as the text states; "
          "an onion packet spans twelve frames")
    return 0


def main():
    if "--check" in sys.argv[1:]:
        return check()
    print("CC 5.4.3 shaped frame: A (the link MDU) against B (1,400 B), same byte rate, ρ = 0.5")
    section_gap()
    section_contact()
    section_budget()
    section_rows()
    section_overhead()
    return 0


if __name__ == "__main__":
    sys.exit(main())
