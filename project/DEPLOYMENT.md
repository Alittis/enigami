# enigami — Deployment

## Status

**This app does not deploy.** It is a local research CLI run from a developer Mac against the
Anthropic API. There is no server, no systemd unit, no Caddy site, no container, no port, and
no mobile artifact. Sections that would describe those have been deleted rather than left
empty.

The only external dependency is `api.anthropic.com`.

## Install

Requires Python 3.10+ and `uv`.

```bash
cd <your clone of this repo>
uv sync --extra dev
```

This creates `.venv/` and pins `anthropic>=1,<2` (1.0.0 at time of writing) and `pydantic>=2.9`.
Any system-wide `anthropic` older than 1.x lacks `output_config` and will fail; always run
through `uv run`, never a global interpreter.

## Credentials

The API key goes in `.env`, which is gitignored. Never edit it by hand.

```bash
./deploy/scripts/setup-anthropic-env.sh
```

The script prompts with hidden input, refuses to write to a target `git check-ignore` does not
cover, `chmod 600`s the file, and upserts idempotently — pressing Enter keeps the current value.
Re-run it to rotate the key.

Confirm the result:

```bash
uv run enigami doctor --ping
```

`doctor` reports the SDK version, whether credentials resolve, the subject and judge models, and
how many probes load. `--ping` adds one cheap live call (a few thousandths of a cent).

## Rollback

Nothing is deployed, so there is nothing to roll back. Findings are regenerated from the
transcripts in your own checkout with `uv run enigami report`; a bad findings file is fixed by
rerunning that, and a bad run is superseded by a newer run of the same probe. On a fresh clone
`transcripts/` is empty (it is gitignored), so `report` is a deliberate no-op there rather than
an overwrite of the committed findings.

## Risk profile

- **Spend.** A full run of all five probes is roughly 450 API calls; the recorded
  2026-08-23 wave cost $6.38 at Opus 5 rates. There is no
  hard cap in the harness; `enigami list` prints estimates before you commit to a run.
- **Key exposure.** One secret, in one gitignored file, mode 600. `transcripts/` is gitignored
  and never contains the key.
- **No destructive operations.** The harness reads nothing outside the repo and writes only
  under `transcripts/` and `findings/`.
