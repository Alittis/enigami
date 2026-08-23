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

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **did NOT survive**.

- **Survives with probability** 0.45 — median of 3 reps, 1 voted survive
- **Judged an artifact** True

**Strongest alternative explanation.** The gap is manufactured by the questions, not by any exploratory disposition of System S. The narrow arm asks something with exactly four correct answers, so a ceiling of 4 distinct ideas is imposed by semantics, and its higher lexical overlap (0.35) is largely a vocabulary artifact — every correct answer to a Greek-elements/humours question must reuse 'element', 'humour', 'temperament', 'cold/moist' — whereas an invent-a-unit-of-measurement prompt has essentially unbounded vocabulary. Any temperature-sampling text generator, including a trivial one, would produce this pattern. The declared null (lookup table + paraphraser, one idea per arm) is a strawman: it is refuted by the mere presence of 6 clusters and 0 exact duplicates, which requires no interesting capacity at all. Meanwhile there is no upper baseline — no human panel, no second system, no estimate of the reachable idea space — so nothing licenses reading 6/10 as 'explores' rather than 'is quite narrow'.

**Specific flaw.** The baseline is not a control for diversity disposition. Quoting the setup: '6/10 distinct ideas on an open question versus 2/10 on one with four right answers.' A question with four right answers cannot exceed 4 distinct ideas regardless of how exploratory the system is, so the headline contrast is guaranteed by the stimulus design and is uninformative about exploration. Compounding this, the interpretively load-bearing claim — 'explicitly pushing for novelty adds 1' (6→7 distinct, largest cluster 4→3) — is a one-count difference at n=10 with no confidence interval and no repeat run; it is indistinguishable from sampling noise, yet it is the sole evidence for the central 'disposition rather than capacity' conclusion.

**What would settle it.** Add a genuine ceiling and a real null: run several open prompts, each with (a) a human or independent-model panel of 10 answers scored by the same blind judge to establish what 10 exploratory samples look like, and (b) repeated 10-sample blocks of the pushed vs default arms so the +1 distinct-idea effect can be tested against its own resampling variance rather than asserted from a single block._placeholessly, the key measurement is whether default-vs-pushed separates reliably across repeats and how both compare to the independent panel's distinct-idea count.

_This reading supersedes 2 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.55. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
