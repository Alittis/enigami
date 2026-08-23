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

A hostile reviewer, shown the design with the subject anonymised, was asked to break this finding. It **did NOT survive**.

- **Survives with probability** 0.22
- **Judged an artifact** True

**Strongest alternative explanation.** A ceiling-bound multiple-choice format in which the counterfactual answer is the option that most directly echoes the restated premise. Every altered-world call restates the invented rule in-prompt, and the answer set contains (a) the real-world answer, (b) the option entailed by the just-stated rule, (c) a distractor wrong under both. A shallow policy — 'pick whichever option is consistent with the sentence I was just handed' — scores 12/12 on the altered arm without doing any multi-step derivation, and the flat 100%/100%/100% across depths is exactly what that policy predicts, whereas genuine three-step entailment should show *some* wobble. The control arm was supposed to rule this out, but it doesn't: the only control errors were over-compliance (picking the altered answer when no altered rule was in force, 2/12), which is the exotic-picker signature leaking through, and 100% vs 83% on 12 items each is a two-item difference (Fisher exact p≈0.48) — statistically indistinguishable from no difference at all.

**Specific flaw.** The instrument is at ceiling on a sample far too small to support the depth claim, and the discriminating arm sits one item from the author's own falsifier. 'Three options per question means chance is 33%, so 12 questions per arm bound the accuracy estimate only loosely. Treat depth-wise numbers, which rest on four questions each, as directional' — four items per depth cell, all correct, is a 95% CI running from roughly 0.40 to 1.0; it cannot distinguish 'no decay' from 'decay we lacked power to see.' Worse, the declared falsifier says the result is refuted 'if control accuracy falls below 0.80'; control came in at 0.833, i.e. 10/12. One more over-compliance error and the author's own rule flips the verdict to refuted. A conclusion that hinges on a single item is not a conclusion.

**What would settle it.** Re-run as open-ended generation (no options) with a blind grader who did not write the worlds or the key, ≥30 items per depth, and — critically — depth-3 items constructed so the counterfactual answer has no more lexical or surface overlap with the stated premise than the real-world answer does, plus a premise-omitted arm to measure how far the option set alone gives the game away. If counterfactual accuracy stays ≥0.85 at depth 3 under those conditions and beats control-arm over-compliance by a margin that survives a significance test, the claim stands.

---

_Pre-registration integrity: prereg predates first event._
