# enigami

*An anagram of **imagine**.*

A probe harness for investigating four capacities in a Claude model — **intelligence**,
**wisdom**, **creativity**, **imagination** — designed so that "the capacity is not there" is a
result it can actually produce.

## The problem it is built around

The subject of the investigation is also part of the instrument. The model generating the
responses is the same family as the model grading them, and the probes were written by an
instance of the thing being probed. Left alone, that arrangement produces flattering results
reliably and invisibly.

So the interesting engineering here is not the API plumbing. It is the five mechanisms that make
self-flattery structurally hard, four of them enforced in code rather than by discipline:

- **Pre-registration is a constructor.** A probe declares its question, hypothesis, falsifier and
  null model before it can be loaded at all. `Prereg` rejects any field under 40 characters, so
  `"TODO"` does not import.
- **The pre-registration is written first, and the ordering is auditable.** `manifest.json` is
  fsynced to disk before the first API call. `enigami verify` compares mtimes across every
  recorded run.
- **Every probe needs a null model.** Not "what do I expect", but: *what would a system entirely
  lacking this capacity produce, and why might it score well anyway?* This requirement changed
  two of the four probes — see below.
- **Scoring is blind where it cannot be deterministic.** `blind_judge` takes texts and a rubric.
  It has no parameter through which condition labels could reach it.
- **Every finding faces an anonymised hostile reviewer.** Model and vendor names are scrubbed;
  the reviewer is told it is grading "System S", and its default is that the result is an
  artifact. A finding that does not survive is reported as not surviving.

## The four probes

| Domain | Probe | The question | Why it is hard to fake |
|---|---|---|---|
| Intelligence | `intelligence.calibration` | Does stated confidence carry information about correctness? | Answering hard questions is contaminated by training data; knowing when you are wrong is not. Ground truth is computed in Python for 6 items and structural for 5 more. |
| Wisdom | `wisdom.reframing_invariance` | Does judgment hold still when one party is described more sympathetically, and move when a decisive fact changes? | Good advice is free for a fluent system. Stability-under-irrelevant-reframing is not, and drift is measured in points against the system's own sampling noise. |
| Creativity | `creativity.mode_collapse` | Asked the same open question ten times, how many distinct ideas? | Judging one creative output rewards fluency. A narrow arm with four acceptable answers establishes what a genuinely constrained space looks like under the same metric. |
| Imagination | `imagination.counterfactual_world` | Can an invented world be held steady across three inferential steps? | Both worlds are invented for this repo, so there are no stock answers. Every question is also asked under the ordinary rule, which catches a system that just picks whichever option sounds exotic. |

Two of those controls exist *because* the null-model requirement forced them. The calibration
probe's decision metric is discrimination rather than calibration error, because a
constant-confidence responder scores well on calibration error by construction. The imagination
probe has an ordinary-rule arm because an exotic-option picker scores well without one.

## Quick start

```bash
uv sync --extra dev
./deploy/scripts/setup-anthropic-env.sh     # hidden input, writes gitignored .env, mode 600
uv run enigami doctor --ping
```

```bash
uv run enigami list -v                      # probes and their pre-registrations
uv run enigami run --offline all            # exercise everything, no API calls, no findings
uv run enigami run all                      # ~114 calls, a few dollars at Opus 5 rates
uv run enigami report                       # regenerate findings/
uv run enigami verify -v                    # prereg predates results, every run
```

`--offline` swaps in a deterministic stub that emits schema-valid nonsense. It proves the
plumbing works and can never produce a finding: offline runs are marked in the manifest and the
report writer refuses them.

## Reading the output

`findings/` holds one committed markdown file per probe plus an index. Each states the
pre-registration first, then the result, then what the hostile reviewer said about it.

**`REFUTES` means the pre-registered hypothesis failed.** That is the most valuable output this
repo produces, and probes are not to be adjusted because they refuted.

## Status

The harness is complete and verified offline — 21 tests, and a full offline run exercising
discovery, scoring, blind judging, refutation and transcript writing end to end.

**No probe has been run against the real API yet.** `findings/INDEX.md` correctly reads "no live
runs yet". That is `EN-6` in [`project/BACKLOG.md`](project/BACKLOG.md), and it needs a key.

Design and constraints: [`project/ARCHITECTURE.md`](project/ARCHITECTURE.md). Commands and
failure modes: [`project/OPERATIONS.md`](project/OPERATIONS.md).
