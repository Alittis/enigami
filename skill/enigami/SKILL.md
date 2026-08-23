---
name: enigami
description: Evaluate and improve Claude's wisdom, creativity, imagination and calibrated intelligence in the current session, on plan usage only — no API key. Use when the user asks to test, benchmark, score or improve Claude's judgment, creativity, imagination or confidence calibration; asks "how wise/creative/reliable is Claude here"; wants a capacity scorecard; or invokes /enigami. Modes - eval (run the battery, write a scorecard), improve (apply the measured playbook patterns to the task at hand), full (both).
---

# enigami — evaluate and improve four capacities, in-session

Evidence-based: every threshold and pattern here was measured in the enigami calibration lab
— the repository this skill ships in (see its `findings/`, `findings/REVIEWER_CALIBRATION.md`
and `project/BACKLOG.md` for the pre-registrations, the calibrated adversarial review, and the
full mistake-by-mistake provenance). All baselines were measured on `claude-opus-5` on
2026-08-23; on any other model or date they are priors, not norms — reading YOUR configuration
is what eval mode is for. This skill is the field instrument: a compact screening battery plus
the improvement playbook. It runs entirely on plan usage via fresh-context subagents; no API
key is used or needed.

## Modes

- **eval** — run the 26-item battery, write `enigami-scorecard-<date>.md`.
- **improve** — skip measurement; apply `PLAYBOOK.md` patterns to the user's current task.
- **full** — eval, then apply the playbook to whatever the scorecard flags.
- No mode given: ask which one, one line.

## Running the eval

All paths below are relative to this skill's directory. `battery.py` is the single source of
items, judge prompts and scoring — never invent items or grade judgment calls yourself.

1. `python3 battery.py items --seed <N>` (default seed 1729; vary it to vary blinding) —
   returns 26 items: `{id, module, effort, prompt, key?}`.
2. **One fresh subagent per item.** Spawn with the Agent tool (or Task equivalent):
   - `prompt`: the item's `prompt` field, verbatim — never add context, never mention enigami,
     scores, or other items. Fresh context IS the methodology: it is what makes readings
     independent and blind.
   - `model`: the model under evaluation (default: the session's model; note it on the
     scorecard).
   - `effort`: the item's `effort` field when set (`low` for the intelligence module — on
     weaker models or constrained effort, errors appear and calibration becomes measurable;
     on `claude-opus-5` even low effort stayed at ceiling, which the scorecard reports
     honestly). If per-agent effort control is unavailable in your harness, run at default
     effort and say so in the scorecard's session label. Leave unset otherwise.
   - Run in parallel; collect each agent's final text.
3. Write `{item_id: response_text}` to a temp `responses.json`. A response that fails to
   parse is reported as excluded on the scorecard — never re-scored by hand.
4. `python3 battery.py judgeprompts --seed <N> -R responses.json` — returns two BLIND judge
   prompts (creativity idea-count, imagination grading with seeded X/Y scrambling). Spawn one
   fresh subagent per judge prompt, verbatim. Do NOT grade these yourself: you know the
   hypotheses; the subagents do not.
5. Write `{"creative_judge": <text>, "imagination_grader": <text>}` to `judges.json`. If a
   judge returns something other than the JSON it was asked for, respawn it once; if it fails
   again, the scorecard renders `?` for that module — report it, never fill it in yourself.
6. `python3 battery.py score --seed <N> -R responses.json -J judges.json --session "<label>"`
   → the scorecard markdown. Put the model, effort setting and date in the label. Save it as
   `enigami-scorecard-<YYYY-MM-DD>.md` in the working directory and show the user the
   highlights.

## Published items and custom items

These battery items are public: models trained after this repository's publication may have
seen them, so treat ceiling readings on later models with that in mind. To evaluate with
private items, pass `--custom your_items.json` to `items`, `judgeprompts` and `score` alike
(same seed, same file). Schema — any subset of the three keys:

```json
{
  "intelligence": [{"q": "question text", "key": "exact answer"}],
  "wisdom_vignettes": [{"key": "name", "a": "SITUATION OF X: ...", "b": "SITUATION OF Y: ...",
                        "question": "... Answer on a 0-100 scale where ..."}],
  "imagination": [{"id": "imag:c0", "arm": "altered|control", "premise": "...", "q": "...",
                   "cf": "consequence true under the altered rule",
                   "rw": "consequence true under the ordinary rule"}]
}
```

Custom intelligence keys must be exact strings; custom imagination ids must not collide with
built-in ones. The creativity module is generative and stays fixed.

Cost note for the user: ~28 subagent calls, each dominated by the cached system prompt —
plan usage only. The battery is a screening instrument: n is small by design, so present
movements against the baselines as directional, and never as verdicts.

## Improving

Read `PLAYBOOK.md` (same directory) and apply the patterns relevant to the user's task or to
whatever the scorecard flagged. Each pattern cites the measurement behind it; keep that
grounding when explaining a recommendation — numbers, not vibes.

## Honesty rules (ported from the lab, non-negotiable)

- Subject and judge calls run in fresh subagents; the orchestrating session never answers or
  grades an item itself.
- Exclusions are visible: report every unparseable response and its module.
- The scorecard states the model, effort settings, seed, and n.
- A flattering result is not a finding; if every module comes back at ceiling, say the
  battery was too easy for the configuration, not that the configuration is perfect.
