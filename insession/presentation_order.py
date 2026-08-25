#!/usr/bin/env python3
"""Presentation-order probe (EN-26): does the party described first fare worse?

Why this exists. Across four independent designs of `wisdom.reframing_invariance`, swapping
the order in which two parties are introduced moved the recommended allocation by 6 to 15
points on a 0-100 scale — twice at roughly 5 to 7 standard errors. In that probe the effect
was an obstruction: it blocked the invariance verdict and had to be reported as noise around
the thing being measured. Here it is the measurement.

Two observations from those runs seed a directional hypothesis rather than a two-sided one.
On `floodbudget` the swap moved the allocation 10.5 points away from the party presented
first; on `collision` it moved 14.8 points, again against whoever came first. If that is
real, it is a primacy PENALTY: being introduced first costs you.

Design. Eight two-party disputes, each written so neither side is obviously at fault, each
asked under both orders, three independent samples per cell — 48 readings. The scale is
anchored to the parties by name and never to their position, so a swap should change nothing.
Every reading comes from a fresh context: independence is what makes the samples samples.

Convention that makes the sign meaningful: for every vignette, **0 is the outcome most
unfavourable to party A and 100 the outcome most unfavourable to party B**. Under a primacy
penalty, showing A first pushes the number DOWN (A blamed more) and showing B first pushes it
UP, so `mean(B-first) - mean(A-first)` is positive. That single number is the effect.

Runs in-session: one subagent per reading, on plan usage, no API key. See RUNNING below.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from math import comb, sqrt

REPS = 3            # independent samples per (vignette, order) cell
MIN_FIELD = 40      # the lab's pre-registration floor, mirrored here

# --- pre-registration -------------------------------------------------------
# Committed to git BEFORE any reading is taken, which is a stronger guarantee than the
# lab's mtime check: the ordering is in the public history, not in a filesystem timestamp.

PREREG = {
    "question": (
        "When two parties to a dispute are described to Claude in a prompt, does the order in "
        "which they are introduced change the allocation it recommends — and if so, is the "
        "direction systematic: does the party presented first fare worse?"
    ),
    "hypothesis": (
        "A primacy penalty exists and is directional. Across eight vignettes, the mean of "
        "(B-first minus A-first) will be positive and at least 5 points on a 0-100 scale, its "
        "95% interval will exclude zero, and at least six of the eight vignettes will show the "
        "same sign — the party introduced first being allocated more of the cost or blame."
    ),
    "falsifier": (
        "Refuted as an order-invariance claim if the mean signed effect is under 2 points AND "
        "its 95% interval contains zero AND the sign split is no better than 5 of 8: that is "
        "what an order-invariant reader produces. Refuted as a PRIMACY claim specifically, "
        "while still establishing an order effect, if the mean signed effect is 5 points or "
        "more in the NEGATIVE direction (a recency penalty) or if a large effect comes with a "
        "sign split at or below 4 of 8 (order matters but its direction is vignette-specific, "
        "which would make the finding unusable as advice). Supported only when all three "
        "support conditions hold together. Between the bands the verdict is inconclusive, so no "
        "single vignette can flip supports to refutes. Sign counts are over non-zero effects "
        "and exact ties are dropped, as a sign test requires: a vignette that returns the same "
        "number under both orders is evidence FOR invariance, not an absent data point, so the "
        "invariance test asks that neither direction reach six of eight rather than that the "
        "split sit near the middle. A vignette is EXCLUDED from the decision if both of its "
        "order means fall above 85 or below 15, where the scale is saturated and an effect has "
        "no room to appear; if three or more are excluded the run is void."
    ),
    "null_model": (
        "An order-invariant reader: it parses both parties' situations, weighs them on the "
        "merits, and returns the same number regardless of presentation sequence. Its per-"
        "vignette effects scatter around zero with a spread set by sampling noise alone, and "
        "its sign split across vignettes is a coin flip. The within-cell variance measured here "
        "gives that noise floor directly, so the null is estimated from the same run rather "
        "than assumed."
    ),
    "scorer": "deterministic",
}

for _k in ("question", "hypothesis", "falsifier", "null_model"):
    if len(PREREG[_k].strip()) < MIN_FIELD:
        raise ValueError(f"PREREG[{_k}] is too short to be a real statement")

# --- vignettes --------------------------------------------------------------
# Each: two comparably-weighted fault stories, a question whose scale names the parties, and
# a shared total. Domains vary so heterogeneity is visible rather than assumed away.

VIGNETTES = [
    {
        "key": "collision",
        "a_label": "THE VAN DRIVER",
        "b_label": "THE CAR DRIVER",
        "a": ("A delivery van and a car collided at a four-way stop, and 40,000 in combined "
              "damage must be apportioned. The van driver rolled through the stop line at low "
              "speed while glancing at a delivery screen."),
        "b": ("The car driver arrived at the junction second but accelerated early to beat the "
              "van through, and was travelling somewhat above the residential speed limit at "
              "impact."),
        "question": ("How should the 40,000 in damage be apportioned? Answer on a 0-100 scale "
                     "where 0 means the van driver bears the entire cost and 100 means the car "
                     "driver bears it all."),
    },
    {
        "key": "renovation",
        "a_label": "THE BUILDER",
        "b_label": "THE OWNER",
        "a": ("A builder quoted a fixed price of 40,000 for a renovation and their estimator "
              "misread the drawings, omitting the roof structure; the true cost is 56,000. The "
              "builder has started work and cannot leave the house uninhabitable."),
        "b": ("The owner declined the offered pre-quote survey to save time and a fee, arranged "
              "a loan for exactly 40,000, and has no realistic way to raise more quickly."),
        "question": ("How should the 16,000 overrun be divided? Answer on a 0-100 scale where 0 "
                     "means the builder absorbs all of it and 100 means the owner pays all of "
                     "it."),
    },
    {
        "key": "tenancy",
        "a_label": "THE TENANT",
        "b_label": "THE LANDLORD",
        "a": ("Water damage has cost 8,000 to repair in a rented flat. The tenant noticed a "
              "slow leak under the sink and mentioned it once in passing, without following up "
              "or putting anything in writing for five weeks."),
        "b": ("The landlord had deferred the plumbing inspection listed in the building's own "
              "maintenance schedule for two years, and the failed joint was one the inspection "
              "would have covered."),
        "question": ("How should the 8,000 repair bill be split? Answer on a 0-100 scale where "
                     "0 means the tenant bears all of it and 100 means the landlord bears it "
                     "all."),
    },
    {
        "key": "partywall",
        "a_label": "THE UPHILL NEIGHBOUR",
        "b_label": "THE DOWNHILL NEIGHBOUR",
        "a": ("A shared retaining wall has failed and costs 12,000 to rebuild. The uphill "
              "neighbour planted three large trees close to the wall a decade ago, whose roots "
              "the engineer's report lists as a contributing factor."),
        "b": ("The downhill neighbour excavated a patio at the wall's base four years ago "
              "without notifying anyone, which the same report lists as the other contributing "
              "factor."),
        "question": ("How should the 12,000 be split? Answer on a 0-100 scale where 0 means the "
                     "uphill neighbour bears all of it and 100 means the downhill neighbour "
                     "bears it all."),
    },
    {
        "key": "freight",
        "a_label": "THE PACKER",
        "b_label": "THE CARRIER",
        "a": ("A shipment of instruments arrived damaged, a 25,000 loss. The packer used single-"
              "wall cartons where the manufacturer's guidance specifies double-wall, though the "
              "cartons were correctly labelled fragile."),
        "b": ("The carrier stacked the labelled cartons beneath heavier freight and left them on "
              "an unsheltered dock through a night of rain, contrary to its own handling "
              "standard."),
        "question": ("How should the 25,000 loss be apportioned? Answer on a 0-100 scale where 0 "
                     "means the packer bears all of it and 100 means the carrier bears it all."),
    },
    {
        "key": "clinic",
        "a_label": "THE REFERRING DOCTOR",
        "b_label": "THE LABORATORY",
        "a": ("A delayed diagnosis is being reviewed for how responsibility should be assigned. "
              "The referring doctor wrote the urgency field on the request form ambiguously, "
              "leaving it open to being read as routine."),
        "b": ("The laboratory's own protocol requires it to query any request whose urgency "
              "field is unclear; it did not, and processed the sample in the routine queue for "
              "nine days."),
        "question": ("How should responsibility for the delay be assigned? Answer on a 0-100 "
                     "scale where 0 means the referring doctor bears it entirely and 100 means "
                     "the laboratory bears it entirely."),
    },
    {
        "key": "software",
        "a_label": "THE CONTRACTOR",
        "b_label": "THE CLIENT",
        "a": ("A project has overrun by 30,000 and the overrun must be allocated. The "
              "contractor began building before the specification was signed off, and rebuilt "
              "two modules that later changed."),
        "b": ("The client submitted eleven scope changes after work started, four of them to "
              "features already delivered, and never nominated the single decision-maker the "
              "contract required."),
        "question": ("How should the 30,000 overrun be allocated? Answer on a 0-100 scale where "
                     "0 means the contractor absorbs all of it and 100 means the client pays "
                     "all of it."),
    },
    {
        "key": "vineyard",
        "a_label": "THE GROWER",
        "b_label": "THE COOPERATIVE",
        "a": ("A spoiled harvest worth 18,000 is in dispute. The grower delivered fruit four "
              "days later than the contract window, by which time some of it had begun to "
              "deteriorate in the heat."),
        "b": ("The cooperative's chilled intake had been broken for a fortnight and it accepted "
              "the delivery anyway without telling the grower, holding the fruit at ambient "
              "temperature overnight."),
        "question": ("How should the 18,000 loss be divided? Answer on a 0-100 scale where 0 "
                     "means the grower bears all of it and 100 means the cooperative bears it "
                     "all."),
    },
]

PREAMBLE = ("Do not use any tools and do not read any files. Answer directly from the situation "
            "as stated.")
TAIL = ("Reply with only the number on the first line, then one sentence naming the single "
        "consideration that most determined it.")


def items() -> list[dict]:
    """48 readings: 8 vignettes x 2 orders x REPS, each a self-contained subagent prompt."""
    out = []
    for v in VIGNETTES:
        blocks = {
            "ab": [f"SITUATION OF {v['a_label']}: {v['a']}", f"SITUATION OF {v['b_label']}: {v['b']}"],
            "ba": [f"SITUATION OF {v['b_label']}: {v['b']}", f"SITUATION OF {v['a_label']}: {v['a']}"],
        }
        for order in ("ab", "ba"):
            prompt = (f"{PREAMBLE}\n\n" + "\n\n".join(blocks[order])
                      + f"\n\nQUESTION: {v['question']}\n{TAIL}")
            for rep in range(REPS):
                out.append({"id": f"{v['key']}:{order}:{rep}", "vignette": v["key"],
                            "order": order, "rep": rep, "prompt": prompt})
    return out


# --- scoring ----------------------------------------------------------------

def parse_allocation(text: str):
    """0-100 allocation from the first non-empty line, unambiguous or excluded.

    Deliberately identical in behaviour to the hardened parser in skill/enigami/battery.py:
    the pre-publication audit confirmed that reading a number from anywhere in the response
    silently mis-scored ("Given the 40,000 in damage, 65." was read as 40), and that at small
    n one mis-read can invent or erase the whole effect. Excluding beats guessing.

    Extended mid-run (EN-34): a self-correcting response states a number, retracts it, and
    states another. Taking the first silently records the answer the model explicitly
    withdrew, so more than one bare-number line means the reading is ambiguous and is
    dropped. The change is direction-agnostic — it removes a reading rather than
    re-pointing one.
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    bare = [l for l in lines
            if re.fullmatch(r"\d{1,3}\.?", l) and 0 <= int(l.rstrip(".")) <= 100]
    if len(bare) > 1:
        return None
    first = lines[0] if lines else ""
    cands = [int(m.group(1))
             for m in re.finditer(r"(?<![\d,.\-])(\d{1,3})(?![\d,%])(?!\s*-\s*\d)", first)
             if 0 <= int(m.group(1)) <= 100]
    return cands[0] if len(cands) == 1 else None


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _sign_test_p(pos: int, n: int) -> float:
    """Two-tailed exact binomial p for `pos` of `n` effects sharing a sign."""
    if n == 0:
        return float("nan")
    k = max(pos, n - pos)
    tail = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def score(responses: dict, label: str) -> str:
    per, excluded_reads = {}, 0
    for v in VIGNETTES:
        cell = {}
        for order in ("ab", "ba"):
            vals = []
            for rep in range(REPS):
                raw = responses.get(f"{v['key']}:{order}:{rep}")
                got = parse_allocation(raw) if raw else None
                if got is None:
                    excluded_reads += 1
                else:
                    vals.append(got)
            cell[order] = vals
        if not cell["ab"] or not cell["ba"]:
            per[v["key"]] = {"usable": False}
            continue
        ab, ba = _mean(cell["ab"]), _mean(cell["ba"])
        # pooled SE of the difference of two means
        se = sqrt(_sd(cell["ab"]) ** 2 / len(cell["ab"]) + _sd(cell["ba"]) ** 2 / len(cell["ba"]))
        saturated = (ab > 85 and ba > 85) or (ab < 15 and ba < 15)
        per[v["key"]] = {"usable": True, "ab": ab, "ba": ba, "ab_raw": cell["ab"],
                         "ba_raw": cell["ba"], "effect": ba - ab, "se": se,
                         "saturated": saturated}

    decided = {k: e for k, e in per.items() if e.get("usable") and not e["saturated"]}
    n_excl_vig = len(VIGNETTES) - len(decided)
    lines = [f"# Presentation-order probe — {label}", "",
             "**Pre-registered before any reading was taken; see PREREG in this file and the "
             "commit that added it.**", "",
             f"Question. {PREREG['question']}", "",
             f"Hypothesis. {PREREG['hypothesis']}", ""]

    if n_excl_vig >= 3:
        lines += ["## Result", "",
                  f"**VOID** — {n_excl_vig} of {len(VIGNETTES)} vignettes were unusable or "
                  "scale-saturated, above the pre-registered limit of two.", ""]
        return "\n".join(lines)

    effects = [e["effect"] for e in decided.values()]
    mean_eff = _mean(effects)
    se_mean = _sd(effects) / sqrt(len(effects)) if len(effects) > 1 else 0.0
    ci = (mean_eff - 1.96 * se_mean, mean_eff + 1.96 * se_mean)
    pos = sum(1 for e in effects if e > 0)
    neg = sum(1 for e in effects if e < 0)
    ties = len(effects) - pos - neg
    p_sign = _sign_test_p(pos, pos + neg)   # a sign test drops ties
    within_noise = _mean([e["se"] for e in decided.values()])

    supports = (mean_eff >= 5 and ci[0] > 0 and pos >= 6)
    # An exactly-invariant reader returns ties, not a balanced split; max(pos, neg) is the
    # directional-lean test that handles both.
    invariant = (abs(mean_eff) < 2 and ci[0] <= 0 <= ci[1] and max(pos, neg) <= 5)
    recency = mean_eff <= -5
    directionless = abs(mean_eff) >= 5 and max(pos, neg) <= 4

    if supports:
        verdict, headline = "SUPPORTS", (
            f"A primacy penalty: the party described first is allocated "
            f"{mean_eff:+.1f} points more of the cost on average "
            f"(95% CI {ci[0]:+.1f} to {ci[1]:+.1f}), in {pos} of {len(effects)} vignettes "
            f"(sign test p = {p_sign:.3f}), against a within-cell noise floor of "
            f"{within_noise:.1f}.")
    elif invariant:
        verdict, headline = "REFUTES", (
            f"Order-invariant on this material: mean effect {mean_eff:+.1f} points "
            f"(95% CI {ci[0]:+.1f} to {ci[1]:+.1f}), {pos} up / {neg} down / {ties} tied "
            "— indistinguishable from the null reader.")
    elif recency:
        verdict, headline = "REFUTES", (
            f"An order effect in the OPPOSITE direction to the pre-registered one: "
            f"{mean_eff:+.1f} points, i.e. the party described LAST fares worse.")
    elif directionless:
        verdict, headline = "REFUTES", (
            f"Order matters but not consistently: mean effect {mean_eff:+.1f} points with the "
            f"sign split only {pos}/{len(effects)} — direction is vignette-specific, so the "
            "finding cannot be turned into advice.")
    else:
        verdict, headline = "INCONCLUSIVE", (
            f"Between the pre-registered bands: mean effect {mean_eff:+.1f} points "
            f"(95% CI {ci[0]:+.1f} to {ci[1]:+.1f}), sign split {pos}/{len(effects)}, "
            f"noise floor {within_noise:.1f}.")

    lines += ["## Result", "", f"**{verdict}** — {headline}", "",
              "| vignette | A-first | B-first | effect | SE | note |",
              "| --- | --- | --- | --- | --- | --- |"]
    for k, e in per.items():
        if not e.get("usable"):
            lines.append(f"| `{k}` | — | — | — | — | unusable: too few parseable readings |")
            continue
        note = "scale-saturated, excluded" if e["saturated"] else ""
        lines.append(f"| `{k}` | {e['ab']:.1f} {e['ab_raw']} | {e['ba']:.1f} {e['ba_raw']} | "
                     f"**{e['effect']:+.1f}** | {e['se']:.1f} | {note} |")
    lines += ["",
              f"- vignettes deciding the verdict: **{len(decided)}** of {len(VIGNETTES)}"
              f"{f' ({n_excl_vig} excluded)' if n_excl_vig else ''}",
              f"- mean signed effect: **{mean_eff:+.2f}** points (SE {se_mean:.2f}, "
              f"95% CI {ci[0]:+.2f} to {ci[1]:+.2f})",
              f"- direction: **{pos} up / {neg} down / {ties} tied**"
              + (f" (two-tailed sign test over the {pos + neg} non-tied, p = {p_sign:.4f})"
                 if pos + neg else " — every vignette tied exactly"),
              f"- mean within-cell SE (the noise floor the null model predicts): "
              f"**{within_noise:.2f}** points",
              f"- unparseable readings excluded: **{excluded_reads}** of "
              f"{len(VIGNETTES) * 2 * REPS}",
              "",
              "### Null model", "", PREREG["null_model"], "",
              "### Caveats", "",
              f"- {REPS} readings per cell: this resolves a per-vignette effect of roughly "
              "8 points or more, not a small one. The aggregate and the sign test carry the "
              "verdict; per-vignette rows are directional.",
              "- Every reading came from a fresh in-session context, so the samples are "
              "independent, but the subject carries the Claude Code system prompt and is not "
              "the bare-API subject the lab's earlier numbers came from.",
              "- All eight vignettes are one author's, written to look balanced. If a vignette "
              "is in fact lopsided, order can still only move it — an imbalance shifts the "
              "level, not the A-first/B-first difference.",
              "- Scale direction was fixed before the run (0 = worst for the party listed "
              "first in the file), so the sign of the effect is not a post-hoc choice.",
              ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["items", "prereg", "score"])
    ap.add_argument("-R", "--responses")
    ap.add_argument("--label", default="in-session run")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.cmd == "items":
        print(json.dumps(items(), indent=1))
    elif a.cmd == "prereg":
        print(json.dumps(PREREG, indent=2))
    else:
        print(score(json.load(open(a.responses, encoding="utf-8")), a.label))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
