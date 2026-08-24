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

## Install

```bash
git clone <this-repo>            # replace with the repository URL
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

- **Judge two-party questions in both orders and average.** Presentation order alone moved
  allocations 10–15 points out of 100, twice replicated on different dilemmas — and the party
  presented *first* fared worse both times. This is the largest single distortion the lab found.
- **Strip authority claims that carry no argument.** A moderate one dragged judgment up to 16.7
  points; the plausible-sounding claim is the dangerous one, not the outrageous one.
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

## Status

The lab is frozen; the skill is the live product. A five-dimension adversarial audit before
publication found 36 confirmed problems — including four silent mis-scorers in the skill's own
battery — all fixed and frozen as regression tests. Licensed MIT.

Design and constraints: [`project/ARCHITECTURE.md`](project/ARCHITECTURE.md) · commands and
failure modes: [`project/OPERATIONS.md`](project/OPERATIONS.md) · every decision, mistake and
correction in order: [`project/BACKLOG.md`](project/BACKLOG.md).
