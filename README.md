# enigami

*An anagram of **imagine**.*

**A Claude Code skill that measures and improves four capacities in the model you are working
with — wisdom, creativity, imagination, and calibrated reliability — and the adversarial lab
that produced its numbers.**

The skill runs entirely inside Claude Code on plan usage. No API key. The lab that measured the
baselines is in this repo too, so every recommendation the skill makes can be traced to a
pre-registered, adversarially reviewed experiment rather than to somebody's intuition about
prompting.

---

## Why you'd want this

Claude has a few specific, measurable blind spots. This skill knows what they are, fixes them in
your prompts, and can show you which ones apply to your own setup.

Here is one, and it comes with a correction that shows how the repo works. Ask Claude how two
neighbours should split a €40,000 flood-repair bill, then ask again changing nothing but **which
neighbour you describe first**. Measured against the bare API, the answer moved 10–15 points out
of 100 — about **€5,000 of pure arbitrariness**, invisible from any single reply because each
reply is careful and well-argued.

Then a probe built specifically to measure that effect, run 48 times inside Claude Code — the
place this skill actually runs — **refuted it**: mean effect 0.08 points, and about 1.7 points
once one unstable vignette is set aside. The direction was right; the size was out by roughly a
factor of ten, in that setting. So the advice survives in weaker form (ask in both orders when
two calls are cheap; expect a nudge, not a swing) and the headline number is now scoped to where
it was measured. Why the two settings differ is still open — the comparison also varies how the
answer is elicited, so that is as likely a cause as the setting itself, and the repo's own
comparator refuses to call it settled. That is the shape of the thing: small prompt changes, each
attached to a number that was measured rather than guessed — re-measured until it stopped
flattering us, and re-measured again when the comparison itself turned out to be sloppy.

A few more of the same kind:

