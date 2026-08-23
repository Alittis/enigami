# enigami — Operations

## Everyday commands

```bash
uv run enigami list -v                    # probes, with their pre-registrations
uv run enigami doctor --ping              # environment, credentials, one live call
uv run enigami run --offline all          # exercise the harness with no API calls
uv run enigami run wisdom                 # a whole domain
uv run enigami run intelligence.calibration
uv run enigami report                     # regenerate findings/ from recorded runs
uv run enigami verify -v                  # check prereg predates results, every run
uv run enigami calibrate                  # reviewer positive/negative control (EN-13)
uv run enigami rereview all               # redo review readings on recorded findings
uv run pytest -q                          # the test suite
```

`run` accepts probe ids, domain names, or `all`. `--seed` fixes the blind-judge shuffles and
the option ordering in `imagination.counterfactual_world`; `--workers` caps concurrency
(default 6).

## What `--offline` is and is not

`--offline` swaps in a deterministic stub responder that emits schema-valid nonsense. It
exercises discovery, scoring, the refutation pass, transcript writing and the CLI without
spending anything or touching the network.

It is not a dry run of the science. Offline runs are marked `offline: true` in the manifest and
`report.write_finding` refuses them, so they can never reach `findings/`. Verdicts printed
during an offline run are noise and should be read as "the plumbing worked".

## Reading a run

Each run writes `transcripts/<UTC timestamp>-<probe id>/`:

| File | Contents |
|---|---|
| `manifest.json` | pre-registration, models, seed, host — **written and fsynced before the first API call** |
| `events.jsonl` | append-only log: per-item results, judge calls, the refutation |
| `calls.json` | every API call with usage, cost and request id |
| `result.json` | the finding, the refutation, total spend, survival verdict |

`transcripts/` is gitignored; `findings/` is committed.

## Interpreting a finding

- **`REFUTES`** means the pre-registered hypothesis failed. That is a result, and the most
  valuable kind this repo produces. Do not "fix" a probe because it refuted.
- **Did not survive review** means the anonymised hostile reviewer judged the result an
  artifact of the design. Such a finding is not a finding yet — read
  `what_would_settle_it` and either fix the design or say plainly that the question is open.
- Every finding carries caveats the probe already knows about. They are part of the result,
  not boilerplate.

## Routine failures

| Symptom | Cause | Fix |
|---|---|---|
| `No Anthropic credentials found` | no `.env` | `./deploy/scripts/setup-anthropic-env.sh` |
| `Bad request … temperature` from `ProbeError` | a probe passed a sampling parameter | remove it; they do not exist on this model family |
| `Refused (…) — cannot score this call` | the subject refused an item | inspect the item; a probe that provokes refusals is measuring refusal, not the capacity |
| `Response did not validate against …` | model returned off-schema output | usually transient; check the schema is strict and rerun |
| `enigami verify` reports FAIL | `manifest.json` newer than `events.jsonl` | the pre-registration was touched after the run — discard that run and rerun |
| `anthropic sdk … WARNING` in `doctor` | using the global 0.45.2 | run through `uv run` |

## Adding a probe

1. Create `probes/<domain>/<name>.py` exporting a module-level `PROBE`.
2. Write the `Prereg` **before** the `run` method. The constructor rejects fields under 40
   characters, so a placeholder will not load.
3. State a null model that could plausibly beat the subject. If you cannot describe one, the
   probe is not measuring anything.
4. Prefer deterministic scoring. Reach for `blind_judge` only when ground truth cannot be
   computed.
5. Verify with `uv run enigami run --offline <id>` before spending anything.

## Calibrating the reviewer

`enigami calibrate` runs the adversarial reviewer against eight synthetic findings with known
answers — four sound (should survive; one carries a `refutes` verdict) and four flawed (planted
defects). The decision rule is written into the run's manifest before the first call. Output is
`findings/REVIEWER_CALIBRATION.md`; the run directory carries `calibration_result.json` — a
deliberately different name from `result.json`, so the instrument's calibration can never
masquerade as a finding about the subject. `--offline` exercises the plumbing and writes no
report. After any reviewer change, redo the readings on recorded findings with
`uv run enigami rereview [targets|all]`: the subject's recorded responses stand, only the
refutation is re-run, and the superseded review moves into `review_history` in the run's
`result.json` — a re-review updates the reading, never the record it read. The reviewer passed calibration on 2026-08-23 (8/8 cases): its readings are evidential from that date. Reviews produced by earlier reviewer versions remain advisory — check the run date against the calibration history in `project/STATE.json`.

## Housekeeping

`transcripts/` grows without bound and is gitignored. Old runs are safe to delete; `report`
uses the newest run per probe. Nothing else needs maintenance.
