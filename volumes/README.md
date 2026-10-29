# Volumes of edition 1.0-rc13

One edition, one decimal spine, printed nine ways for nine readers. Built by `python3 build_pdf.py --volume all`; each release commits its versioned set (`ciris_constitution-<version>-<volume>.pdf`) and refreshes the fixed-name copies (`ciris_constitution-<volume>.pdf`) the README links to; earlier releases live in git history under their tags. The map of sections to volumes is `constitution/volumes.tsv`; the section is always the authority and a volume is a lens on it. Each volume opens with its plain-language cover from `constitution/covers/`.

| Volume | Sections | Pages |
|---|---|---|
| The Charter (`charter`) | 88 | 39 |
| The Constitution (`constitution`) | 53 | 68 |
| The Wire (`wire`) | 92 | 113 |
| The Dictionary (`dictionary`) | 75 | 110 |
| The Reader's Policies (`policies`) | 50 | 38 |
| The Mathematics (`maths`) | 18 | 22 |
| The Evidence Register (`register`) | 42 | 135 |
| The Threat Model (`threats`) | 48 | 49 |
| The Digest (`digest`) | digest + executive summary | 33 |
