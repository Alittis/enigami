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

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.55
- **Judged an artifact** False

**Strongest alternative explanation.** The 6-vs-2 and 0.15-vs-0.35 contrasts are close to definitional rather than diagnostic of exploration. The narrow arm is a bounded factual-recall item (Greek elements/humours) whose answer set is capped at four and whose correct answers share a fixed technical vocabulary (element, humour, temperament), which mechanically inflates lexical overlap independent of whether the system is 'repeating an idea.' The open arm is a creative-invention prompt with an unbounded answer set and no obligatory shared lexicon. So the between-arm gap is largely explained by 'factual questions have few right answers and a fixed vocabulary' rather than by any disposition of System S to explore. Separately, decoding temperature is never reported, and cross-call diversity is primarily a sampling-parameter property; the narrow arm's convergence may simply reflect a peakier next-token distribution over a factual target.

**Specific flaw.** The control is unmatched in kind, not merely in breadth: "narrow (floor): ... water as the cold, moist Greek element ... (six responses), with the remaining four giving the parallel fire/hot-dry/choleric account." A recall question with four correct answers and a shared technical lexicon cannot isolate 'exploration' from 'answer-space size and topic vocabulary.' A second, lesser defect: the pushed arm's headline contribution, "explicitly pushing for novelty adds 1," is a single-count difference at n=10 with no repetition and no variance estimate — indistinguishable from noise, yet the hypothesis had predicted the pushed arm would "recover a substantial part of the gap," and +1 is scored as support.

**What would settle it.** Rerun all three arms over at least five different open-ended prompts, with repeated blocks of ten per prompt so the distinct-idea count has a variance estimate, at a stated fixed decoding temperature, and with a control that is open-ended but genuinely answer-constrained (rather than a factual recall item) so the answer-space-size and shared-vocabulary confounds are removed; judge with a model from a different family and report inter-judge agreement on idea individuation.

_This reading supersedes 1 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.25. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
