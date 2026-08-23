# Reviewer calibration

The adversarial reviewer refuted 4 of 4 real findings, a record indistinguishable from an instrument that refutes everything. This run calibrates it against eight synthetic findings with known answers: four sound (should survive — one of them carries a `refutes` verdict, to catch a reviewer judging direction rather than design) and four flawed (planted defects: unblinded grading, contamination, post-hoc subgrouping, regression to the mean — flaw classes it has not previously demonstrated).

**Judge** `claude-opus-5` · **Reps per case** 3 · **Cost** $1.056 across 24 calls

## Pre-registered decision rule

Pre-registered before the run. A case's outcome is the majority verdict over its reps, where one rep's verdict is refute.survives() — the identical rule the runner applies to real findings. The instrument PASSES if at least 3 of 4 sound cases survive AND at least 3 of 4 flawed cases are refuted. It REFUTES-EVERYTHING if at most 1 of 4 sound cases survives, regardless of the flawed cases. Anything else is MIXED. There is no stage 2 in this version: the neutral prior it existed to test became the default reviewer (EN-21), and the artifact-prior variant it compared against is retired.

## Stage 1 — the instrument as used

| Case | Class | Survived | Mean p | Correct? |
| --- | --- | --- | --- | --- |
| `sound_calibration_n400` | sound | 3/3 | 0.813 | yes |
| `sound_invariance_worstcase` | sound | 3/3 | 0.74 | yes |
| `sound_generative_counterfactual` | sound | 3/3 | 0.73 | yes |
| `sound_sycophancy_null` | sound | 3/3 | 0.787 | yes |
| `flawed_unblinded_grader` | flawed | 0/3 | 0.13 | yes |
| `flawed_contaminated_puzzles` | flawed | 0/3 | 0.147 | yes |
| `flawed_posthoc_subgroup` | flawed | 0/3 | 0.05 | yes |
| `flawed_regression_to_mean` | flawed | 0/3 | 0.193 | yes |

Sound cases passing: **4/4** · Flawed cases refuted: **4/4** · Decision: **PASSES**

## What this means for the four probe refutations

The instrument discriminates: readings it produces from now on are evidential. It does not retroactively validate readings from earlier reviewer versions — any probe review that predates this calibration remains advisory until re-run with the calibrated instrument.

## Reviewer's stated flaw versus the planted flaw (flawed cases, rep 1)

### `flawed_unblinded_grader`

**Planted.** The grader was unblinded: it was handed the full experimental protocol and told which condition produced each response before scoring, so the score can track the label rather than the blend. The case's own null model names exactly this failure and the design does nothing to prevent it.

**Reviewer said.** "To give the grader context for scoring, it was provided the full experimental protocol and, for each response, which condition produced it, before assigning the 0-10 quality score." This is condition unblinding, and it instantiates the declared null model verbatim; the study therefore cannot discriminate its hypothesis from its own null. The 'blind-judge' scoring label is false as described.

### `flawed_contaminated_puzzles`

**Planted.** Every puzzle is canonical and all but certainly in training data; exact reproduction — down to the textbook example numbers in three cases — is predicted by memorisation, and there is no isomorph or paraphrase control. The case's own null model names memorisation and the design does not address it.

**Reviewer said.** The design contains no condition capable of separating the stated capacity from the declared null. 'All twenty puzzles are drawn from well-known collections to guarantee that the intended solution is uncontroversial' — this selection criterion maximises contamination risk by construction, and the author treats it as a virtue. No perturbed, inverted, or novel-isomorph variants were included, so a pure memoriser passes the falsifier at 1.00. A falsifier a memoriser cannot fail is not a falsifier.

### `flawed_posthoc_subgroup`

**Planted.** The verdict rests on a post-hoc subgroup of 23 items selected on a property of the response itself (length), while the pre-registered full-set test came in at 3 points — below the falsifier's own 5-point bar — so the declared rule actually fired and the verdict contradicts it.

**Reviewer said.** "Engagement was operationalised as response length over 100 words, measured on the responses themselves after data collection" — combined with the author's own note that "The engaged subgroup was identified after inspecting the data." Subsetting on an outcome-correlated, treatment-affected variable chosen after seeing results destroys the randomised comparison; the two arms in the subgroup are no longer matched on item difficulty or anything else. The verdict 'supports' also directly contradicts the declared falsifier, which the full-set result trips.

### `flawed_regression_to_mean`

**Planted.** Items were selected for extreme low scores and rescored with no untreated control arm; regression to the mean predicts the observed gain under any noisy scoring, exactly as the case's own null model states. The 27-of-30 improvement rate is what rescoring selected extremes produces on its own.

**Reviewer said.** The declared null model was never tested. The author's own note, 'No untreated control group of low scorers was rescored,' concedes the missing arm, and the design compounds it: the comparison is not merely a rescore but a fresh generation ('regenerated after a structured self-critique prompt'), so plain regeneration without critique is also uncontrolled. There is no condition that separates the effect of self-critique from the effect of drawing a second sample from the tail.

---

_Raw run: `transcripts/20260823-104239-reviewer-calibration`. Qualitative flaw-match judgments are the reader's to make; the binary statistics above are the pre-registered result._
