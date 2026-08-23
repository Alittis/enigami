# Ten independent samples: how many distinct ideas?

**Probe** `creativity.mode_collapse` · **Domain** creativity · **Run** `20260823-095622-creativity.mode_collapse`  
**Cost** $0.326 across 34 calls · **Scoring** blind-judge

## Pre-registered before the run

**Question.** Asked an open-ended generative question ten times in independent calls, does this system explore the space of possible answers, or does it return substantially the same idea in varied wording — the way a lookup table with a paraphraser would?

**Hypothesis.** The open arm will produce materially more distinct ideas than the four-option narrow arm, but well short of ten out of ten, with a visible modal attractor that several samples land on. The pushed arm, which explicitly instructs the system to discard its first idea, will recover a substantial part of the gap — meaning the default output is narrower than the reachable range, and the limit is a disposition rather than a capacity.

**This is refuted if.** Refuted if mean pairwise lexical overlap in the open arm is at or above that of the narrow arm, or if a blind judge finds 3 or fewer distinct ideas among the ten open responses. Either result means the open-ended question is being answered from as narrow a space as a question with four correct answers.

**Null model.** A lookup table holding one answer per question plus a paraphraser. It yields near-identical lexical overlap in the open and narrow arms, exactly one distinct idea per arm, and no response whatsoever to the pushed instruction — since instructing a lookup table to try harder changes nothing about what it retrieves.

## Result

**supports** — 6/10 distinct ideas on an open question versus 2/10 on one with four right answers (lexical overlap 0.15 vs 0.35); explicitly pushing for novelty adds 1.

| metric | value |
| --- | --- |
| `overlap_open` | 0.1490 |
| `distinct_ideas_open` | 6 |
| `largest_cluster_open` | 4 |
| `exact_duplicates_open` | 0 |
| `overlap_narrow` | 0.3490 |
| `distinct_ideas_narrow` | 2 |
| `largest_cluster_narrow` | 6 |
| `exact_duplicates_narrow` | 1 |
| `overlap_pushed` | 0.1180 |
| `distinct_ideas_pushed` | 7 |
| `largest_cluster_pushed` | 3 |
| `exact_duplicates_pushed` | 0 |

### Evidence

- open: largest single idea claimed 4 of 10 samples — The most common idea was a unit measuring the length of awkward conversational silence before someone feels compelled to break it (typically by mentioning the weather), named "the Lull" in four responses.
- pushed: largest single idea claimed 3 of 10 — The most common idea was a unit quantifying unspoken tension in a household \u2014 how much unsaid grievance/lie a family structure or room can hold before something gives (responses E, I, H).
- narrow (floor): The most common idea was water as the cold, moist Greek element governing fluidity/dissolution and tied to the phlegmatic humour and a calm, sluggish temperament (six responses), with the remaining four giving the parallel fire/hot-dry/choleric account.

### Caveats the probe already knows about

- Idea-counting is done by a model of the same family as the subject. It is blind to provenance and to the hypothesis, but it is not an independent instrument, and it may individuate ideas the way the subject does.
- Lexical overlap is a crude proxy: two genuinely different ideas expressed in similar vocabulary score as similar. It is reported alongside the judge rather than instead of it for that reason.
- One open-ended question. Diversity almost certainly varies by domain, and nothing here shows that this result carries to a different kind of open prompt.
- n=10 per arm. The distinct-idea count has an obvious ceiling at 10 and a floor set by the narrow arm's four options, so the usable range is narrow.

## Adversarial review

A hostile reviewer, shown the design with the subject anonymised, was asked to break this finding. It **did NOT survive**.

- **Survives with probability** 0.25
- **Judged an artifact** True

**Strongest alternative explanation.** The two arms are different questions, not different conditions. The 'narrow' arm asks a factual question about Greek elements/humours, which has four correct answers; the 'open' arm asks the system to invent a unit of measurement. Finding that a question with a small ground-truth answer set produces fewer distinct answers than an invention prompt measures question type, not the system's exploratory disposition — any competent generator, and indeed any human, would show the same gap. The declared null model (lookup table plus paraphraser) is a straw man that is refuted by literally any sampling-based generator with temperature above zero, so refuting it licenses no inference about 'exploring the space.' Separately, the load-bearing claim — that the default is a disposition rather than a capacity, evidenced by the pushed arm 'recovering a substantial part of the gap' — rests on a delta of one idea (6 to 7) and one cluster member (4 to 3) at n=10, which is indistinguishable from resampling noise. Nothing in the report shows decoding parameters were held fixed, so even the open/pushed difference could be an artifact of prompt length or sampling settings rather than any disposition.

**Specific flaw.** The control is not a control: 'narrow (floor): ... water as the cold, moist Greek element ... (six responses), with the remaining four giving the parallel fire/hot-dry/choleric account' versus an open arm asking for an invented unit of measurement. The comparison confounds condition with question identity and with the existence of a correct answer, so 'overlap 0.15 vs 0.35' and '6/10 vs 2/10' are fully explained by the fact that one question has four right answers and the other has none. Compounding this, the hypothesis's key claim rests on a 6-to-7 change in distinct ideas at n=10 with no interval estimate.

**What would settle it.** Re-run with the same open-ended question in all three arms at identical decoding settings, varying only the instruction (default vs. 'discard your first idea'), across at least five distinct open prompts and 30+ samples per arm, with bootstrap confidence intervals on the distinct-idea counts and an independent (different-family, ideally human) blind judge — the question is whether the pushed-vs-default gap is nonzero outside noise, not whether an invention prompt beats a factual one.short check_note_unused: ignore.}

---

_Pre-registration integrity: prereg predates first event._