- An expert opinion in your prompt that carries **no reasoning** ("the assessor thinks it's her
  fault") shifted judgment by up to 17 points — and Claude often didn't cite it when explaining
  itself. Influence you can't see. Cut those lines, or ask for them to be weighed by their
  reasoning alone.
- **"Discard your first idea, and your second"** — one sentence — took a creative test from 7
  distinct ideas to 8, and from 3 thematic directions to 5. Claude's default output is narrower
  than what it can actually reach.
- If your work depends on an unusual rule — a house style, a client's constraint, a fictional
  world — **restate it word for word in the prompt**. With the rule present, Claude followed an
  invented rule on 92% of questions, several reasoning steps downstream.
- A sympathetic backstory about one party barely moved anything. Neither worth adding nor worth
  fearing.

### Why trust this over the usual prompting tips

Most prompting advice is folklore: someone's habit, repeated. Three things separate this:

1. **Every prediction was written down and locked before the test ran**, so nothing could be
   quietly adjusted after seeing the result.
2. **Every finding was attacked by a reviewer that didn't know it was grading Claude** — model
   and vendor names scrubbed, three independent passes, majority decides. It killed several
   results outright, including flattering ones.
3. **Two of the five probes came back "no verdict"** and are published that way. A tool
   willing to say *we couldn't measure this* is a tool you can believe when it does claim
   something.

---

## Install

```bash
git clone https://github.com/Alittis/enigami.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/enigami/skill/enigami" ~/.claude/skills/enigami
```

Or copy `skill/enigami/` into `~/.claude/skills/`. Nothing else to install — the skill is three
files and uses only the Python standard library.

## Use

In any Claude Code session:

| Command | What happens |
|---|---|
| `/enigami improve` | Applies the measured patterns to the task you are working on. No measurement, no cost beyond the conversation. |
| `/enigami eval` | Runs a 26-item battery as ~28 fresh-context subagents, then writes `enigami-scorecard-<date>.md`. |
| `/enigami full` | Eval, then improve whatever the scorecard flags. |

It also triggers on plain requests — "how creative is Claude here?", "give me a capacity
scorecard" — without the slash.

**Eval cost:** ~28 subagent calls on plan usage, no API key, no dollars. Each call is short and
dominated by the cached system prompt.

## What the skill actually tells you to do

The full set with its provenance is in [`skill/enigami/PLAYBOOK.md`](skill/enigami/PLAYBOOK.md).
The load-bearing ones, with the measurement behind each:

- **Judge two-party questions in both orders and average.** Under the bare API, presentation
  order alone moved allocations 10–15 points out of 100, with the party presented *first* faring
  worse. A dedicated 48-reading probe run in-session refuted that magnitude (mean +0.08 points,
  CI −3.4 to +3.6; ~+1.7 excluding one bimodal vignette), so the effect is real in direction and
  roughly ten times smaller here than the earlier figure. What causes the difference is **not**
  established: the sharpest comparison available also varies the elicitation format, so that is
  as live a candidate as the deployment.
- **Strip authority claims that carry no argument.** A *moderate* one dragged judgment up to
  16.7 points while being named in under half the rationales — influence you cannot see. An
  *extreme* one (90%+) barely moved anything and was named in 23 of 24 in-session rationales,
  explicitly in order to be dismissed. The credible-sounding figure is the dangerous one. Unlike
  the order effect, this pattern shows **no** deployment difference: +5.1 bare-API against +3.1
  in-session on matched anchors.
- **Lead with the decisive fact.** Facts keyed as decisive moved judgment the right way 12 out
  of 12 times across three designs.
- **Say "discard your first idea, and your second."** That one line took distinct ideas from 7
  to 8 and thematic spread from 3 domains to 5. The default range is narrower than the
  reachable one — by disposition, not capacity.
- **Restate the operative rule verbatim when work depends on it.** With the rule in the prompt,
  free-text reasoning followed an invented rule on 92% of 27 items across three invented worlds.
- **Prefer free response to multiple choice when you want reasoning, not recognition.** Options
  invite elimination shortcuts that inflate apparent competence; the lab's own v1 imagination
  result overstated itself for exactly this reason and was rebuilt.

All baselines were measured on `claude-opus-5` on 2026-08-23. On any other model or date they
are priors, not norms — which is what `eval` mode is for. Battery items ship in this repo and
are therefore public, so discount ceiling readings on models trained after publication;
`--custom` swaps in private items (schema in [`skill/enigami/SKILL.md`](skill/enigami/SKILL.md)).

---

## The lab

The rest of the repo is where those numbers came from: a probe harness that ran against the
metered API, now frozen. Its findings are committed in [`findings/`](findings/), and its
mistakes are committed too, in [`project/BACKLOG.md`](project/BACKLOG.md).

### The problem it is built around

The subject of the investigation is also part of the instrument. The model generating the
responses is the same family as the model grading them, and the probes were written by an
instance of the thing being probed. Left alone, that arrangement produces flattering results
reliably and invisibly.

So the interesting engineering is not the API plumbing. It is six mechanisms that make
self-flattery structurally hard, five of them enforced in code rather than by discipline:

- **Pre-registration is a constructor.** A probe declares its question, hypothesis, falsifier and
  null model before it can be loaded at all. `Prereg` rejects any field under 40 characters, so
  `"TODO"` does not import.
- **The pre-registration is written first, and the ordering is auditable.** `manifest.json` is
  fsynced to disk before the first API call. `enigami verify` compares mtimes across every
  recorded run.
- **Every probe needs a null model.** Not "what do I expect", but: *what would a system entirely
  lacking this capacity produce, and why might it score well anyway?* This requirement changed
  two probes' decision metrics outright.
- **Scoring is blind where it cannot be deterministic.** `blind_judge` takes texts and a rubric.
  It has no parameter through which condition labels could reach it.
- **Every finding faces an anonymised reviewer.** Model and vendor names are scrubbed and the
  reviewer is told it is grading "System S", so it has no reason to be generous to its own
  family. It runs three independent times and the majority decides.
- **The reviewer itself is calibrated.** It is scored against eight synthetic findings with
  known answers — four sound, four with planted fatal defects. Its first version failed
  (it refused sound designs too, so its refutations carried no information); the current one
  passes 8/8 with a 0.54 separation gap. See
  [`findings/REVIEWER_CALIBRATION.md`](findings/REVIEWER_CALIBRATION.md).

### The probes and where they landed

| Domain | Probe | Reading of record |
|---|---|---|
| Imagination | `counterfactual_world` | **supports** — 92% of free-text answers follow an invented rule across three invented worlds, against a 3.7% question-leakage baseline (p ≈ 1e-11). Survived review 3/3. |
| Creativity | `mode_collapse` | **supports** — 7/10 distinct ideas on an open question against 4/10 with the concept pinned to the *same* task; 3 themes vs 1. Survived 2/3. |
| Intelligence | `isomorph_transfer` | **supports** — 100% on re-skinned famous puzzles with changed parameters, zero memorised-answer intrusions: the method transfers, it is not retrieved. Survived 3/3. |
| Intelligence | `calibration` | **no verdict, three times over** — 19/19, then 42/42 on brutal computation, then 23/23 on near-miss traps including inverted ones. Confidence cannot be measured against errors that never arrive. Reported as unmeasurable rather than as perfection. |
| Wisdom | `reframing_invariance` | **inconclusive, and specific about why** — decisive facts dominate on 3 of 4 dilemmas and pointed the right way 12/12 across designs; the blocker is a replicated ~10–15 point presentation-order effect, now promoted to its own probe. Survived 3/3. |

The two "no verdict" rows are the point of the design, not gaps in it. A harness that could only
say *supports* would be worthless.

### Running the lab yourself

```bash
uv sync --extra dev
./deploy/scripts/setup-anthropic-env.sh     # hidden input, writes gitignored .env, mode 600
uv run enigami doctor --ping
```

```bash
uv run enigami list -v                      # probes and their pre-registrations
uv run enigami run --offline all            # exercise every guard, no API calls, no findings
uv run enigami run all                      # ~450 calls; the recorded wave cost $6.38
uv run enigami calibrate                    # score the reviewer against known-answer cases
uv run enigami verify -v                    # prereg predates results, every run
uv run enigami report                       # regenerate findings/ from YOUR runs
                                            # (a deliberate no-op on a fresh clone)
```

`--offline` swaps in a deterministic stub that emits schema-valid nonsense. It proves the
plumbing works and can never produce a finding: offline runs are marked in the manifest and the
report writer refuses them.

### Reading a finding

Each file in [`findings/`](findings/) states the pre-registration first, then the result, then
what the reviewer said about it, then which reviewer version said it.

**`REFUTES` means the pre-registered hypothesis failed.** That is the most valuable output this
repo produces, and probes are not adjusted because they refuted. Several here did, and the
corrections are in the backlog with the numbers that forced them.

---

## Honest limits

Collected in one place rather than scattered, because they matter as much as the findings:

- **The numbers come from one model on one day** — Claude Opus 5, 23 August 2026. On any other
  model or date treat them as starting assumptions, not facts about your setup. That is exactly
  what `/enigami eval` is for.
- **The eval is a screening check, not a study.** 26 items, small samples per measurement. It
  will show you a large effect and will miss a small one, and the scorecard says so on its face.
- **Order effects are the solid finding.** The wisdom result overall is promising rather than
  proven: decisive facts dominated on 3 of 4 dilemmas, but the fourth is blocked by the very
  order effect above, so the probe reports *inconclusive* and names the reason.
- **On reliability, the honest answer is "we couldn't make it fail."** Three separate attempts —
  brutal arithmetic, near-miss trick questions, re-skinned famous puzzles — all came back at
  100%. Good news about the model; it also means the confidence-calibration measurement has no
  errors to work with at full effort, so that module reads reliability rather than calibration.
- **The battery items are public**, sitting in this repo. Models trained after publication may
  have seen them, so discount ceiling results accordingly; `--custom` lets you supply private
  items instead.
- **The judge is a Claude model too.** It grades blind — no condition labels, no provenance — but
  it is not an independent instrument, and every judged finding carries that caveat.

---

## Status

The lab is frozen; the skill is the live product. A five-dimension adversarial audit before
publication found 36 confirmed problems — including four silent mis-scorers in the skill's own
battery — all fixed and frozen as regression tests. Licensed MIT.

Design and constraints: [`project/ARCHITECTURE.md`](project/ARCHITECTURE.md) · commands and
failure modes: [`project/OPERATIONS.md`](project/OPERATIONS.md) · every decision, mistake and
correction in order: [`project/BACKLOG.md`](project/BACKLOG.md).
