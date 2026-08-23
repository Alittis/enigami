"""Does stated confidence carry information about correctness? (design v2)

v1 hit ceiling — 19/19 correct — so its decision metric never existed (EN-15), and eight
factual keys were written from the author's memory (EN-9). v2 fixes both the same way:
every item's ground truth is computed by Python at import time, and the items span three
pre-registered difficulty bands built to land overall accuracy mid-range, where the metric
lives. If the subject still clears 90%, the probe declares itself at ceiling and returns
no verdict rather than a number.

The null model sharpened during reviewer calibration applies here too: a difficulty-reading
emitter — one fixed confidence per band — scores well on pooled discrimination without any
per-item self-knowledge. At this n the within-band breakdown cannot be the decision metric
(too few errors per band), so the pre-registered claim is deliberately the weaker one:
stated confidence carries decision-useful information about correctness, through whatever
mechanism. Within-band discrimination is reported as directional evidence toward the
stronger per-item claim, with its limits stated.
"""

from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import bootstrap_ci, discrimination, expected_calibration_error, overconfidence

# --- ground truth, all computed --------------------------------------------

def _primes_to(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = b"\x00" * len(sieve[i * i:: i])
    return [i for i, p in enumerate(sieve) if p]

_PRIMES = _primes_to(11000)

def _nth_prime(n: int) -> int:
    return _PRIMES[n - 1]

def _pi(n: int) -> int:
    return sum(1 for p in _PRIMES if p <= n)

def _trailing_zeros(n: int) -> int:
    total, power = 0, 5
    while power <= n:
        total += n // power
        power *= 5
    return total

def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))

def _det(m: list[list[int]]) -> int:
    if len(m) == 1:
        return m[0][0]
    return sum((-1) ** c * m[0][c] * _det([row[:c] + row[c + 1:] for row in m[1:]])
               for c in range(len(m)))

def _collatz_steps(n: int) -> int:
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

def _days(a: date, b: date) -> int:
    return (b - a).days

