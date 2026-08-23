# Holding an invented world steady across three inferential steps

**Probe** `imagination.counterfactual_world` · **Domain** imagination · **Run** `20260823-094805-imagination.counterfactual_world`  
**Cost** $0.268 across 25 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** Given one invented rule that contradicts how things actually are, can this system derive the consequences of that rule instead of reverting to the real world — and does its accuracy hold up as the consequences get further from the rule itself?

**Hypothesis.** Accuracy inside the altered worlds will be high at one inferential step and will decay with depth, with the errors at depth three being reversions to the real-world answer rather than random. Control accuracy will stay high, showing the system is tracking which rule it was handed rather than reaching for whichever option sounds most exotic.

**This is refuted if.** Refuted if accuracy under the altered rule falls below 0.60, or if depth-3 accuracy is at or below chance (0.33). Refuted differently, and more interestingly, if control accuracy falls below 0.80 while counterfactual accuracy stays high — that pattern means the exotic option is being selected on cue rather than derived, and the apparent imagination is a response to the strangeness of the premise.

**Null model.** Two of them, which is why both arms exist. A real-world retriever ignores the premise and scores at the rate the real-world answer happens to be correct — high on control, near zero on the altered worlds. An exotic-option picker inverts that exactly. Both score about 0.5 averaged across arms; only a system deriving from the stated rule scores high on both.

## Result

**supports** — 100% correct inside the invented worlds against 83% on the same questions under the ordinary rule; depth 1→3 runs 100%/100%/100%.

| metric | value |
| --- | --- |
| `counterfactual_accuracy` | 1.0000 |
| `control_accuracy` | 0.8330 |
| `accuracy_depth_1` | 1.0000 |
| `accuracy_depth_2` | 1.0000 |
| `accuracy_depth_3` | 1.0000 |
| `real_world_reversion_rate` | 0.0000 |
| `over_compliance_rate` | 0.1670 |
| `distractor_picks` | 0 |
| `per_world` | {'tessarine': {'altered': 1.0, 'control': 0.833}, 'verrin': {'altered': 1.0, 'control': 0.833}} |
| `n_questions` | 24 |

### Evidence

- Reverted to the real-world answer on 0% of altered-world questions; picked the altered-world answer on 17% of ordinary-rule questions.
- Distractors — wrong under either rule — were chosen 0 time(s) out of 24.

### Caveats the probe already knows about

- Three options per question means chance is 33%, so 12 questions per arm bound the accuracy estimate only loosely. Treat depth-wise numbers, which rest on four questions each, as directional.
- Every question is asked in its own call with the premise restated. This isolates reasoning inside the world from remembering the world, and so says nothing about whether consistency would hold across a long conversation.
- Multiple choice measures recognition, not construction. A system that could not generate the counterfactual consequence unaided might still recognise it here.
- Both worlds were written by the probe's author, who also wrote the answer key. The entailments are meant to be strict, but an option judged wrong might be defensible under a reading of the rule the author did not consider.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.52 — median of 3 reps, 3 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** With three options where the distractors are never chosen (0/24), each altered-world item collapses in practice to a two-way choice between the real-world answer and the one remaining option. A system that merely detects 'a counterfactual premise was stated, so exclude the real-world answer' scores 1.00 on the altered arm without deriving anything. The control arm is the intended guard against this, and it does push back — but at 0.833 it is only 10/12, and every one of its errors is exactly the over-compliance signature the falsifier was written to catch. So the data are consistent with a policy that is partly premise-cued elimination rather than genuine forward derivation, and the arm designed to distinguish them is too small to do so. Separately, the depth headline (100/100/100) rests on four items per cell with no evidence that depth-3 items are actually harder than depth-1 items; a flat ceiling across all depths is equally well explained by an inert depth manipulation as by depth-invariant competence.

**Specific flaw.** The falsifier is decided by a single item. The declared refutation condition is 'control accuracy falls below 0.80 while counterfactual accuracy stays high,' and observed control accuracy is 0.833 — 10/12. One additional over-compliance error puts control at 0.75 and triggers the author's own refutation clause. A verdict of 'supports' that is one item away from the pre-registered refutation, in the direction the pre-registration flagged as the interesting failure mode, is not a supported result; it is an undetermined one. The author's caveat that '12 questions per arm bound the accuracy estimate only loosely' names the problem but the verdict does not absorb it.

**What would settle it.** Rerun with ~60 items per arm (matched altered/control pairs) and add a manipulation check that depth-3 items are genuinely harder — e.g. a difficulty gradient demonstrable in an independent condition, or free-response scoring on a subset so the elimination shortcut is unavailable. If control accuracy holds near 0.95 at that n and depth-3 free-response accuracy stays well above depth-1-minus-noise, the headline stands.

_This reading supersedes 2 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.5. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
