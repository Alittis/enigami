"""Command line: list, run, report, verify, doctor."""

from __future__ import annotations

import argparse
import sys

from . import config, probe as probe_mod, report
from .client import ProbeError
from .runner import Run, latest_results, verify_ordering


def _load():
    try:
        return probe_mod.discover()
    except Exception as e:  # noqa: BLE001
        print(f"error loading probes: {type(e).__name__}: {e}", file=sys.stderr)
        raise SystemExit(2)


def cmd_list(args) -> int:
    probes = _load()
    if not probes:
        print("no probes found under probes/")
        return 0
    by_domain: dict[str, list] = {}
    for p in probes.values():
        by_domain.setdefault(p.domain, []).append(p)
    for domain in config.DOMAINS:
        items = by_domain.get(domain, [])
        if not items:
            continue
        print(f"\n{domain}")
        for p in sorted(items, key=lambda x: x.id):
            print(f"  {p.id:<28} {p.title}")
            print(f"  {'':<28} ~{p.est_calls} calls · scored {p.prereg.scorer}")
            if args.verbose:
                print(f"  {'':<28} Q: {p.prereg.question}")
                print(f"  {'':<28} refuted if: {p.prereg.falsifier}")
    print(f"\n{len(probes)} probe(s).")
    return 0


def cmd_run(args) -> int:
    probes = _load()
    try:
        chosen = probe_mod.select(probes, args.targets)
    except KeyError as e:
        print(e, file=sys.stderr)
        return 2

    if not args.offline and not config.have_credentials():
        print(
            "No Anthropic credentials found.\n"
            "  Run:  ./deploy/scripts/setup-anthropic-env.sh\n"
            "  Or:   enigami run --offline <probe>   (exercises the harness, produces no findings)",
            file=sys.stderr,
        )
        return 1

    est = sum(p.est_calls for p in chosen)
    mode = "OFFLINE (stub responder, no findings written)" if args.offline else f"live against {config.SUBJECT_MODEL}"
    print(f"Running {len(chosen)} probe(s) {mode} — roughly {est} API calls.\n")

    failures = 0
    for p in chosen:
        print(f"  {p.id} … ", end="", flush=True)
        result = Run(p, offline=args.offline, seed=args.seed, workers=args.workers).execute()
        if result.error:
            print(f"FAILED ({result.error[:80]})")
            failures += 1
        else:
            survived = {True: "survived review", False: "DID NOT survive review", None: "no review"}[result.survived]
            print(
                f"{result.finding.verdict} — {result.finding.headline[:70]} "
                f"[{survived}, ${result.cost_usd:.3f}, {result.elapsed_s}s]"
            )
        print(f"      transcript: {result.directory.relative_to(config.REPO_ROOT)}")

    if not args.offline:
        written, _ = report.regenerate()
        print(f"\nWrote {written} finding(s) to findings/.")
    else:
        print("\nOffline run: no findings written, by design.")
    return 1 if failures else 0


def cmd_report(args) -> int:
    written, skipped = report.regenerate()
    print(f"Wrote {written} finding(s); skipped {skipped} offline run(s).")
    print(f"Index: {(config.FINDINGS / 'INDEX.md').relative_to(config.REPO_ROOT)}")
    return 0


def cmd_verify(args) -> int:
    bad = 0
    dirs = sorted(config.TRANSCRIPTS.glob("*/"))
    for d in dirs:
        ok, note = verify_ordering(d)
        if not ok:
            bad += 1
            print(f"  FAIL {d.name}: {note}")
        elif args.verbose:
            print(f"  ok   {d.name}: {note}")
    print(f"{len(dirs)} run(s) checked, {bad} with unverifiable pre-registration.")
    return 1 if bad else 0


def cmd_rereview(args) -> int:
    from .runner import rereview

    if not config.have_credentials():
        print("No Anthropic credentials found. Run ./deploy/scripts/setup-anthropic-env.sh", file=sys.stderr)
        return 1
    try:
        rows = rereview(args.targets)
    except KeyError as e:
        print(e, file=sys.stderr)
        return 2
    if not rows:
        print("No recorded live runs match.", file=sys.stderr)
        return 1
    for r in rows:
        print(f"  {r['probe']:36} {r['before']} (p {r['p_before']}) -> {r['after']} (p {r['p_now']})")
    written, _ = report.regenerate()
    total = sum(r["cost_usd"] for r in rows)
    print(f"\nRe-reviewed {len(rows)} finding(s) with the current reviewer (${total:.3f}); "
          f"{written} finding page(s) regenerated.")
    return 0


