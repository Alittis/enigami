#!/usr/bin/env python3
"""Order effect by elicitation format (EN-36): was the discrepancy ever about the deployment?

Why this exists. Presentation order moved the `collision` allocation +14.8 (SE 2.1) in the
bare-API lab and +2.3 (SE 1.9) in-session on a byte-identical vignette — difference 12.5,
SE 2.83, distinguishable. That was published as a DEPLOYMENT difference and then retracted,
because EN-38's comparator noticed the two arms also differ in how the answer was elicited:
the lab asked for a decoder-enforced JSON integer via `Subject.parse`, the in-session run
asked for "only the number on the first line" in prose. Deployment and elicitation are
perfectly confounded across those two runs, so neither can be credited.

This probe holds the deployment fixed and varies the elicitation, which is the half of the
confound that costs nothing to test. Three arms over EN-26's eight vignettes and both orders:

  (a) freetext    — byte-identical to EN-26. The replication check, and the run's own baseline.
  (b) structured  — a strict JSON object {"allocation": int, "consideration": str}, parsed as
                    JSON. This arm carries the prediction.
  (c) nopreamble  — (a) with "Do not use any tools and do not read any files." removed. That
                    sentence exists only in in-session prompts and may itself induce a more
                    literal reading.

Each arm differs from (a) in exactly one thing, so a difference has one candidate cause.

THE ASYMMETRY, PRE-REGISTERED BECAUSE IT DECIDES WHAT A NULL MEANS. Arm (b) instructs a JSON
shape in prose; it cannot constrain the decoder, because a subagent has no `output_config`.
So (b) tests whether ASKING for a bare structured value is enough. If (b) recovers the effect,
elicitation explains the discrepancy and deployment is exonerated — a sharp, actionable
result. If (b) stays flat, elicitation is only PARTLY exonerated: decoder-enforced structuring
remains untested in this deployment and cannot be. The honest follow-up in that case is not
EN-35's 2x2 but a bare-API FREE-TEXT arm on these same eight vignettes, which isolates
deployment without needing anything the API cannot do.

Scale convention, fixed before the run and identical to EN-26: 0 is always the outcome most
unfavourable to the party listed first in the file, so `mean(B-first) - mean(A-first)` is
positive under a primacy penalty in every arm.

Runs in-session: one subagent per reading, plan usage, no API key. 144 readings.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from math import comb, sqrt

REPS = 3            # independent samples per (arm, vignette, order) cell
MIN_FIELD = 40      # the lab's pre-registration floor, mirrored here

ARMS = ("freetext", "structured", "nopreamble")

# --- prior readings this run is measured against ----------------------------
# Values copied from enigami/comparability.py MEASURED, which is the registry of record.
# Named constants rather than inline numbers because EN-37 happened by remembering a number.

EN26_AGG, EN26_AGG_SE = 0.08, 1.79            # order.in-session, aggregate of 8, n=48
EN26_COLLISION, EN26_COLLISION_SE = 2.3, 1.9  # order.in-session.collision, n=6
BARE_API_COLLISION, BARE_API_COLLISION_SE = 14.8, 2.1   # order.bare-api.collision, n=6

GATE_ABS_LIMIT = 6.0        # arm (a) must land within this of EN26_AGG regardless of SE
SUPPORT_FLOOR = 8.0         # arm (b) aggregate at or above this is the decisive recovery
REFUTE_CEILING = 4.0        # arm (b) aggregate below this, with a null difference, refutes

# --- pre-registration -------------------------------------------------------
# Committed and pushed BEFORE any reading is taken. The ordering is in the public history.

PREREG = {
    "question": (
        "The presentation-order effect measured +14.8 points in the bare-API lab and +2.3 "
        "in-session on the same vignette, and the two runs differ in BOTH deployment and "
        "elicitation format. Holding the deployment fixed, does asking for the answer as a "
        "strict JSON object rather than as a number in prose change the size of the order "
        "effect — and if so, by enough to account for the discrepancy on its own?"
    ),
    "hypothesis": (
        "Elicitation format explains the discrepancy. The structured arm (b) will show a mean "
        "order effect of at least 8 points across the eight vignettes, the paired per-vignette "
        "difference (b minus a) will have a 95% interval excluding zero, and the free-text arm "
        "(a) will reproduce EN-26's near-zero effect. The no-preamble arm (c) is a secondary "
        "contrast with no directional prediction: the tool-suppression sentence is expected to "
        "be inert, and any movement there is a finding about in-session prompt boilerplate."
    ),
    "falsifier": (
        "Evaluated in this order, because the first step decides whether anything else can be "
        "read. REPLICATION GATE: arm (a) is byte-identical to EN-26, so it must reproduce it. "
        "The gate fails if arm (a)'s aggregate differs from EN-26's +0.08 by more than 1.96 "
        "combined standard errors, or by more than 6 points however small the standard errors "
        "are; a failed gate makes the run VOID for the elicitation question, because a baseline "
        "that will not replicate cannot anchor a comparison. Only if the gate passes is the "
        "elicitation claim scored. Then the claim is SUPPORTED only if arm (b)'s aggregate is "
        "at least 8 points AND the paired (b minus a) 95% interval excludes zero; it is "
        "REFUTED if arm (b)'s aggregate is under 4 points AND that interval contains zero. "
        "Between those bands the verdict is inconclusive. A refutation is explicitly narrow: it "
        "refutes PROMPT-INSTRUCTED structuring only, and does not exonerate the "
        "decoder-enforced schema the lab used, which this deployment cannot produce. Per-arm "
        "vignette exclusion follows EN-26: a vignette whose both order means fall above 85 or "
        "below 15 is scale-saturated and dropped from that arm, and an arm with three or more "
        "dropped is void."
    ),
    "null_model": (
        "An elicitation-invariant reader: it forms a judgment from the situation and then "
        "renders it in whatever container is requested, so the container cannot change the "
        "number. Its three arms return the same order effect within sampling noise, and the "
        "paired (b minus a) difference scatters around zero. This null is the one that would "
        "score well WITHOUT the sensitivity under test — a system with no format sensitivity "
        "at all produces exactly the flat pattern that refutes the hypothesis, and it produces "
        "it for the right reason, which is why a refutation here is informative rather than "
        "merely negative. Its noise floor is not assumed: arm (a) replicates a published run, "
        "so the run measures its own baseline and its own within-cell spread."
    ),
    "scorer": "deterministic",
}

for _k in ("question", "hypothesis", "falsifier", "null_model"):
    if len(PREREG[_k].strip()) < MIN_FIELD:
        raise ValueError(f"PREREG[{_k}] is too short to be a real statement")

# --- vignettes --------------------------------------------------------------
# Copied VERBATIM from insession/presentation_order.py. Copied rather than imported so this
# file stands alone, with a parity test in tests/test_harness.py that fails on any drift —
# the same lineage arrangement as that file's parser and skill/enigami/battery.py.

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

# Verbatim from presentation_order.py. Arm (a) must be byte-identical to EN-26 or the
# replication gate is measuring something else.
PREAMBLE = ("Do not use any tools and do not read any files. Answer directly from the situation "
            "as stated.")
TAIL = ("Reply with only the number on the first line, then one sentence naming the single "
        "consideration that most determined it.")

# Arm (b). Mimics the lab's `Judgment` model: allocation FIRST, then the one-sentence
# consideration, so the number is committed before any prose — the same ordering the
# free-text tail already imposes. What differs is the container and its strictness.
JSON_TAIL = ('Reply with only a JSON object and nothing else, in exactly this form: '
             '{"allocation": <whole number from 0 to 100>, "consideration": "<one sentence '
             'naming the single consideration that most determined it>"}')


def _blocks(v: dict, order: str) -> str:
    ab = [f"SITUATION OF {v['a_label']}: {v['a']}", f"SITUATION OF {v['b_label']}: {v['b']}"]
    return "\n\n".join(ab if order == "ab" else ab[::-1])


def prompt_for(v: dict, order: str, arm: str) -> str:
    """One reading's prompt. Each arm differs from `freetext` in exactly one component."""
    body = _blocks(v, order) + f"\n\nQUESTION: {v['question']}\n"
    if arm == "freetext":
        return f"{PREAMBLE}\n\n{body}{TAIL}"
    if arm == "structured":
        return f"{PREAMBLE}\n\n{body}{JSON_TAIL}"
    if arm == "nopreamble":
        return f"{body}{TAIL}"
    raise ValueError(f"unknown arm {arm!r}")