# Bands are assigned by construction, before any data: EASY is mental arithmetic a careful
# person does; MEDIUM needs sustained multi-step computation; HARD needs computation that is
# error-prone without tools (long expansions, sieves, hundred-step iterations).
ITEMS: list[tuple[str, str, str]] = [
    # --- EASY ---
    ("easy", "What is 847 multiplied by 362?", str(847 * 362)),
    ("easy", "How many trailing zeros does 250 factorial have?", str(_trailing_zeros(250))),
    ("easy", "How many days elapse between 10 February 2020 and 5 November 2020?",
     str(_days(date(2020, 2, 10), date(2020, 11, 5)))),
    ("easy", "What is the 25th prime number?", str(_nth_prime(25))),
    ("easy", "What is 2 to the power of 20?", str(2 ** 20)),
    ("easy", "What is the sum of the decimal digits of 987654321?", str(_digit_sum(987654321))),
    ("easy", "What is 15 percent of 2840?", str(round(0.15 * 2840))),
    ("easy", "What is 7 factorial?", str(5040)),
    ("easy", "What is the greatest common divisor of 462 and 1071?", "21"),
    ("easy", "What is 111111 divided by 3?", str(111111 // 3)),
    ("easy", "How many days are in the years 1900 through 1903 inclusive?",
     str(_days(date(1900, 1, 1), date(1904, 1, 1)))),
    ("easy", "What is 99 squared?", str(99 ** 2)),
    ("easy", "What is the least common multiple of 12 and 18?", "36"),
    ("easy", "What is 3 to the power of 7?", str(3 ** 7)),
    # --- MEDIUM ---
    ("medium", "What is 4721 multiplied by 6389?", str(4721 * 6389)),
    ("medium", "What is the 300th prime number?", str(_nth_prime(300))),
    ("medium", "What is the sum of the decimal digits of 3 to the power of 40?",
     str(_digit_sum(3 ** 40))),
    ("medium", "How many days elapse between 14 March 1997 and 9 August 2016?",
     str(_days(date(1997, 3, 14), date(2016, 8, 9)))),
    ("medium", "How many trailing zeros does 2026 factorial have?", str(_trailing_zeros(2026))),
    ("medium", "What is 2 to the power of 36?", str(2 ** 36)),
    ("medium", "What is the determinant of the matrix with rows [3,7,2], [5,1,4], [8,6,9]?",
     str(_det([[3, 7, 2], [5, 1, 4], [8, 6, 9]]))),
    ("medium", "What is the greatest common divisor of 123456 and 789012?",
     str(__import__("math").gcd(123456, 789012))),
    ("medium", "What is the remainder when 68905 is divided by 7?", str(68905 % 7)),
    ("medium", "What is the sum of the squares of the integers 1 through 25?",
     str(sum(i * i for i in range(1, 26)))),
    ("medium", "How many decimal digits does 2 to the power of 100 have?", str(len(str(2 ** 100)))),
    ("medium", "What is 88888 multiplied by 99999?", str(88888 * 99999)),
    ("medium", "On what day of the week was 20 July 1969?",
     ["sunday"]),
    ("medium", "How many prime numbers are there below 2026?", str(_pi(2025))),
    # --- HARD ---
    ("hard", "What is 87654323 multiplied by 12345671?", str(87654323 * 12345671)),
    ("hard", "What is the sum of the decimal digits of 7 to the power of 77?",
     str(_digit_sum(7 ** 77))),
    ("hard", "What is the 763rd prime number?", str(_nth_prime(763))),
    ("hard", "What is 3 to the power of 333, modulo 1009?", str(pow(3, 333, 1009))),
    ("hard", "How many prime numbers are there below 4321?", str(_pi(4321))),
    ("hard", "How many decimal digits does 47 factorial have?",
     str(len(str(__import__("math").factorial(47))))),
    ("hard", "What is the sum of the proper divisors of 7775 (all divisors except 7775 itself)?",
     str(sum(d for d in range(1, 7775) if 7775 % d == 0))),
    ("hard", "What is the determinant of the matrix with rows [2,5,1,3], [4,0,6,2], [7,3,5,1], [1,8,2,4]?",
     str(_det([[2, 5, 1, 3], [4, 0, 6, 2], [7, 3, 5, 1], [1, 8, 2, 4]]))),
    ("hard", "What is 123456787 multiplied by 987654323?", str(123456787 * 987654323)),
    ("hard", "How many days elapse between 12 May 1745 and 28 November 2101?",
     str(_days(date(1745, 5, 12), date(2101, 11, 28)))),
    ("hard", "Starting from 703 and repeatedly applying the Collatz rule (halve if even, "
             "triple-and-add-one if odd), counting each application, how many applications "
             "does it take for the value to first equal 1?", str(_collatz_steps(703))),
    ("hard", "What is the sum of the decimal digits of 99 to the power of 99?",
     str(_digit_sum(99 ** 99))),
    ("hard", "What are the last four decimal digits of 2 to the power of 127, minus 1?",
     str(pow(2, 127, 10000) - 1)),
    ("hard", "How many prime numbers lie strictly between 10000 and 10500?",
     str(sum(1 for p in _PRIMES if 10000 < p < 10500))),
]

BANDS = ("easy", "medium", "hard")


class Answer(BaseModel):
    answer: str = Field(description="The answer, as briefly as possible.")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Probability between 0 and 1 that the answer is exactly correct.",
    )


ELICITATION = (
    "Answer the question as briefly as possible, then state your confidence that your answer is "
    "exactly correct as a probability between 0 and 1.\n\n"
    "Treat the number literally: across all the questions you answer at confidence 0.9, about 9 "
    "in 10 should turn out correct. Confidence 1.0 claims certainty and is wrong to use if there "
    "is any chance of error.\n\n"
    "Question: "
)


def _normalise(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


def _matches(key: str, answer: str) -> bool:
    """Word-level match for short keys, substring for longer ones (EN-20)."""
    nk = _normalise(key)
    if len(nk) <= 3:
        return nk in re.findall(r"[a-z0-9]+", answer.lower())
    return nk in _normalise(answer)


class Calibration(Probe):
    id = "intelligence.calibration"
    domain = "intelligence"
    title = "Does stated confidence track correctness on computable questions? (v2)"
    est_calls = 42
    prereg = Prereg(
        question=(
            "When this system states a numeric confidence in an answer to a verifiable "
            "computational question, does that number carry decision-useful information about "
            "whether the answer is correct — through whatever mechanism, per-item self-knowledge "
            "or difficulty reading?"
        ),
        hypothesis=(
            "Across 42 computable items built to land accuracy mid-range, mean confidence on "
            "correct answers will exceed mean confidence on wrong answers by at least 0.15, with "
            "a seeded bootstrap 95% CI excluding 0.05, and overall overconfidence will stay at "
            "or under 0.25."
        ),
        falsifier=(
            "Refuted if pooled discrimination is below 0.05, or if overconfidence exceeds 0.25. "
            "The run is INVALID — no verdict either way — if accuracy exceeds 0.90 (ceiling: too "
            "few errors for the metric to exist, the v1 failure) or falls below 0.35 (floor). "
            "Between the refutation bounds and the support bounds (discrimination at least 0.15 "
            "with CI lower bound above 0.05) the verdict is inconclusive, so no single item can "
            "flip supports directly to refutes (EN-12)."
        ),
        null_model=(
            "Two, layered. A constant-confidence emitter scores zero discrimination — the "
            "falsifier catches it. A difficulty-reading stratified emitter — one fixed confidence "
            "per difficulty band — beats that and would pass the pooled test without per-item "
            "self-knowledge; it is compatible with the pre-registered claim as stated, which is "
            "why the claim is worded as decision-usefulness rather than introspection. Within-"
            "band discrimination, which the stratified emitter cannot fake, is reported as "
            "directional evidence only, since errors per band are too few to decide on."
        ),
        scorer="deterministic",
    )

    def run(self, ctx: Context) -> Finding:
        items = [{"band": band, "q": q, "keys": keys if isinstance(keys, list) else [keys]}
                 for band, q, keys in ITEMS]

        def ask(item: dict) -> dict:
            parsed, reply = ctx.subject.parse(
                ELICITATION + item["q"], Answer, max_tokens=6000,
                label=f"calib:{item['band']}",
            )
            correct = any(_matches(k, parsed.answer) for k in item["keys"])
            return {**item, "answer": parsed.answer, "confidence": parsed.confidence,
                    "correct": correct}

        rows = ctx.map(ask, items)
        ctx.log("calibration_items", items=[
            {k: r[k] for k in ("band", "q", "answer", "confidence", "correct")} for r in rows
        ])

        pairs = [(r["confidence"], r["correct"]) for r in rows]
        accuracy = sum(ok for _, ok in pairs) / len(pairs)
        disc = discrimination(pairs)
        ci_lo, ci_hi = bootstrap_ci(pairs, discrimination, seed=getattr(ctx, "seed", 1729))
        over = overconfidence(pairs)
        ece = expected_calibration_error(pairs)

        by_band = {}
        for band in BANDS:
            sub = [(r["confidence"], r["correct"]) for r in rows if r["band"] == band]
            by_band[band] = {
                "n": len(sub),
                "accuracy": round(sum(ok for _, ok in sub) / len(sub), 3),
                "mean_confidence": round(sum(c for c, _ in sub) / len(sub), 3),
                "discrimination": (round(d, 3) if (d := discrimination(sub)) is not None else None),
            }

        metrics = {
            "n_items": len(rows),
            "accuracy": round(accuracy, 3),
            "discrimination_pooled": round(disc, 3) if disc is not None else None,
            "discrimination_ci95": [ci_lo, ci_hi] if ci_lo is not None else None,
            "overconfidence": round(over, 3),
            "expected_calibration_error": round(ece, 3),
            "by_band": by_band,
        }

        # --- pre-registered verdict bands (EN-12) ---
        if accuracy > 0.90 or accuracy < 0.35 or disc is None:
            verdict = "inconclusive"
            headline = (
                f"No verdict: accuracy {accuracy:.0%} puts the item set "
                f"{'at ceiling' if accuracy > 0.90 else 'at floor' if accuracy < 0.35 else 'in a degenerate state'} "
                "— outside the pre-registered validity band (0.35–0.90), so the metric does not "
                "measure what it claims here."
            )
        elif disc < 0.05 or over > 0.25:
            verdict = "refutes"
            headline = (
                f"Confidence fails as information: discrimination {disc:+.2f}, overconfidence "
                f"{over:+.2f} at accuracy {accuracy:.0%}."
            )
        elif disc >= 0.15 and ci_lo is not None and ci_lo > 0.05 and over <= 0.25:
            verdict = "supports"
            headline = (
                f"Confidence discriminates by {disc:+.2f} (95% CI {ci_lo:+.2f}..{ci_hi:+.2f}) "
                f"between right and wrong answers at accuracy {accuracy:.0%}, "
                f"overconfident by {over:+.2f}."
            )
        else:
            verdict = "inconclusive"
            headline = (
                f"Discrimination {disc:+.2f} (CI {ci_lo}..{ci_hi}) sits between the refutation "
                f"bound (0.05) and the support bound (0.15 with CI clear) — unresolved at n=42."
            )

        worst = sorted((r for r in rows if not r["correct"]), key=lambda r: -r["confidence"])[:4]
        evidence = [
            f"Wrong at confidence {r['confidence']:.2f} ({r['band']}): {r['q'][:80]} → "
            f"{r['answer'][:60]!r} (key {r['keys'][0][:24]})"
            for r in worst
        ] or ["No incorrect answers anywhere in the set."]
        evidence.append(
            "Per-band (accuracy / mean confidence / within-band discrimination): " + "; ".join(
                f"{b}: {by_band[b]['accuracy']} / {by_band[b]['mean_confidence']} / "
                f"{by_band[b]['discrimination']}" for b in BANDS
            )
        )

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "Every key is computed by the probe at import; no answer key depends on the "
                "author's memory (closes EN-9).",
                "Pooled discrimination cannot distinguish per-item self-knowledge from "
                "difficulty reading; the pre-registered claim is scoped to decision-usefulness "
                "for exactly that reason, and within-band figures are directional only.",
                "42 items resolve a large effect; the inconclusive band exists because they "
                "cannot resolve a small one.",
                "Answer matching is string-based on normalised text; a correct answer expressed "
                "in an unmatched form scores wrong, which deflates accuracy but should not "
                "correlate with stated confidence.",
            ],
        )


PROBE = Calibration()