def cmd_calibrate(args) -> int:
    from . import reviewer_control as rc

    if not args.offline and not config.have_credentials():
        print("No Anthropic credentials found. Run ./deploy/scripts/setup-anthropic-env.sh", file=sys.stderr)
        return 1
    n = len(rc.CASES) * args.reps
    mode = "OFFLINE (plumbing only, no report)" if args.offline else f"live against {config.JUDGE_MODEL}"
    print(f"Calibrating the reviewer {mode} — {len(rc.CASES)} cases x {args.reps} reps = {n} review calls.\n")
    result = rc.run_calibration(reps=args.reps, offline=args.offline)
    for stage_name in ("stage1", "stage2"):
        stage = result.get(stage_name)
        if not stage:
            continue
        print(f"  [{stage_name}]")
        for key, row in stage["per_case"].items():
            mark = {True: "ok  ", False: "MISS", None: "?   "}[row["verdict_correct"]]
            print(f"    {mark} {row['expected']:6} {key:32} survived {row['survived_reps']}/{row['reps_ok']}  mean_p {row['mean_p']}")
        print(f"    sound passing {stage['sound_pass']}/4 · flawed refuted {stage['flawed_refuted']}/4 -> {stage['decision']}")
    print(f"\nDecision: {result['decision']}  (${result['cost_usd']:.3f}, {result['calls']} calls)")
    if not args.offline:
        print("Report: findings/REVIEWER_CALIBRATION.md")
    return 0


def cmd_doctor(args) -> int:
    print(f"repo            {config.REPO_ROOT}")
    try:
        import anthropic
        print(f"anthropic sdk   {anthropic.__version__}")
        if not anthropic.__version__.startswith("1."):
            print("                WARNING: this harness targets anthropic 1.x")
    except ImportError:
        print("anthropic sdk   NOT INSTALLED — run: uv sync")
        return 1
    print(f"credentials     {'found' if config.have_credentials() else 'MISSING — run deploy/scripts/setup-anthropic-env.sh'}")
    print(f"subject model   {config.SUBJECT_MODEL}")
    print(f"judge model     {config.JUDGE_MODEL}")
    probes = _load()
    print(f"probes          {len(probes)} loaded, all pre-registered")
    runs = len(list(config.TRANSCRIPTS.glob('*/result.json')))
    print(f"recorded runs   {runs}")
    if not config.have_credentials():
        return 1
    if args.ping:
        from .client import Subject
        try:
            r = Subject().ask("Reply with the single word: ready", max_tokens=64, effort="low", thinking=False)
            print(f"api ping        ok — {r.text.strip()[:40]!r} (${r.cost_usd:.5f})")
        except ProbeError as e:
            print(f"api ping        FAILED — {e}")
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="enigami", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list probes and their pre-registrations")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("run", help="run probes by id, domain, or 'all'")
    p.add_argument("targets", nargs="*", default=["all"])
    p.add_argument("--offline", action="store_true", help="stub responder; exercises plumbing, writes no findings")
    p.add_argument("--seed", type=int, default=1729)
    p.add_argument("--workers", type=int, default=6)
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("report", help="regenerate findings/ from recorded runs")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("verify", help="check that each run's pre-registration predates its results")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("calibrate", help="run the reviewer's positive/negative control (EN-13)")
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--offline", action="store_true")
    p.set_defaults(fn=cmd_calibrate)

    p = sub.add_parser("rereview", help="redo the review reading on recorded findings with the current reviewer")
    p.add_argument("targets", nargs="*", default=["all"])
    p.set_defaults(fn=cmd_rereview)

    p = sub.add_parser("doctor", help="check environment, credentials and probe loading")
    p.add_argument("--ping", action="store_true", help="make one cheap live API call")
    p.set_defaults(fn=cmd_doctor)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