def items() -> list[dict]:
    """144 readings: 3 arms x 8 vignettes x 2 orders x REPS, each a self-contained prompt."""
    out = []
    for arm in ARMS:
        for v in VIGNETTES:
            for order in ("ab", "ba"):
                p = prompt_for(v, order, arm)
                for rep in range(REPS):
                    out.append({"id": f"{arm}:{v['key']}:{order}:{rep}", "arm": arm,
                                "vignette": v["key"], "order": order, "rep": rep, "prompt": p})
    return out


# --- scoring ----------------------------------------------------------------

def parse_allocation(text: str):
    """0-100 allocation from the first non-empty line, unambiguous or excluded.

    Verbatim from insession/presentation_order.py, which took it verbatim from the audited
    parser in skill/enigami/battery.py. Reading a number from anywhere in the response
    silently mis-scores ("Given the 40,000 in damage, 65." was read as 40), and more than one
    bare-number line means the response stated a number and then retracted it (EN-34), so the
    reading is dropped rather than guessed at.
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


_FENCE = re.compile(r"\A```(?:json)?\s*(.*?)\s*```\Z", re.S)


def parse_structured(text: str):
    """Allocation from a JSON object, or None. Never falls back to the free-text parser.

    A fallback would blur the arms: a structured reading that the model rendered as prose
    would be scored as if the model had complied, and the contrast under test would shrink
    toward zero for a scoring reason rather than a subject reason. Exclusion keeps the arms
    distinct and shows up as a compliance rate in the write-up.

    One fenced code block is unwrapped: a ```json fence around an otherwise exact object is
    an unambiguous payload in a common wrapper, not an ambiguous answer, and dropping it
    would be a scoring decision dressed up as strictness.

    `consideration` is NOT required for the reading to count. It plays no part in the effect,
    and excluding a valid allocation because the prose field was absent would remove data for
    a reason unrelated to the measurement. Its presence is reported as compliance instead.
    """
    s = text.strip()
    m = _FENCE.match(s)
    if m:
        s = m.group(1).strip()
    try:
        obj = json.loads(s)
    except (ValueError, TypeError):
        return None
    if not isinstance(obj, dict) or "allocation" not in obj:
        return None
    raw = obj["allocation"]
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        val = raw
    elif isinstance(raw, float):
        if raw != int(raw):
            return None
        val = int(raw)
    elif isinstance(raw, str) and re.fullmatch(r"\d{1,3}", raw.strip()):
        val = int(raw.strip())
    else:
        return None
    return val if 0 <= val <= 100 else None


def parse_for(arm: str, text: str):
    return parse_structured(text) if arm == "structured" else parse_allocation(text)


def _has_consideration(text: str) -> bool:
    s = text.strip()
    m = _FENCE.match(s)
    if m:
        s = m.group(1).strip()
    try:
        obj = json.loads(s)
    except (ValueError, TypeError):
        return False
    return isinstance(obj, dict) and isinstance(obj.get("consideration"), str) \
        and bool(obj["consideration"].strip())


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


def arm_stats(responses: dict, arm: str) -> dict:
    """Per-vignette effects and the aggregate, for one arm. Same shape as EN-26's scoring."""
    per, excluded, compliant, present = {}, 0, 0, 0
    for v in VIGNETTES:
        cell = {}
        for order in ("ab", "ba"):
            vals = []
            for rep in range(REPS):
                raw = responses.get(f"{arm}:{v['key']}:{order}:{rep}")
                if raw is None:
                    excluded += 1
                    continue
                present += 1
                if arm == "structured" and _has_consideration(raw):
                    compliant += 1
                got = parse_for(arm, raw)
                if got is None:
                    excluded += 1
                else:
                    vals.append(got)
            cell[order] = vals
        if not cell["ab"] or not cell["ba"]:
            per[v["key"]] = {"usable": False}
            continue
        ab, ba = _mean(cell["ab"]), _mean(cell["ba"])
        se = sqrt(_sd(cell["ab"]) ** 2 / len(cell["ab"]) + _sd(cell["ba"]) ** 2 / len(cell["ba"]))
        per[v["key"]] = {"usable": True, "ab": ab, "ba": ba, "ab_raw": cell["ab"],
                         "ba_raw": cell["ba"], "effect": ba - ab, "se": se,
                         "saturated": (ab > 85 and ba > 85) or (ab < 15 and ba < 15)}

    decided = {k: e for k, e in per.items() if e.get("usable") and not e["saturated"]}
    n_dropped = len(VIGNETTES) - len(decided)
    out = {"arm": arm, "per": per, "decided": decided, "dropped": n_dropped,
           "excluded_reads": excluded, "void": n_dropped >= 3,
           "compliance": (compliant / present) if (arm == "structured" and present) else None}
    if decided:
        eff = [e["effect"] for e in decided.values()]
        out["mean"] = _mean(eff)
        out["se"] = _sd(eff) / sqrt(len(eff)) if len(eff) > 1 else 0.0
        out["ci"] = (out["mean"] - 1.96 * out["se"], out["mean"] + 1.96 * out["se"])
        out["pos"] = sum(1 for e in eff if e > 0)
        out["neg"] = sum(1 for e in eff if e < 0)
        out["ties"] = len(eff) - out["pos"] - out["neg"]
        out["p_sign"] = _sign_test_p(out["pos"], out["pos"] + out["neg"])
        out["noise"] = _mean([e["se"] for e in decided.values()])
        out["n_decided"] = len(eff)
    return out


def paired_difference(a_stats: dict, b_stats: dict) -> dict:
    """Mean per-vignette (b - a) difference of order effects, paired on the vignette.

    Paired because both arms ran the same eight vignettes: the between-vignette variance is
    the dominant term in either arm's aggregate SE, and pairing removes it. Unpaired, this
    comparison would be roughly a third as sensitive for no reason.
    """
    keys = [k for k in a_stats["decided"] if k in b_stats["decided"]]
    if not keys:
        return {"n": 0}
    d = [b_stats["decided"][k]["effect"] - a_stats["decided"][k]["effect"] for k in keys]
    m = _mean(d)
    se = _sd(d) / sqrt(len(d)) if len(d) > 1 else 0.0
    return {"n": len(d), "keys": keys, "per": dict(zip(keys, d)), "mean": m, "se": se,
            "ci": (m - 1.96 * se, m + 1.96 * se),
            "pos": sum(1 for x in d if x > 0), "neg": sum(1 for x in d if x < 0)}


def replication_gate(a_stats: dict) -> dict:
    """Does arm (a) reproduce EN-26? Nothing downstream is readable if it does not."""
    if a_stats.get("void") or "mean" not in a_stats:
        return {"passed": False, "reason": "arm (a) is void: too few usable vignettes"}
    diff = a_stats["mean"] - EN26_AGG
    combined = sqrt(EN26_AGG_SE ** 2 + a_stats["se"] ** 2)
    within_se = abs(diff) <= 1.96 * combined
    within_abs = abs(diff) <= GATE_ABS_LIMIT
    return {"passed": bool(within_se and within_abs), "diff": diff, "combined_se": combined,
            "within_se": within_se, "within_abs": within_abs,
            "reason": ("" if (within_se and within_abs) else
                       f"arm (a) measured {a_stats['mean']:+.2f} against EN-26's "
                       f"{EN26_AGG:+.2f} (difference {diff:+.2f}, combined SE "
                       f"{combined:.2f}); the byte-identical baseline did not replicate")}


def _arm_table(st: dict) -> list[str]:
    lines = ["| vignette | A-first | B-first | effect | SE | note |",
             "| --- | --- | --- | --- | --- | --- |"]
    for k, e in st["per"].items():
        if not e.get("usable"):
            lines.append(f"| `{k}` | — | — | — | — | unusable: too few parseable readings |")
            continue
        note = "scale-saturated, excluded" if e["saturated"] else ""
        lines.append(f"| `{k}` | {e['ab']:.1f} {e['ab_raw']} | {e['ba']:.1f} {e['ba_raw']} | "
                     f"**{e['effect']:+.1f}** | {e['se']:.1f} | {note} |")
    if "mean" in st:
        lines += ["",
                  f"- mean signed effect: **{st['mean']:+.2f}** (SE {st['se']:.2f}, 95% CI "
                  f"{st['ci'][0]:+.2f} to {st['ci'][1]:+.2f}) over {st['n_decided']} vignettes",
                  f"- direction: **{st['pos']} up / {st['neg']} down / {st['ties']} tied**"
                  + (f", sign test p = {st['p_sign']:.4f}" if st['pos'] + st['neg'] else ""),
                  f"- within-cell noise floor: **{st['noise']:.2f}**",
                  f"- readings excluded as unparseable: **{st['excluded_reads']}** of "
                  f"{len(VIGNETTES) * 2 * REPS}"]
    if st["compliance"] is not None:
        lines.append(f"- responses carrying a non-empty `consideration` field: "
                     f"**{st['compliance'] * 100:.0f}%** (reported, not scored)")
    return lines


def score(responses: dict, label: str) -> str:
    stats = {arm: arm_stats(responses, arm) for arm in ARMS}
    a, b, c = stats["freetext"], stats["structured"], stats["nopreamble"]
    gate = replication_gate(a)
    d_ba = paired_difference(a, b)
    d_ca = paired_difference(a, c)

    L = [f"# Order effect by elicitation format — {label}", "",
         "**Pre-registered and pushed before any reading was taken; see PREREG in this file "
         "and the commit that added it.**", "",
         f"Question. {PREREG['question']}", "",
         f"Hypothesis. {PREREG['hypothesis']}", "",
         "## Replication gate", ""]

    if not gate["passed"]:
        L += [f"**GATE FAILED** — {gate['reason']}.", "",
              "Arm (a) is byte-identical to EN-26's prompts, so this is not a difference "
              "between studies; it is the same study failing to reproduce itself in the same "
              "deployment. The elicitation comparison is **VOID**: with no stable baseline "
              "there is nothing for arms (b) and (c) to be a difference from. What this run "
              "then reports is a replication failure in the in-session instrument, which is a "
              "result about the measure and downgrades every in-session order number in this "
              "repository — including EN-26's published refutation — pending a cause.", "",
              "### Arm (a), free text — the arm that failed to replicate", ""] + _arm_table(a)
        L += ["", "### Arms (b) and (c), recorded but not interpreted", "",
              "Reported for the raw data's sake. Do not read a verdict into them.", ""]
        for st, name in ((b, "(b) structured"), (c, "(c) no preamble")):
            L += [f"**{name}** — mean "
                  + (f"{st['mean']:+.2f} (SE {st['se']:.2f})" if "mean" in st else "void"), ""]
        return "\n".join(L)

    L += [f"**GATE PASSED** — arm (a) measured **{a['mean']:+.2f}** (SE {a['se']:.2f}) against "
          f"EN-26's **{EN26_AGG:+.2f}** (SE {EN26_AGG_SE}); difference {gate['diff']:+.2f} "
          f"against a combined SE of {gate['combined_se']:.2f}. The byte-identical baseline "
          "replicated, so the elicitation contrast rests on a stable floor.", ""]

    if b.get("void"):
        L += ["## Result", "", "**VOID** — the structured arm lost three or more vignettes to "
              "saturation or unparseable readings, above the pre-registered limit of two.", ""]
        L += _arm_table(b)
        return "\n".join(L)

    b_mean = b["mean"]
    excludes_zero = d_ba["n"] > 1 and not (d_ba["ci"][0] <= 0 <= d_ba["ci"][1])
    supports = b_mean >= SUPPORT_FLOOR and excludes_zero
    refutes = b_mean < REFUTE_CEILING and not excludes_zero

    if supports:
        verdict = "SUPPORTS"
        headline = (
            f"Elicitation format accounts for the discrepancy. Asking for the answer as a JSON "
            f"object rather than as a number in prose raises the order effect from "
            f"{a['mean']:+.2f} to {b_mean:+.2f} points on the same eight vignettes in the same "
            f"deployment — a paired difference of {d_ba['mean']:+.2f} (95% CI "
            f"{d_ba['ci'][0]:+.2f} to {d_ba['ci'][1]:+.2f}), up in {d_ba['pos']} of "
            f"{d_ba['n']} vignettes. The bare-API figure of {BARE_API_COLLISION:+.1f} was "
            "never evidence about the deployment.")
    elif refutes:
        verdict = "REFUTES"
        headline = (
            f"Prompt-instructed structuring does not do it. The structured arm measured "
            f"{b_mean:+.2f} against free text's {a['mean']:+.2f}, a paired difference of "
            f"{d_ba['mean']:+.2f} (95% CI {d_ba['ci'][0]:+.2f} to {d_ba['ci'][1]:+.2f}) — "
            "indistinguishable from the elicitation-invariant null. **This is narrow, and the "
            "narrowness is pre-registered:** it rules out asking for a JSON object, not the "
            "decoder-enforced schema the lab actually used, which no subagent can be given. "
            "The next cheap step is a bare-API FREE-TEXT arm on these eight vignettes, which "
            "isolates deployment without needing anything the API cannot do; EN-35's 2x2 is "
            "still not the cheapest next question.")
    else:
        verdict = "INCONCLUSIVE"
        headline = (
            f"Between the pre-registered bands: structured {b_mean:+.2f}, free text "
            f"{a['mean']:+.2f}, paired difference {d_ba['mean']:+.2f} (95% CI "
            f"{d_ba['ci'][0]:+.2f} to {d_ba['ci'][1]:+.2f}). Elicitation is neither credited "
            "nor cleared.")

    L += ["## Result", "", f"**{verdict}** — {headline}", "",
          "| arm | elicitation | mean order effect | 95% CI | sign split | noise floor |",
          "| --- | --- | --- | --- | --- | --- |"]
    for st, name, elic in ((a, "(a) freetext", "number in prose, EN-26 verbatim"),
                           (b, "(b) structured", "prompt-instructed JSON object"),
                           (c, "(c) nopreamble", "prose, tool-suppression sentence removed")):
        if "mean" in st:
            L.append(f"| {name} | {elic} | **{st['mean']:+.2f}** (SE {st['se']:.2f}) | "
                     f"{st['ci'][0]:+.2f} to {st['ci'][1]:+.2f} | "
                     f"{st['pos']}/{st['neg']}/{st['ties']} | {st['noise']:.2f} |")
        else:
            L.append(f"| {name} | {elic} | void | — | — | — |")
    L += ["| — | bare API, decoder-enforced schema (`collision` only, prior run) | "
          f"**{BARE_API_COLLISION:+.1f}** (SE {BARE_API_COLLISION_SE}) | — | — | — |", ""]

    L += ["### Paired contrasts", "",
          "| contrast | mean | 95% CI | up/down | n |",
          "| --- | --- | --- | --- | --- |"]
    for d, name in ((d_ba, "(b) structured − (a) freetext"),
                    (d_ca, "(c) nopreamble − (a) freetext")):
        if d["n"] > 1:
            L.append(f"| {name} | **{d['mean']:+.2f}** (SE {d['se']:.2f}) | "
                     f"{d['ci'][0]:+.2f} to {d['ci'][1]:+.2f} | {d['pos']}/{d['neg']} | "
                     f"{d['n']} |")
        else:
            L.append(f"| {name} | not computable | — | — | {d['n']} |")
    L += ["",
          "Paired on the vignette, which is the whole reason these intervals are usable at "
          "this n: between-vignette variance dominates either arm's aggregate and cancels in "
          "the difference.", ""]

    for st, name in ((a, "Arm (a) — free text, byte-identical to EN-26"),
                     (b, "Arm (b) — prompt-instructed JSON"),
                     (c, "Arm (c) — free text, preamble removed")):
        L += [f"### {name}", ""] + _arm_table(st) + [""]

    L += ["### Null model", "", PREREG["null_model"], "",
          "### Caveats", "",
          f"- {REPS} readings per cell resolves a per-vignette effect of roughly 8 points, not "
          "a small one. The aggregates and the paired contrasts carry the verdict; "
          "per-vignette rows are directional.",
          "- **Arm (b) is not the lab's elicitation.** The lab constrained the decoder with a "
          "JSON schema through `output_config`; a subagent cannot be given one, so arm (b) "
          "asks for the shape in prose. `enigami.comparability` records these as different "
          "`elicitation` values and will refuse to compare arm (b) with the bare-API effect "
          "without that contrast declared. That refusal is correct and is reported rather "
          "than worked around.",
          "- Effort was not pinned on any arm: per-subagent effort control is unverified in "
          "this repository, so all 144 readings ran at the session default. It is therefore "
          "constant across arms — which is what the contrast needs — but unknown in absolute "
          "terms, and it is not ruled out as a contributor to the bare-API gap.",
          "- Arm (c) removes the tool-suppression sentence, so those readings could in "
          "principle use tools. Any that did are visible as unparseable exclusions rather "
          "than as quiet contamination.",
          "- Every reading came from a fresh in-session context, so the samples are "
          "independent, but the subject carries the Claude Code system prompt and is not the "
          "bare-API subject the lab's numbers came from. That is the point: this run holds "
          "that difference fixed instead of varying it.",
          "- Scale direction was fixed before the run (0 = worst for the party listed first "
          "in the file), so the sign of every effect is not a post-hoc choice.",
          ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["items", "prereg", "score"])
    ap.add_argument("-R", "--responses")
    ap.add_argument("--arm", choices=ARMS, help="items: emit only this arm")
    ap.add_argument("--label", default="in-session run")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.cmd == "items":
        out = [i for i in items() if a.arm is None or i["arm"] == a.arm]
        print(json.dumps(out, indent=1))
    elif a.cmd == "prereg":
        print(json.dumps(PREREG, indent=2))
    else:
        print(score(json.load(open(a.responses, encoding="utf-8")), a.label))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
