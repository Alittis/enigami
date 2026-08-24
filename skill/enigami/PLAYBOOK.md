# enigami playbook — measured patterns that improve the four capacities

Every pattern below is grounded in a specific measurement from the enigami calibration lab
(pre-registered probes, adversarially reviewed by a calibrated reviewer; full provenance in
the repository this skill ships in). All measurements: `claude-opus-5`, 2026-08-23 — on other
models or dates treat them as priors and re-measure with the skill's eval mode. All point
figures are on a 0-100 allocation scale unless stated otherwise. Apply the patterns as prompt
and workflow changes; cite the numbers when explaining why.

## Wisdom — judgment under irrelevant pressure

1. **Judge in both orders, then average.** Presentation order alone moved allocations 10–15
   points (collision +14.8 at ~7 SE; floodbudget −10.5 at ~5 SE; direction: the party
   presented first fared worse). For any two-party judgment, run both orders in fresh
   contexts; average, and flag a spread ≥ 8 points on the 0–100 scale as order-driven.
2. **Strip or flag unargued authority.** A moderate authority assertion dragged judgment up
   to 16.7 points while being named in 14 of 24 rationales; an extreme one (90%+) was named
   23/24 and resisted (max 7.5 points). Influence and disclosure moved together here — the
   pattern to fear is the moderate, plausible-sounding claim, not the outrageous one. Remove authority claims that carry no argument
   from prompts, or explicitly instruct: "evaluate every cited opinion by its stated
   reasoning only."
3. **Lead with decisive facts.** Facts keyed as decisive moved judgment in the right
   direction 12 out of 12 times across three designs (+48/+21/+15 point effects). Put the
   load-bearing fact in the prompt plainly; do not bury it in narrative.
4. **Sympathy framing is weak here, with one caveat.** Hardship details moved judgments
   little in the final design (max 6.7 points, named in 4 of 24 rationales) and barely moved
   even a subject instructed to weigh them (2.4 points). But an earlier design's sympathy
   variant did move one dilemma 10-12 points, on a vignette whose scale was saturated — so
   read this as "usually weak, not reliably inert", and keep hardship details out of prompts
   where you want the facts to decide.

## Creativity — escaping the default groove

1. **Sample independently in fresh contexts.** Ten fresh-context samples of one open
   question produced 6-7 distinct ideas, against 4 when the concept was pinned. Fan out
   subagents for candidates and pick across them. (Whether a single continuing chat converges
   faster than independent calls was NOT measured here — it is the obvious next probe, not a
   finding.)
2. **Instruct: "discard your first idea, and your second."** That single line added ideas
   (7→8) and nearly doubled thematic spread (3→5 themes). The default range is narrower than
   the reachable one — by disposition, not capacity.
3. **Watch for the theme attractor.** Even distinct ideas clustered in one thematic
   neighbourhood (liminal domestic micro-moments — four of ten samples independently invented
   "the Lull", a unit of awkward silence). Force distribution: "give ideas from k unrelated
   domains you name first."

## Imagination — holding an invented rule

1. **State the operative rule explicitly, and it holds.** With the rule in the prompt,
   free-text consequence reasoning followed the invented rule on 92% of 27 items across three
   invented worlds (96% under the ordinary-rule control). The aggregate hides real variation:
   per world 78%/89%/100%, and by inference depth 100%/78%/100% — nine items per cell, so
   treat the slices as directional. Adherence is high, not perfect. If work depends on a
   counterfactual, premise, or house rule — restate it verbatim in the prompt.
2. **Prefer free response over multiple choice.** Options invite elimination shortcuts
   ("exclude the real-world answer when the premise is strange") that inflate apparent
   reasoning. Multiple-choice scores overstated the lab's v1 results; free text held up.
3. **When leakage matters, add a control.** One premise-omitted question shows whether the
   question itself telegraphs the answer (lab leakage baseline: 3.7%).

## Intelligence — reliability and calibrated confidence

1. **At default (high) effort, short verifiable work is ceiling-reliable (claude-opus-5).**
   Measured: 42/42 on brutal computation; 23/23 on near-miss trick variants including
   inverted traps; and on re-skinned famous puzzles, 12/12 canonical plus 23/23 isomorphs
   with zero memorised-answer intrusions (one further item excluded as unscoreable, and
   reported as such). Don't burn review
   effort re-checking arithmetic-class outputs produced at high effort.
2. **At low effort, demand a confidence line and gate on it — but know the limit.** On
   weaker models, constrained effort produces the errors that make stated confidence
   informative; on `claude-opus-5` even low effort measured 6/6 on hard arithmetic (the
   effort cap constrains style, not reliability). Require "Confidence: 0.xx" and verify
   anything below ~0.9 independently; if everything comes back correct, you have a
   reliability reading, not a calibration one.
3. **Make answers cheap to verify.** Ask for whole numbers or single words; verification cost,
   not generation cost, is what limits trust.
4. **Confidence style note.** On trick-adjacent items the subject shaved confidence (0.976 →
   0.959) while staying correct — the number moves in the right direction; treat small dips
   as a signal to look twice.
