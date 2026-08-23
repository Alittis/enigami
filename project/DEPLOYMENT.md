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
cd ~/Developer/enigami
uv sync --extra dev
```

This creates `.venv/` and pins `anthropic>=1,<2` (1.0.0 at time of writing) and `pydantic>=2.9`.
The Mac's global `anthropic` is 0.45.2, which is too old for `output_config`; always run through
`uv run`, never the global interpreter.

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

Nothing is deployed, so there is nothing to roll back. Findings are regenerated from recorded
transcripts with `uv run enigami report`; a bad findings file is fixed by rerunning that, and a
bad run is superseded by a newer run of the same probe.

## Risk profile

- **Spend.** A full run is roughly 114 API calls, a few dollars at Opus 5 rates. There is no
  hard cap in the harness; `enigami list` prints estimates before you commit to a run.
- **Key exposure.** One secret, in one gitignored file, mode 600. `transcripts/` is gitignored
  and never contains the key.
- **No destructive operations.** The harness reads nothing outside the repo and writes only
  under `transcripts/` and `findings/`.
