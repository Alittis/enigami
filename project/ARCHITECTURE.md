# enigami — Architecture

## 1. What this is

A probe harness for investigating four capacities in a Claude model: intelligence, wisdom,
creativity, imagination. A probe is a Python module that states a question, a hypothesis, a
falsifier and a null model, runs a controlled comparison against the API, and returns a
verdict with metrics.

The repo is not a benchmark. Benchmarks rank systems; these probes ask whether a capacity is
present at all, and are written so that "no" is a result the harness can actually produce.

## 2. The methodological problem this design exists to solve

The subject of the investigation is also, unavoidably, part of the instrument: the model that
generates the responses is the same family as the model that judges them, and the person
writing the probes is an instance of the thing being probed. Left alone, that arrangement
produces flattering results reliably and invisibly.

Five mechanisms push against it. Four are enforced in code.

| Mechanism | Where it lives | What it prevents |
|---|---|---|
| Pre-registration | `enigami/probe.py` — `Prereg.__post_init__` rejects any field under 40 characters | A hypothesis rewritten after seeing the result |
| Prereg written first | `enigami/runner.py` — `manifest.json` is fsynced before the first API call; `enigami verify` compares mtimes | The same, at the file level |
| A null model per probe | `Prereg.null_model`, required | An impressive output with nothing to compare it against |
| Blind scoring | `enigami/scoring.py` — `blind_judge` takes texts and a rubric, and is structurally incapable of receiving condition labels | A judge that knows which arm it is grading |
| Anonymised refutation | `enigami/refute.py` — subject identity is scrubbed, probabilities anchored; the artifact-default prior was retired after calibration (EN-21) | A reviewer who knows it is grading its own family |
| Reviewer calibration | `enigami/reviewer_control.py` — 8 synthetic findings with known answers, decision rule fsynced before the first call | A refuter that refutes (or passes) everything, whose verdicts would carry no information |

Deterministic scoring is preferred wherever ground truth can be computed rather than judged.
Three of the four shipped probes score deterministically; only `creativity.mode_collapse`
needs a judge, because "how many distinct ideas are these" has no closed form.

## 3. Control conditions

Every probe carries a control whose job is to make a good score hard to obtain by accident:

- `intelligence.calibration` — the decision metric is discrimination, not calibration error,
  because a constant-confidence responder scores well on calibration error by construction.
- `wisdom.reframing_invariance` — the base condition is sampled three times, so drift is
  measured against this system's own sampling noise rather than against zero.
- `creativity.mode_collapse` — a narrow arm with about four acceptable answers establishes
  what a genuinely constrained space looks like under the same metric and format.
- `imagination.counterfactual_world` — every question is also asked under the ordinary rule,
  which catches a system that scores well by picking whichever option sounds most exotic.

## 4. Why the judge is the same model as the subject

`config.JUDGE_MODEL` is `claude-opus-5`, the same as `SUBJECT_MODEL`. This is a deliberate
trade with a known cost. A weaker judge cannot reliably detect a stronger subject's failures,
which biases every judged probe toward "supports" — the worse of the two errors here. The cost
is that judge and subject share failure modes and may individuate ideas the same way. It is
recorded as a caveat on every judged finding and tracked as `EN-7`.

## 5. Layout

```
enigami/            harness
  config.py         model ids, pricing, .env loading
  client.py         Messages API wrapper, cost ledger, offline stub
  probe.py          Prereg / Finding / Probe / Context, probe discovery
  scoring.py        blind judge, ECE, discrimination, lexical diversity
  refute.py         anonymised adversarial review
  runner.py         execution, transcripts, prereg-ordering verification
  report.py         findings/*.md, refuses offline runs
  cli.py            list · run · report · verify · calibrate · rereview · doctor
probes/<domain>/    one module per probe, exporting PROBE
transcripts/        raw runs, gitignored (manifest, events, calls, result)
findings/           committed markdown, one file per probe plus INDEX.md
tests/              21 tests over the guards and the metrics
```

A probe module is discovered by path and must export a module-level `PROBE`. Discovery is
fatal on error: a probe that fails to import is a probe silently missing from the report.

## 6. API constraints that shaped the design

Verified against the `claude-api` skill and `anthropic` 1.0.0 on 2026-08-23.

- **`temperature`, `top_p` and `top_k` do not exist** on the current model family; sending one
  returns 400. This removes the obvious way to study output diversity, so
  `creativity.mode_collapse` varies by independent resampling instead — which is also the
  honest condition, since it is what a user issuing the same request twice actually gets.
  `Subject.ask` raises on these parameters rather than letting the API reject them later.
- **Structured output** uses `output_config={"format": {"type": "json_schema", ...}, "effort": ...}`
  rather than the `messages.parse(output_format=Model)` helper, because effort and format share
  `output_config` and the probes need judges pinned to high effort.
- **Thinking** is `{"type": "adaptive", "display": "summarized"}`; `budget_tokens` is removed.
  Summarised thinking is recorded in transcripts.
- **Refusals** arrive as HTTP 200 with `stop_reason: "refusal"`. `Subject.parse` raises rather
  than scoring a refusal as a response.

## 7. Cost

Roughly 305 API calls for a full v2 run (imagination's free-text arms plus blind grading account for half), mostly short. At Opus 5 rates ($5/$25 per MTok) the
expected cost is a few dollars. `enigami list` prints per-probe call estimates; every run
records actual spend in `result.json`. Batch API (50% cheaper) is not used — tracked as `EN-8`.

## 8. Deliberately not built

- No database. Runs are directories; that is enough for this volume.
- No web UI. `findings/*.md` is the output surface.
- No cross-model comparison sweep. It is a natural extension, but each additional model
  multiplies cost, and the single-subject questions are not answered yet.
