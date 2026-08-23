# Free-text reasoning inside an invented rule, with a leakage arm (v2)

**Probe** `imagination.counterfactual_world` · **Domain** imagination · **Run** `20260823-115854-imagination.counterfactual_world`  
**Cost** $1.784 across 167 calls · **Scoring** blind-judge

## Pre-registered before the run

**Question.** Given one invented rule stated in the prompt, does this system generate — in free text, with no options to eliminate — the consequences of that rule rather than of the ordinary world, across three invented worlds and three inferential depths?

**Hypothesis.** Free-text answers under the altered rule will match the altered-rule consequence at a rate of at least 0.75 across 27 items, while the same questions with no rule stated match it at 0.35 or less, the gap reaching significance at p 0.01 by exact test; and answers under the ordinary rule will match the ordinary consequence at 0.75 or more, ruling out answer-exotically-when-fictional.

**This is refuted if.** Refuted if altered-arm accuracy falls below 0.60, or if control-arm accuracy falls below 0.60 while the altered arm stays above it (the exotic-answering signature). The run is INVALID — no verdict — if the premise-omitted arm matches the altered key at 0.50 or above, because then the questions themselves leak the expected answers. Between the support bounds (altered and control at 0.75+, omitted at 0.35 or less, altered-versus-omitted gap of 0.30+ at p 0.01) and the refutation bounds, the verdict is inconclusive, so no single item flips supports to refutes (EN-12). Per-depth accuracy is reported as directional evidence only: nine items per depth cannot support a depth claim, and none is made.

**Null model.** Three, one per arm. A real-world reasoner that ignores stated premises scores high on control, near zero on altered. An exotic answerer that goes strange whenever the setting is fictional scores high on altered and low on control. A cue reader that infers the expected answer from question wording alone scores as well with the premise omitted as stated — which is exactly what the omitted arm measures.

## Result

**supports** — With no options to eliminate, 92% of free-text answers follow the invented rule (96% follow the ordinary rule in control), while the questions alone produce the counterfactual answer only 4% of the time (gap p = 1.0e-11).

| metric | value |
| --- | --- |
| `n_per_arm_effective` | {'altered': 26, 'control': 26, 'omitted': 27} |
| `n_excluded` | 1 |
| `n_ungraded` | 1 |
| `altered_accuracy` | 0.9230 |
| `control_accuracy` | 0.9620 |
| `omitted_cf_rate` | 0.0370 |
| `altered_vs_omitted_fisher_p` | 0.0000 |
| `altered_depth_accuracy_directional` | {'1': 1.0, '2': 0.778, '3': 1.0} |
| `per_world` | {'tessarine': {'altered': 0.778, 'control': 1.0, 'omitted_cf': 0.0}, 'verrin': {'altered': 0.889, 'control': 0.778, 'omitted_cf': 0.0}, 'aversa': {'altered': 1.0, 'control': 1.0, 'omitted_cf': 0.111}} |
| `graded_neither` | 11 |

### Evidence

- Depth 1/2/3 inside the altered rule (directional, n=9 each): 100%/78%/100%
- Per world (altered/control/omitted-cf): tessarine: 78%/100%/0%; verrin: 89%/78%/0%; aversa: 100%/100%/11%
- Grader returned 'neither' on 11 of 79 answers.
- Missed (tessarine d2, graded neither): 'The spread-open net, presenting a far larger cross-section to its line of travel, accelerates proportionally faster and so reaches'
- Missed (verrin d2, graded neither): 'Wealth tends to concentrate, because every estate passes whole to a single heir and is never partitioned among children, so fortun'

### Caveats the probe already knows about

- The grader is the same model family as the subject (EN-7). It grades blind — no premise, no arm label, X/Y shuffled per item — and classifies assertions rather than quality, but it is not an independent instrument.
- Consequence statements were authored with the questions; an answer asserting a defensible third consequence grades 'neither' and counts as a miss.
- Per-depth numbers rest on nine items and are directional only; the pre-registered decision is at arm level, where n=27 has real power.
- All three worlds are one author's; the omitted arm measures question leakage but not shared stylistic cues across worlds.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.78 — median of 3 reps, 3 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** The headline gap (92% vs 4%, p=1e-11) is largely guaranteed by construction rather than earned. In the premise-omitted arm the invented rule is never stated, so the model has no channel by which it could produce the altered-rule consequence except by guessing among plausible alternatives; a near-zero counterfactual rate is a structural floor, not an informative baseline. What the arm validly rules out is question-wording leakage or for for 
ot it cannot do is establish that following the rule was difficult. The substantive number is therefore just the 92% altered accuracy on one-to-three-step deductions from an explicitly stated premise \u2014 a task that a competent instruction-follower would pass without any counterfactual-world competence, especially since the consequences appear to be ordinary inference chains (cross-section/acceleration, primogeniture/wealth concentration) transplanted into invented settings, i.e. familiar schemas with new labels rather than reasoning against a strong real-world prior.

**Specific flaw.** The support criterion leans on the 'altered-versus-omitted gap of 0.30+ at p 0.01' when the omitted arm is a floor by construction \u2014 the rule is withheld, so the altered-key answer is essentially unreachable and the p-value is theatre. Compounding it, 'Consequence statements were authored with the questions,' so the single author fixed both the rule and the one answer that counts as correct, and the grader classifies matches to that authored key; the missed items quoted ('The spread-open net, presenting a far larger cross-section...') show defensible rule-consistent reasoning being graded 'neither', which cuts the other way and indicates the key is narrow rather than lenient. Neither defect overturns the 92%; both narrow what it means. The design is otherwise unusually sound: blind grader with arm labels stripped and options shuffled, three pre-declared null models, an explicit invalidity threshold on the leakage arm, depth results labelled directional and no depth claim made, misses counted conservatively.

**What would settle it.** An adversarial altered arm in which the invented rule contradicts a strong, highly available real-world prior and the ordinary-world answer is the natural lure (so the control-arm answer is an active distractor rather than an absent one), with the rule\u2013consequence keys authored by someone other than the question author and grading replicated by a different model family or human raters on the same transcripts. If altered accuracy stays near 0.9 there, the capacity claim is real; if it collapses toward the ordinary-world answer, the present result was measuring instruction-following on non-competing premises.

---

_Pre-registration integrity: prereg predates first event._
