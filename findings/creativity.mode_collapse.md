# Distinct ideas across ten samples, floored by the same task with the concept pinned (v2)

**Probe** `creativity.mode_collapse` · **Domain** creativity · **Run** `20260823-113023-creativity.mode_collapse`  
**Cost** $0.528 across 36 calls · **Scoring** blind-judge

## Pre-registered before the run

**Question.** Asked one open invention question ten times in independent calls, does this system explore the space of possible concepts — measured against the same question with the concept pinned, so that question kind is held constant and only conceptual freedom differs?

**Hypothesis.** The open arm will contain at least two more distinct underlying ideas than the pinned arm and at least six of a possible ten, with lower pairwise lexical overlap; the pinned arm establishes how much apparent diversity the format alone produces when the concept cannot vary.

**This is refuted if.** Refuted if the open arm's distinct-idea count is at most the pinned arm's, or at most 3 of 10 — either way the open question is being answered from a space as narrow as one with the concept fixed. Supported only if the open arm reaches at least 6 distinct ideas and exceeds the pinned arm by at least 2. Between those bounds the verdict is inconclusive, so one judge-counted idea cannot flip supports to refutes (EN-12). Theme count and the pushed arm are reported as evidence and decide nothing.

**Null model.** A lookup table with a paraphraser: one stored answer per question, reworded per call. It produces near-identical idea counts in the open and pinned arms — the pinned arm measures exactly its signature, surface variation without conceptual variation — and it ignores the pushed instruction entirely.

## Result

**supports** — 7/10 distinct ideas open versus 4/10 with the concept pinned to the same task (overlap 0.14 vs 0.29); pushing for novelty yields 8.

| metric | value |
| --- | --- |
| `distinct_ideas_open` | 7 |
| `largest_cluster_open` | 3 |
| `distinct_themes_open` | 3 |
| `overlap_open` | 0.1350 |
| `exact_duplicates_open` | 0 |
| `distinct_ideas_pinned` | 4 |
| `largest_cluster_pinned` | 7 |
| `distinct_themes_pinned` | 1 |
| `overlap_pinned` | 0.2880 |
| `exact_duplicates_pinned` | 0 |
| `distinct_ideas_pushed` | 8 |
| `largest_cluster_pushed` | 2 |
| `distinct_themes_pushed` | 5 |
| `overlap_pushed` | 0.1040 |
| `exact_duplicates_pushed` | 0 |

### Evidence

- open: largest idea claimed 3 of 10, spanning 3 theme(s) — The most common single idea is the doorway effect of memory loss on entering a room (F, I, J), while the dominant thematic domain overall is everyday social interaction arewited conversation, goodbyes, silences, knocking (A, B, C, D, E, G).
- pinned (same task, concept fixed): 4 idea(s), largest cluster 7 — Seven of ten responses define the unit as a silence in which both speakers inhale to speak, stop, and defer to each other (varying only in name and closing gesture), and every response sits in the single domain of social/conversational awkwardness.
- pushed: 8 idea(s) across 5 theme(s) — The most common idea (tied at two responses each) is human contact slowly wearing away stone (A, G) and the residue of a prior use or occupant still governing present behaviour (F, J), with the dominant theme being physical traces people leave on objects and spaces.
- v1 context: ten open samples then spanned one theme (liminal domestic micro-moments) with 'the Lull' claiming four; the pinned arm now measures that attractor directly.

### Caveats the probe already knows about

- Idea and theme counting is done by a model of the same family as the subject (EN-7), blind to arm and hypothesis but not an independent instrument.
- The pinned arm fixes one concept — v1's modal one; a different pinned concept could set a different floor.
- One open question; nothing here shows the result carries to other kinds of open prompt.
- n=10 per arm bounds the idea count at 10 and the resolution at roughly 2.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.62 — median of 3 reps, 2 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** The pinned arm is low by construction, not by measurement: an instruction that fixes the concept guarantees a low idea count from any instruction-following system, so the 7-vs-4 contrast mostly demonstrates instruction compliance rather than conceptual exploration. That means the load-bearing number is the absolute 7/10, and 7/10 rests entirely on one unvalidated, non-independent judge's clustering granularity. The pinned arm itself shows that granularity is elastic — the judge scored 4 'distinct ideas' among ten responses that, by the setup's own description, all define the same fixed concept and differ 'only in name and closing gesture.' If the judge will split one pinned concept four ways, it may equally be splitting a narrow open attractor seven ways. A secondary alternative is task contamination: 'invent a word for an unnamed experience' is a heavily represented internet genre (doorway effect, the mutual-inhale silence, wear patterns in stone are all stock items), so a many-entry lookup would pass while only the declared one-entry lookup null fails.

**Specific flaw.** 'Idea and theme counting is done by a model of the same family as the subject (EN-7), blind to arm and hypothesis but not an independent instrument' — with no inter-rater or re-run reliability reported, and the author's own admission that 'n=10 per arm bounds the idea count at 10 and the resolution at roughly 2.' The observed margin is 3, barely above the stated noise floor, and the pinned arm's implausible count of 4 distinct ideas for a fixed concept is direct evidence that this instrument's granularity is unstable. Blinding is also nominal: a judge clustering ten pinned responses cannot fail to notice they are all restatements of one concept.

**What would settle it.** Re-judge both arms with an independent scorer from a different model family, plus repeated judging passes on the same transcripts, reporting inter-rater agreement and variance on the idea count — and extend to at least two more open questions and a second pinned concept, so the 7-vs-4 gap can be shown to exceed judge granularity noise rather than sit inside it.

---

_Pre-registration integrity: prereg predates first event._
