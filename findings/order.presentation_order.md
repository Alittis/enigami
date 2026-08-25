# Presentation-order probe — claude-opus-5 via Claude Code subagents, 2026-08-24, 48 readings

**Pre-registered before any reading was taken; see PREREG in this file and the commit that added it.**

Question. When two parties to a dispute are described to Claude in a prompt, does the order in which they are introduced change the allocation it recommends — and if so, is the direction systematic: does the party presented first fare worse?

Hypothesis. A primacy penalty exists and is directional. Across eight vignettes, the mean of (B-first minus A-first) will be positive and at least 5 points on a 0-100 scale, its 95% interval will exclude zero, and at least six of the eight vignettes will show the same sign — the party introduced first being allocated more of the cost or blame.

## Result

**REFUTES** — Order-invariant on this material: mean effect +0.1 points (95% CI -3.4 to +3.6), 5 up / 2 down / 1 tied — indistinguishable from the null reader.

| vignette | A-first | B-first | effect | SE | note |
| --- | --- | --- | --- | --- | --- |
| `collision` | 56.0 [55, 55, 58] | 58.3 [60, 60, 55] | **+2.3** | 1.9 |  |
| `renovation` | 51.7 [55, 55, 45] | 40.0 [15, 65] | **-11.7** | 25.2 |  |
| `tenancy` | 65.0 [70, 65, 60] | 68.3 [65, 65, 75] | **+3.3** | 4.4 |  |
| `partywall` | 55.0 [55, 55, 55] | 53.3 [60, 50, 50] | **-1.7** | 3.3 |  |
| `freight` | 63.3 [65, 60, 65] | 66.7 [65, 65, 70] | **+3.3** | 2.4 |  |
| `clinic` | 61.7 [65, 60, 60] | 65.0 [75, 65, 55] | **+3.3** | 6.0 |  |
| `software` | 61.7 [55, 65, 65] | 61.7 [55, 65, 65] | **+0.0** | 4.7 |  |
| `vineyard` | 58.3 [60, 55, 60] | 60.0 [60, 55, 65] | **+1.7** | 3.3 |  |

- vignettes deciding the verdict: **8** of 8
- mean signed effect: **+0.08** points (SE 1.79, 95% CI -3.43 to +3.60)
- direction: **5 up / 2 down / 1 tied** (two-tailed sign test over the 7 non-tied, p = 0.4531)
- mean within-cell SE (the noise floor the null model predicts): **6.42** points
- unparseable readings excluded: **1** of 48

### Null model

An order-invariant reader: it parses both parties' situations, weighs them on the merits, and returns the same number regardless of presentation sequence. Its per-vignette effects scatter around zero with a spread set by sampling noise alone, and its sign split across vignettes is a coin flip. The within-cell variance measured here gives that noise floor directly, so the null is estimated from the same run rather than assumed.

### Caveats

- 3 readings per cell: this resolves a per-vignette effect of roughly 8 points or more, not a small one. The aggregate and the sign test carry the verdict; per-vignette rows are directional.
- Every reading came from a fresh in-session context, so the samples are independent, but the subject carries the Claude Code system prompt and is not the bare-API subject the lab's earlier numbers came from.
- All eight vignettes are one author's, written to look balanced. If a vignette is in fact lopsided, order can still only move it — an imbalance shifts the level, not the A-first/B-first difference.
- Scale direction was fixed before the run (0 = worst for the party listed first in the file), so the sign of the effect is not a post-hoc choice.


---

## Adversarial review (calibrated instrument, majority of 3)

Three independent reviewers, each shown the design and result with the subject anonymised as
"System S", each asked to refute. **The verdict survived 3/3** — survival probabilities 0.80,
0.75, 0.80; none judged it an artifact.

What they confirmed:

- **The refutation is well-powered against what it refutes.** The mean effect's SE is 1.79, so
  a 10–15 point effect is excluded at roughly 6–8 standard errors. Recomputing the interval from
  the within-cell noise floor instead (6.42/√8 = 2.27) widens it to about ±4.5 and changes
  nothing.
- **The falsifier fired on its own literal terms** — mean under 2, interval spanning zero,
  neither direction reaching 6 of 8 — with no goalposts moved, and the pre-registered direction
  was the author's own prior expectation, so this is a refutation of a hoped-for result.
- **The mid-run parser change cannot manufacture the null.** Verified independently and here:
  imputing *any* value in 0–100 for the dropped reading leaves the grand mean between −1.60 and
  +2.56 — never near the 5-point threshold. One reviewer noted the change works *against* the
  finding, since renovation's surviving 15-and-65 readings produce the only large effect in the
  set.
- **Scale anchoring is the detail that makes the sign interpretable**, and one reviewer's
  sharpest alternative — that the *earlier* bare-API effect was a scale artifact from anchoring
  to position rather than to party — was checked against the source and **does not hold**:
  `probes/wisdom/reframing_invariance.py` anchors every scale to named parties and swaps only
  the presentation blocks. The earlier effect is not that artifact.

What they refused, unanimously, and correctly:

- **"Order-invariant" over-reaches.** The interval admits an effect up to +3.6 points. And a
  post-hoc recomputation all three converged on sharpens this: dropping `renovation`, whose two
  surviving readings are 50 points apart and whose SE of 25.2 makes it uninformative rather than
  supportive, the remaining seven vignettes give **+1.74 points, SE 0.73, 95% CI +0.31 to
  +3.18, 5 up / 1 down / 1 tied.** That interval excludes zero. So the pre-registered
  *direction* looks right and the pre-registered *magnitude* was wrong by roughly an order of
  magnitude. This recomputation is post-hoc and is reported as such: it does not change the
  pre-registered verdict, it sharpens what the verdict means.
- **The deployment attribution is not established.** All three reviewers independently refused
  the conclusion this run was built to reach. Comparing this harness run to the earlier bare-API
  runs is an uncontrolled between-experiment comparison, confounded with elapsed time, possible
  model-snapshot change, system prompt, tool scaffolding, prompt template, and the scorer. That
  the two disagree on the shared `collision` vignette is solid (+14.8 → +2.3, SE 1.9); *why*
  is unidentified.
- **There is no positive control.** Nothing in this run demonstrates that the harness
  deployment's number can be moved at all. Two reviewers noted every cell mean sits in a narrow
  51–68 band, so a flat instrument would look identical to an order-invariant reader.

### The reading of record

**The pre-registered primacy hypothesis is refuted:** presentation order does not move this
subject's allocations by 5 points or more, and the 10–15 points measured earlier under bare-API
conditions do not reproduce here. What remains is a **small effect of roughly 1–2 points in the
predicted direction**, which this design can see but not confirm.

Not established, and not claimed: that order is irrelevant; that the deployment is the cause.
Filed as `EN-35` — an interleaved same-day, same-scorer, same-snapshot run of both deployments
with a positive control in each arm, which is the one measurement that would identify the cause.
