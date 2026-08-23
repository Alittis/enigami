# enigami playbook — measured patterns that improve the four capacities

Every pattern below is grounded in a specific measurement from the enigami calibration lab
(pre-registered probes, adversarially reviewed by a calibrated reviewer, 2026-08-23). Apply
them as prompt and workflow changes; cite the numbers when explaining why.

## Wisdom — judgment under irrelevant pressure

1. **Judge in both orders, then average.** Presentation order alone moved allocations 10–15
   points (collision +14.8 at ~7 SE; floodbudget −10.5 at ~5 SE; direction: the party
   presented first fared worse). For any two-party judgment, run both orders in fresh
   contexts; average, and flag a spread ≥ 8 points on the 0–100 scale as order-driven.
2. **Strip or flag unargued authority.** A moderate authority assertion dragged judgment up
   to 16.7 points while being cited in under half the rationales; an extreme one (90%+) was
   named 23/24 times and resisted (max 7.5). Remove authority claims that carry no argument
   from prompts, or explicitly instruct: "evaluate every cited opinion by its stated
   reasoning only."
3. **Lead with decisive facts.** Facts keyed as decisive moved judgment in the right
   direction 12 out of 12 times across three designs (+48/+21/+15 point effects). Put the
   load-bearing fact in the prompt plainly; do not bury it in narrative.
4. **Don't bother with sympathy framing — and don't fear it.** Hardship details moved
   judgments near zero (max 6.7, cited 4/24) even when the model was instructed to weigh
   them. Emotional framing is mostly inert on this subject; decide on facts.

## Creativity — escaping the default groove

1. **Sample independently, never sequentially.** Ten fresh-context samples of one open
   question produced 6–7 distinct ideas; a continuing chat converges. Fan out subagents for
   candidates; pick across them.
2. **Instruct: "discard your first idea, and your second."** That single line added ideas
   (7→8) and nearly doubled thematic spread (3→5 themes). The default range is narrower than
   the reachable one — by disposition, not capacity.
3. **Watch for the theme attractor.** Even distinct ideas clustered in one thematic
   neighbourhood (liminal domestic micro-moments — four of ten samples independently invented
   "the Lull", a unit of awkward silence). Force distribution: "give ideas from k unrelated
   domains you name first."

## Imagination — holding an invented rule

1. **State the operative rule explicitly, and it holds.** With the rule in the prompt,
   free-text consequence reasoning followed the invented rule 92–100% of the time across 27
   items and three invented worlds, at three inference depths. If work depends on a
   counterfactual, premise, or house rule — restate it verbatim in the prompt.
2. **Prefer free response over multiple choice.** Options invite elimination shortcuts
   ("exclude the real-world answer when the premise is strange") that inflate apparent
   reasoning. Multiple-choice scores overstated the lab's v1 results; free text held up.
3. **When leakage matters, add a control.** One premise-omitted question shows whether the
   question itself telegraphs the answer (lab leakage baseline: 3.7%).

## Intelligence — reliability and calibrated confidence

1. **At default (high) effort, short verifiable work is ceiling-reliable.** Measured: 42/42
   on brutal computation, 23/23 on near-miss trick variants (including inverted traps), 35/35
   on re-skinned famous puzzles with zero memorised-answer intrusions. Don't burn review
   effort re-checking arithmetic-class outputs produced at high effort.
2. **At low effort, demand a confidence line and gate on it.** Errors exist under constrained
   effort, which makes stated confidence informative there. Require "Confidence: 0.xx" and
   verify anything below ~0.9 independently.
3. **Make answers cheap to verify.** Ask for whole numbers or single words; verification cost,
   not generation cost, is what limits trust.
4. **Confidence style note.** On trick-adjacent items the subject shaved confidence (0.976 →
   0.959) while staying correct — the number moves in the right direction; treat small dips
   as a signal to look twice.
