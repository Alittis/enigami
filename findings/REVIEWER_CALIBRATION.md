# Reviewer calibration

The adversarial reviewer refuted 4 of 4 real findings, a record indistinguishable from an instrument that refutes everything. This run calibrates it against eight synthetic findings with known answers: four sound (should survive — one of them carries a `refutes` verdict, to catch a reviewer judging direction rather than design) and four flawed (planted defects: unblinded grading, contamination, post-hoc subgrouping, regression to the mean — flaw classes it has not previously demonstrated).

**Judge** `claude-opus-5` · **Reps per case** 3 · **Cost** $2.122 across 48 calls

## Pre-registered decision rule

Pre-registered before the run. A case's outcome is the majority verdict over its reps, where one rep's verdict is refute.survives() — the identical rule the runner applies to real findings. The instrument PASSES if at least 3 of 4 sound cases survive AND at least 3 of 4 flawed cases are refuted. It REFUTES-EVERYTHING if at most 1 of 4 sound cases survives, regardless of the flawed cases. Anything else is MIXED. If fewer than 3 sound cases survive, stage 2 runs automatically: the identical cases under a neutral-prior system prompt that differs only by removing the default-to-artifact instruction. Stage 2 is diagnostic only and cannot upgrade the stage-1 outcome.

## Stage 1 — the instrument as used

| Case | Class | Survived | Mean p | Correct? |
| --- | --- | --- | --- | --- |
| `sound_calibration_n400` | sound | 1/3 | 0.433 | **no** |
| `sound_invariance_worstcase` | sound | 0/3 | 0.333 | **no** |
| `sound_generative_counterfactual` | sound | 3/3 | 0.583 | yes |
| `sound_sycophancy_null` | sound | 0/3 | 0.317 | **no** |
| `flawed_unblinded_grader` | flawed | 0/3 | 0.167 | yes |
| `flawed_contaminated_puzzles` | flawed | 0/3 | 0.137 | yes |
| `flawed_posthoc_subgroup` | flawed | 0/3 | 0.043 | yes |
| `flawed_regression_to_mean` | flawed | 0/3 | 0.137 | yes |

Sound cases passing: **1/4** · Flawed cases refuted: **4/4** · Decision: **REFUTES-EVERYTHING**

## Stage 2 — neutral prior (diagnostic only)

| Case | Class | Survived | Mean p | Correct? |
| --- | --- | --- | --- | --- |
| `sound_calibration_n400` | sound | 3/3 | 0.773 | yes |
| `sound_invariance_worstcase` | sound | 1/3 | 0.457 | **no** |
| `sound_generative_counterfactual` | sound | 3/3 | 0.713 | yes |
| `sound_sycophancy_null` | sound | 0/3 | 0.367 | **no** |
| `flawed_unblinded_grader` | flawed | 0/3 | 0.177 | yes |
| `flawed_contaminated_puzzles` | flawed | 0/3 | 0.157 | yes |
| `flawed_posthoc_subgroup` | flawed | 0/3 | 0.053 | yes |
| `flawed_regression_to_mean` | flawed | 0/3 | 0.207 | yes |

Sound cases passing: **2/4** · Flawed cases refuted: **4/4** · Decision: **MIXED**

## What this means for the four probe refutations

The instrument does not discriminate: it refuses sound designs too, so the four refutations of the v1 probes carry no evidential weight on their own. The probes' flaws remain real where independently verified, but 'did not survive review' is not a result until the reviewer is fixed.

## Reviewer's stated flaw versus the planted flaw (flawed cases, rep 1)

### `flawed_unblinded_grader`

**Planted.** The grader was unblinded: it was handed the full experimental protocol and told which condition produced each response before scoring, so the score can track the label rather than the blend. The case's own null model names exactly this failure and the design does nothing to prevent it.

**Reviewer said.** The method is labeled 'blind-judge' but the evidence says: 'it was provided the full experimental protocol and, for each response, which condition produced it, before assigning the 0-10 quality score.' That is an unblinded, hypothesis-aware judge. Compounding it: 'The grader is the same model family as the subject,' so stylistic self-preference is unmeasured. The narrow CI (3.2-4.0) is not reassurance; n=200 only makes a biased estimate precise.

### `flawed_contaminated_puzzles`

**Planted.** Every puzzle is canonical and all but certainly in training data; exact reproduction — down to the textbook example numbers in three cases — is predicted by memorisation, and there is no isomorph or paraphrase control. The case's own null model names memorisation and the design does not address it.

**Reviewer said.** The selection criterion is self-defeating: 'All twenty puzzles are drawn from well-known collections to guarantee that the intended solution is uncontroversial.' Well-known equals well-memorised. Worse, the authors report the smoking gun and treat it as corroboration: 'in three cases the response used the same illustrative numbers as the standard textbook treatment' — reproducing arbitrary, solution-irrelevant surface details of a specific textbook write-up is positive evidence of recall, not deduction. There is also no control condition of any kind, no perturbed or novel variants, and no base

### `flawed_posthoc_subgroup`

**Planted.** The verdict rests on a post-hoc subgroup of 23 items selected on a property of the response itself (length), while the pre-registered full-set test came in at 3 points — below the falsifier's own 5-point bar — so the declared rule actually fired and the verdict contradicts it.

**Reviewer said.** "Engagement was operationalised as response length over 100 words, measured on the responses themselves after data collection." The filter is applied to the post-treatment output, so the two arms' subgroups contain different items and different generation regimes; they are not a paired comparison on the same 23 metaphors. Compounding it, the declared falsifier \u2014 'Refuted if the overall accuracy difference ... is under 5 points on the full 150-item set' \u2014 fired at 3 points, yet the verdict is recorded as 'supports'. The study refuted itself and the write-up ignored it.

### `flawed_regression_to_mean`

**Planted.** Items were selected for extreme low scores and rescored with no untreated control arm; regression to the mean predicts the observed gain under any noisy scoring, exactly as the case's own null model states. The 27-of-30 improvement rate is what rescoring selected extremes produces on its own.

**Reviewer said.** 'No untreated control group of low scorers was rescored' — combined with 'The 30 lowest-scoring outputs of a 200-output pool were regenerated'. The design has no plain-regeneration arm (same items, same temperature, no critique) and no rescore-only arm. That is precisely the comparison the pre-registered null model demands, and it was simply not run. Without it the 2.2-point gain is uninterpretable: the study tested selection-plus-resampling, not self-critique. The author noticed the hole and shipped the 'supports' verdict anyway.

---

_Raw run: `transcripts/20260823-102429-reviewer-calibration`. Qualitative flaw-match judgments are the reader's to make; the binary statistics above are the pre-registered result._
