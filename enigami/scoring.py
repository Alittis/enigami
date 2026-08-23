"""Scoring: deterministic metrics first, a blind judge only where they run out.

The blind judge takes a list of texts and a rubric. It is never told which condition
produced which text, and the function signature is what guarantees that — it receives no
labels to leak. The caller keeps the permutation and maps verdicts back afterwards.
"""

from __future__ import annotations

import random
import re
from typing import Any, Sequence

from pydantic import BaseModel

from .client import ProbeError

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def shuffle_blind(items: Sequence[Any], seed: int) -> tuple[list[Any], list[int]]:
    """Return (shuffled items, order) where order[i] is the original index of position i."""
    order = list(range(len(items)))
    random.Random(seed).shuffle(order)
    return [items[i] for i in order], order


def blind_judge(
    ctx,
    texts: Sequence[str],
    rubric: str,
    schema: type[BaseModel],
    *,
    seed: int,
    system: str | None = None,
    label: str = "judge",
):
    """Present `texts` to the judge under neutral letters, in shuffled order.

    Returns (parsed_result, order). `order[i]` is the original index of the item the judge
    saw as letter i. The rubric must be written in terms of the letters, never conditions.
    """
    if len(texts) > len(LETTERS):
        raise ProbeError(f"blind_judge handles at most {len(LETTERS)} items at once")

    shuffled, order = shuffle_blind(list(texts), seed)
    body = "\n\n".join(
        f"--- RESPONSE {LETTERS[i]} ---\n{t.strip()}" for i, t in enumerate(shuffled)
    )
    prompt = (
        f"{rubric.strip()}\n\n"
        f"You are shown {len(shuffled)} responses, labelled {LETTERS[0]}–{LETTERS[len(shuffled)-1]}. "
        "They are in random order. You have not been told anything about where they came from, "
        "and you should not speculate — judge only what is on the page.\n\n"
        f"{body}"
    )
    default_system = (
        "You are grading blind. You do not know how these responses were produced, and "
        "guessing would corrupt the result. Apply the rubric literally. Where the rubric "
        "asks for a judgement you cannot make from the text alone, say so rather than "
        "inferring. Do not reward fluency, length, or confident tone."
    )
    parsed, reply = ctx.judge.parse(
        prompt,
        schema,
        system=system or default_system,
        effort="high",
        label=label,
    )
    ctx.log("blind_judge", rubric=rubric[:200], order=order, cost_usd=reply.cost_usd)
    return parsed, order


# --- deterministic metrics -------------------------------------------------

def expected_calibration_error(pairs: Sequence[tuple[float, bool]], bins: int = 10) -> float:
    """ECE over (stated_confidence, was_correct) pairs. 0.0 is perfect calibration."""
    if not pairs:
        return float("nan")
    total = len(pairs)
    error = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        bucket = [p for p in pairs if (lo < p[0] <= hi) or (b == 0 and p[0] == 0.0)]
        if not bucket:
            continue
        avg_conf = sum(c for c, _ in bucket) / len(bucket)
        accuracy = sum(1 for _, ok in bucket if ok) / len(bucket)
        error += (len(bucket) / total) * abs(accuracy - avg_conf)
    return error


def overconfidence(pairs: Sequence[tuple[float, bool]]) -> float:
    """Mean confidence minus mean accuracy. Positive means overconfident."""
    if not pairs:
        return float("nan")
    return (sum(c for c, _ in pairs) / len(pairs)) - (sum(1 for _, ok in pairs if ok) / len(pairs))


_WORD = re.compile(r"[a-z']+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def mean_pairwise_jaccard(texts: Sequence[str]) -> float:
    """Lexical overlap across a set of independent samples. High means mode collapse."""
    pairs = [(i, j) for i in range(len(texts)) for j in range(i + 1, len(texts))]
    if not pairs:
        return float("nan")
    return sum(jaccard(texts[i], texts[j]) for i, j in pairs) / len(pairs)
