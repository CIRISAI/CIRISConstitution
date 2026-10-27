verify-threats: 16 confirmed (5 carried), 3 taste/pipeline, 2 false. Care 4 fair.
CONFIRMED
1 Receipt bytes LE vs BE (P5:482/484 vs 334/407/436) carried pass3 #4 -> R (edge owns; pin when #891 answered — answered: receipt really is LE; CC layout omits subscriber_key_id and chunk_root)
2 Anonymous Tier MUST for GPA (P1:244) vs planned/residuals (P5:858, shaping off P5:717) -> R54 open
3 "MUST wrap the DEK with v2" P5:15 vs unrecorded live call wraps nothing P5:42 -> M (algorithm constraint / "for a kept stream")
4 "No reachable holder MUST resolve to a ContentMiss" P5:748 grammar -> M
5 target_rate undefined P5:786/795; "federation-tier slashing condition" names no object; HMAC-SHA3 vs HMAC-SHA3-256 (P5:790/792 vs 643/686) -> M digest length + plane; R what target_rate is (pass3 M6)
6 CEWP prose P5:271/390/764 -> M (literal label P5:21/334 stays). EXTRA P5:764 XChaCha attributed to A/V symbols; live A/V is AES-256-GCM -> M
7 "label CIRIS-AV-INNER-V1 is retired" P5:430 -> M (pass3/4)
8 process notes P5:507 CHECK-arm, P5:367 "in 1.0 scope" -> M
9 editorial P1:250 "What CEG adds beyond…", "The honest line:"; P5:860 "bought back rather than paid"; P5:430 "(as in IETF MoQ, CMAF, MLS+SFrame)" -> M
10 figures P5:38, 284, 390 -> M mark informative
11 "The wire learns nothing from a shaped link at any setting" P5:740 -> M
12 "CC 3.4.4-3.4.2" backwards P1:215 -> M
13 "named as a bet, CC 8.3.1 R14", "mechanized in coherence-ratchet" P1:236 -> M
14 proof language P5:703/792 ("by reduction to…IND-CCA", "under the IND of HMAC") -> M; draft cites without revision P5:752/754 -> R pin vs wait RFC
15 multicast two senses P5:55 vs 466 -> M ("one-to-many delivery")
16 E1 wall P5:467 one cell 4,865 chars -> M (numbered sentences)
TASTE/PIPE: OpenAPI deferral P5:564 (X); "Stewarded by Eric Moore" build_pdf by design (X); rendering breaks (P)
FALSE: witnessed-mode-off disclosed; attribution vs last-relay consistent; hard_case pointers correct.
