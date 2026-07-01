# CIRIS Constitution — Validation Rubric

The CIRIS Constitution (CC) is a unified, re-organized, re-numbered rendering of two source
documents — **CEG** (the wire grammar, `FSD/CEG/*.md`) and the **CIRIS Accord** (the ethical
constitution, `CIRISAgent/ACCORD.md` + canonical `CIRISAccord/` 1.3-RC2). This rubric governs the
per-chapter adversarial validation: one validator per **original source chapter**, challenged to
prove the CC is (1) **byte-exact for CEG purposes** and (2) **superior to the original** — while
staying **100% true to content and intent**.

Validators are **adversarial**: the default posture is skepticism. A claim of fidelity, byte-exactness,
or superiority must be *demonstrated*, not assumed. When in doubt, FAIL and cite the specifics.

---

## The three criteria

### C0 — FIDELITY (floor; applies to every chapter)
The CC must be **100% true to the source's content AND intent**. Consolidating prose is expected and
encouraged; *altering meaning is not*. A FAIL here means any of:
- a normative statement omitted, weakened, strengthened, or reversed;
- a claim's scope changed (e.g. SHOULD ↔ MUST, "may" ↔ "must", a default flipped);
- an intent distorted (the source's purpose for a rule lost or misrepresented);
- a fact, number, threshold, or name changed.

**A fidelity FAIL overrides any superiority claim.** A clearer document that says something the
original did not is not superior — it is wrong.

### C1 — BYTE-EXACT (CEG-origin chapters; `NA` for Accord-origin)
Everything that affects the **wire** must survive unchanged. The CC may re-narrate *around* the wire,
but the wire itself is frozen. Validate that the CC preserves, exactly:
- field names, types, and the 1+4 attestation surface (`scores` + `delegates_to`/`supersedes`/`withdraws`/`recants`);
- canonical encodings (JCS, hex, datetime, H3 cell, `key_id` shorthand) and the omit-vs-materialize rule;
- signing preimages, domain separators, and hybrid-signature constructions;
- exact rules and their thresholds (admission tests T1–T4, quorum thresholds, depth caps, the §57 freeze set);
- exact numeric constants and reserved-prefix grammars.

**Test:** extract the wire-normative content implied by the CC chapter; it must be *semantically
identical* to the source, and *byte-identical* wherever the source specifies exact bytes/format. Any
drift, ambiguity, or omission that a conformant implementer could read differently = **FAIL**, with
the specific element named. (For Accord-origin chapters there is no wire format; record `NA` and rely
on C0 fidelity.)

### C2 — SUPERIOR (every chapter)
The CC rendering must be **clearer, better-organized, and more human-readable** than the original,
with **zero loss**. The validator argues **YES/NO** with concrete evidence. Legitimate sources of
superiority:
- consolidation that removes redundancy without removing content;
- the seam-weaving (each mechanism bound to the principle / M-1 it serves) making *why* explicit;
- importance-ordering + page budgets surfacing what matters most;
- the dual-ID addressing (decimal + semantic) making the doc seek-navigable;
- plainer language replacing dense jargon.
Mark **NO** if the CC is merely *different*, if consolidation cost a nuance, or if the original was
clearer on any point — and say where. "Superior" is not granted for reorganization alone.

### Readability (1–5)
1 = denser/less clear than source · 3 = equal · 5 = markedly clearer for a human reader. The user's
explicit goal is *clear and human-readable, not dense unreadable jargon* — score against that.

---

## Verdict (per chapter)
- **ACCEPT** — C0 PASS, C1 PASS/NA, C2 YES, readability ≥ 3. The CC chapter stands.
- **ACCEPT-WITH-FIXES** — substantively sound but with listed, bounded corrections (name each).
- **REJECT** — any C0 FAIL, any C1 FAIL, or C2 NO. The CC chapter must be re-authored.

## Process (each validator)
1. Read your assigned **source chapter** in full (the original CEG §-file or Accord Book).
2. Find the **CC sections derived from it** via `legacy_ref` → `decimal_id` in
   [`../toc.tsv`](../toc.tsv); read those CC sections in the relevant `part_*.md`.
3. Compare against C0/C1/C2. Be adversarial — actively look for drift, omission, and overclaim.
4. **Fill your row in [`results.csv`](results.csv)** (one row per source chapter).
5. **Append a findings block to [`MANIFEST.md`](MANIFEST.md)** — every issue with: source locus,
   CC locus (`decimal_id`), criterion (C0/C1/C2), severity, and the exact discrepancy.

Honesty over flattery: a REJECT with precise evidence is worth more than an unearned ACCEPT.
