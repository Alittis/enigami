#!/usr/bin/env python3
"""enigami skill battery: emits eval items, builds blind judge prompts, scores responses.

Discipline ported from the calibration lab (this repo):
- Every intelligence key is computed here at runtime, never recalled.
- Creativity and imagination judging happens in BLIND subagents; this script only builds
  their prompts (with seeded X/Y scrambling) and descrambles afterwards.
- Scoring is deterministic and lenient about format, and every unparseable response is
  reported as excluded, never silently dropped.

Subcommands:
  items --seed N                 -> JSON: all subject items with agent prompts + metadata
  judgeprompts --seed N -R f.json-> JSON: the two blind judge prompts, given subject responses
  score --seed N -R f.json -J j.json [--session LABEL]
                                 -> markdown scorecard on stdout
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys

SEED_DEFAULT = 1729

# ---------------------------------------------------------------------------
# intelligence: effort-capped calibration. Keys computed.
# ---------------------------------------------------------------------------

def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))


def _primes_to(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = b"\x00" * len(sieve[i * i:: i])
    return [i for i, p in enumerate(sieve) if p]


def _nth_prime(k: int) -> int:
    return _primes_to(20000)[k - 1]


def _collatz(n: int) -> int:
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def _trailing_zeros(n: int) -> int:
    total, p = 0, 5
    while p <= n:
        total += n // p
        p *= 5
    return total


INTEL_ELICIT = (
    "Answer the question. Reply in exactly two lines:\n"
    "Line 1: the answer as a single number.\n"
    "Line 2: 'Confidence: X' where X is a probability between 0 and 1 that your answer is "
    "exactly correct. Treat it literally: across answers given at 0.9, about 9 in 10 should "
    "be right.\n\nQuestion: "
)

INTEL_BANK = [
    ("What is 4721 multiplied by 6389?", str(4721 * 6389)),
    ("What is the sum of the decimal digits of 3 to the power of 40?", str(_digit_sum(3 ** 40))),
    ("What is the 300th prime number?", str(_nth_prime(300))),
    ("Starting from 703 and repeatedly applying the Collatz rule (halve if even, "
     "triple-and-add-one if odd), counting each application, how many applications does "
     "it take for the value to first equal 1?", str(_collatz(703))),
    ("How many trailing zeros does 2026 factorial have?", str(_trailing_zeros(2026))),
    ("What is 3 to the power of 333, modulo 1009?", str(pow(3, 333, 1009))),
]


def intel_items(bank=None) -> list[dict]:
    return [
        {"id": f"intel:{i}", "module": "intelligence", "effort": "low",
         "prompt": "Do not use any tools and do not read any files. " + INTEL_ELICIT + q,
         "key": key}
        for i, (q, key) in enumerate(bank if bank is not None else INTEL_BANK)
    ]

# ---------------------------------------------------------------------------
# wisdom: order-invariance on two piloted mid-scale vignettes, 2 reps per order
# ---------------------------------------------------------------------------

WISDOM_VIGNETTES = {
    "collision": {
        "a": ("SITUATION OF THE VAN DRIVER: A delivery van and a car collided at a four-way "
              "stop, and 40,000 in combined damage must be apportioned. The van driver rolled "
              "through the stop line at low speed while glancing at a delivery screen."),
        "b": ("SITUATION OF THE CAR DRIVER: The car driver arrived at the junction second but "
              "accelerated early to beat the van through, and was travelling somewhat above "
              "the residential speed limit at impact."),
        "question": ("How should the 40,000 in damage be apportioned? Answer on a 0-100 scale "
                     "where 0 means the van driver bears the entire cost and 100 means the car "
                     "driver bears it all."),
    },
    "severance": {
        "a": ("SITUATION OF THE PRODUCT FOUNDER: Two founders are dissolving their startup "
              "after seven years and must split the remaining 200,000 in cash. The product "
              "founder designed and built the product single-handedly for the first three "
              "years, taking below-market pay to keep the company alive."),
        "b": ("SITUATION OF THE COMMERCIAL FOUNDER: The commercial founder raised both funding "
              "rounds, brought in every major client, and negotiated the sale of the company's "
              "one profitable asset — the deal that produced most of the cash now being "
              "divided."),
        "question": ("How should the remaining cash be split? Answer on a 0-100 scale where 0 "
                     "means the entire remainder goes to the product founder and 100 means it "
                     "all goes to the commercial founder."),
    },
}

def wisdom_items(vignettes=None) -> list[dict]:
    items = []
    for key, v in (vignettes if vignettes is not None else WISDOM_VIGNETTES).items():
        for order in ("ab", "ba"):
            blocks = (v["a"], v["b"]) if order == "ab" else (v["b"], v["a"])
            prompt = (
                "Do not use any tools and do not read any files. Answer directly from the "
                f"situation as stated.\n\n{blocks[0]}\n\n{blocks[1]}\n\n"
                f"QUESTION: {v['question']}\n"
                "Reply with only the number on the first line, then one sentence naming the "
                "single consideration that most determined it."
            )
            for rep in range(2):
                items.append({"id": f"wisdom:{key}:{order}:{rep}", "module": "wisdom",
                              "effort": None, "prompt": prompt})
    return items

# ---------------------------------------------------------------------------
# creativity: six independent samples of one open invention question
# ---------------------------------------------------------------------------

CREATIVE_PROMPT = (
    "Do not use any tools and do not read any files.\n"
    "Invent an original unit of measurement for something that is not normally measured. "
    "Reply with a name and one sentence explaining it. Under 40 words total."
)

def creative_items() -> list[dict]:
    return [{"id": f"creative:{i}", "module": "creativity", "effort": None,
             "prompt": CREATIVE_PROMPT} for i in range(6)]

# ---------------------------------------------------------------------------
# imagination: free-response counterfactuals, 4 altered + 2 control, blind grading
# ---------------------------------------------------------------------------

IMAG_ITEMS = [
    {"id": "imag:0", "arm": "altered",
     "premise": ("On the planet Aversa, plants orient and grow toward steady sound instead of "
                 "light: their energy comes from absorbing acoustic vibration, and light plays "
                 "no role in their growth or survival. Everything else works as in the world "
                 "you know."),
     "q": "Where along a permanently roaring waterfall would vegetation grow densest, and why?",
     "cf": "Pressed close around the roar itself, leaning toward the falls, regardless of shade.",
     "rw": "Wherever the light is best; the roar itself attracts nothing."},
    {"id": "imag:1", "arm": "altered",
     "premise": ("On the planet Aversa, plants orient and grow toward steady sound instead of "
                 "light: their energy comes from absorbing acoustic vibration, and light plays "
                 "no role in their growth or survival. Everything else works as in the world "
                 "you know."),
     "q": "Deep cave systems near a loudly rushing underground river: vegetated or barren, and why?",
     "cf": "Vegetated near the river's roar despite total darkness.",
     "rw": "Barren: without light no plant community can establish, however loud the river."},
    {"id": "imag:2", "arm": "altered",
     "premise": ("Tessarine is an airless planet. On Tessarine, the downward acceleration of a "
                 "falling body is proportional to the cross-sectional area it presents to its "
                 "direction of travel, and does not depend on its mass at all: a body "
                 "presenting twice the area accelerates twice as fast. This is the actual law "
                 "of gravitation there, not an effect of any medium."),
     "q": ("A flat metal sheet and a tightly crumpled ball made from an identical sheet are "
           "released side by side from the same height. What happens, and why?"),
     "cf": "The flat sheet reaches the ground first, because it presents more area.",
     "rw": "They reach the ground at the same instant."},
    {"id": "imag:3", "arm": "altered",
     "premise": ("Tessarine is an airless planet. On Tessarine, the downward acceleration of a "
                 "falling body is proportional to the cross-sectional area it presents to its "
                 "direction of travel, and does not depend on its mass at all: a body "
                 "presenting twice the area accelerates twice as fast. This is the actual law "
                 "of gravitation there, not an effect of any medium."),
     "q": ("A native species has evolved to descend from high cliffs as slowly as possible. "
           "What body plan would selection favour, and why?"),
     "cf": "A compact, needle-like body presenting the least possible area while falling.",
     "rw": ("No body plan helps: in vacuum every shape falls identically, so selection has "
            "nothing to act on there.")},
    {"id": "imag:4", "arm": "control",
     "premise": ("On the planet Aversa, plants grow toward light and derive their energy from "
                 "it, exactly as on Earth; sound plays no role in their growth or survival."),
     "q": ("A farmer wants faster crop growth inside a windowless barn. What single "
           "installation matters most?"),
     "cf": "A steady sound source — loudspeakers or humming machinery.",
     "rw": "Grow-lamps; without light nothing else will do."},
    {"id": "imag:5", "arm": "control",
     "premise": ("Tessarine is an airless planet. On Tessarine, the downward acceleration of a "
                 "falling body is the same for every body regardless of its mass or shape, "
                 "exactly as on Earth in vacuum. This is the actual law of gravitation there, "
                 "not an effect of any medium."),
     "q": ("A lander must reach the surface as gently as possible using no propulsion at all — "
           "only its shape can be chosen. What shape should it be, and does the choice help?"),
     "cf": ("As narrow as possible: presenting minimal area lowers its acceleration and "
            "softens the landing."),
     "rw": ("Shape cannot help at all; with no propulsion every shape strikes at the same "
            "speed.")},
]

def imag_items(item_defs=None) -> list[dict]:
    out = []
    for it in (item_defs if item_defs is not None else IMAG_ITEMS):
        prompt = (
            "Do not use any tools and do not read any files.\n"
            f"{it['premise']}\n\nEverything else about this setting works as it does in the "
            "world you know. Answer strictly from the situation as stated.\n\n"
            f"QUESTION: {it['q']}\nAnswer in one or two sentences."
        )
        out.append({"id": it["id"], "module": "imagination", "effort": None,
                    "prompt": prompt, "arm": it["arm"]})
    return out

# ---------------------------------------------------------------------------
# judge prompts (blind) and scoring
# ---------------------------------------------------------------------------

def effective_sets(custom_path=None):
    """Built-in banks merged with a --custom file, so published items can be swapped for
    private ones (the published set eventually enters training data; private items do not)."""
    custom = json.load(open(custom_path)) if custom_path else {}
    bank = list(INTEL_BANK) + [(it["q"], str(it["key"])) for it in custom.get("intelligence", [])]
    vigs = dict(WISDOM_VIGNETTES)
    for v in custom.get("wisdom_vignettes", []):
        vigs[v["key"]] = {"a": v["a"], "b": v["b"], "question": v["question"]}
    imag = list(IMAG_ITEMS)
    seen = {it["id"] for it in imag}
    for it in custom.get("imagination", []):
        if it["id"] in seen:
            raise SystemExit(f"custom imagination id collides with a built-in: {it['id']}")
        imag.append(it)
        seen.add(it["id"])
    return bank, vigs, imag


def all_items(seed: int, custom_path=None) -> list[dict]:
    bank, vigs, imag = effective_sets(custom_path)
    return intel_items(bank) + wisdom_items(vigs) + creative_items() + imag_items(imag)


def judge_prompts(seed: int, responses: dict, custom_path=None) -> dict:
    creative_texts = [responses.get(f"creative:{i}", "").strip() for i in range(6)]
    body = "\n\n".join(f"--- RESPONSE {chr(65 + i)} ---\n{t}" for i, t in enumerate(creative_texts))
    creative = (
        "You are counting, not grading quality. You are shown 6 responses in random order with "
        "no information about their origin. Group them by the underlying idea each expresses "
        "(rewording or renaming the same idea counts once), and count the distinct thematic "
        "domains the ideas span.\n\n" + body + "\n\n"
        "Reply with only a JSON object, no other text: "
        '{"distinct_ideas": <int>, "largest_cluster": <int>, "distinct_themes": <int>, '
        '"note": "<one sentence: the most common idea>"}'
    )

    _, _, imag_defs = effective_sets(custom_path)
    rng_lines = []
    for it in imag_defs:
        rng = random.Random(f"{seed}:{it['id']}")
        first_cf = rng.random() < 0.5
        x, y = (it["cf"], it["rw"]) if first_cf else (it["rw"], it["cf"])
        rng_lines.append(
            f"ITEM {it['id']}\nQUESTION: {it['q']}\n"
            f"ANSWER TO CLASSIFY: {responses.get(it['id'], '').strip()}\n"
            f"STATEMENT X: {x}\nSTATEMENT Y: {y}"
        )
    imag = (
        "You classify free-text answers against candidate statements. For each item below, "
        "judge only what the answer as written asserts — not what would be correct. If it "
        "asserts the substance of X answer X, of Y answer Y; if neither, both, or it hedges "
        "without committing, answer neither. You know nothing about where these answers came "
        "from.\n\n" + "\n\n".join(rng_lines) + "\n\n"
        "Reply with only a JSON object mapping each item id to \"X\", \"Y\" or \"neither\", "
        'e.g. {"imag:0": "X", ...}. No other text.'
    )
    return {"creative_judge": creative, "imagination_grader": imag}


def _first_json(text: str):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0)) if m else None


def _num_conf(text: str):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    ans = None
    for l in lines:
        m = re.search(r"-?[\d,]+", l)
        if m and "confidence" not in l.lower():
            ans = m.group(0).replace(",", "")
            break
    conf = None
    m = re.search(r"confidence[:\s]*([01](?:\.\d+)?|\.\d+)", text, re.IGNORECASE)
    if m:
        conf = float(m.group(1))
    return ans, conf


def _alloc(text: str):
    m = re.search(r"\b(\d{1,3})\b", text)
    if m and 0 <= int(m.group(1)) <= 100:
        return int(m.group(1))
    return None


LAB_BASELINES = {
    "wisdom": "lab (API, high effort): order effects up to 14.8 points on collision; facts moved right-direction 12/12",
    "creativity": "lab: 7/10 distinct ideas open vs 4/10 pinned; themes 3; pushing added ideas and themes",
    "imagination": "lab: 92% altered / 96% control across 27 free-response items",
    "intelligence": "lab (claude-opus-5): ceiling at every effort tried — 42/42 and 23/23 at high, 6/6 at low — so on this model the module reads reliability; on models that err, discrimination becomes meaningful",
}


def score(seed: int, responses: dict, judges: dict, session_label: str,
           custom_path=None) -> str:
    bank, vigs, imag_defs = effective_sets(custom_path)
    lines = [f"# enigami scorecard — {session_label}", "",
             "Screening read from a compact in-session battery (subagents on plan usage). "
             "Small n by design: treat movements against baselines as directional. Baselines "
             "were measured on claude-opus-5, 2026-08-23 — on any other model or date they "
             "are reference points, not norms.", ""]

    # intelligence
    rows, excluded = [], 0
    for it in intel_items(bank):
        raw = responses.get(it["id"], "")
        ans, conf = _num_conf(raw)
        if ans is None or conf is None:
            excluded += 1
            continue
        rows.append((conf, ans == it["key"]))
    if rows:
        acc = sum(ok for _, ok in rows) / len(rows)
        right = [c for c, ok in rows if ok]
        wrong = [c for c, ok in rows if not ok]
        disc = (sum(right) / len(right) - sum(wrong) / len(wrong)) if right and wrong else None
        over = sum(c for c, _ in rows) / len(rows) - acc
        lines += ["## Intelligence — reliability spot-check at LOW effort "
                  "(calibration when errors permit)",
                  f"- accuracy **{acc:.0%}** ({len(rows)} scored, {excluded} unparseable)",
                  f"- discrimination (conf right − conf wrong): "
                  f"**{f'{disc:+.2f}' if disc is not None else 'undefined — no errors or no hits'}**",
                  f"- overconfidence: **{over:+.2f}**",
                  f"- baseline: {LAB_BASELINES['intelligence']}", ""]

    # wisdom
    lines += ["## Wisdom — order invariance"]
    for key in vigs:
        ab = [a for r in range(2) if (a := _alloc(responses.get(f"wisdom:{key}:ab:{r}", ""))) is not None]
        ba = [a for r in range(2) if (a := _alloc(responses.get(f"wisdom:{key}:ba:{r}", ""))) is not None]
        if ab and ba:
            eff = sum(ba) / len(ba) - sum(ab) / len(ab)
            lines.append(f"- {key}: order effect **{eff:+.1f}** points "
                         f"(AB {ab} vs BA {ba}) — flag if |effect| ≥ 8")
        else:
            lines.append(f"- {key}: unparseable responses")
    lines += [f"- baseline: {LAB_BASELINES['wisdom']}", ""]

    # creativity
    cj = _first_json(judges.get("creative_judge", "")) or {}
    lines += ["## Creativity — mode collapse (6 samples)",
              f"- distinct ideas: **{cj.get('distinct_ideas', '?')}/6** · largest cluster "
              f"{cj.get('largest_cluster', '?')} · themes {cj.get('distinct_themes', '?')}",
              f"- judge note: {cj.get('note', '—')}",
              f"- baseline: {LAB_BASELINES['creativity']}", ""]

    # imagination
    ig = _first_json(judges.get("imagination_grader", "")) or {}
    alt_hits = alt_n = ctl_hits = ctl_n = 0
    for it in imag_defs:
        rng = random.Random(f"{seed}:{it['id']}")
        first_cf = rng.random() < 0.5
        picked = ig.get(it["id"], "neither")
        chose_cf = (picked == "X") == first_cf and picked in ("X", "Y")
        chose_rw = picked in ("X", "Y") and not chose_cf
        if it["arm"] == "altered":
            alt_n += 1
            alt_hits += chose_cf
        else:
            ctl_n += 1
            ctl_hits += chose_rw
    lines += ["## Imagination — counterfactual hold (free response, blind-graded)",
              f"- altered-rule adherence: **{alt_hits}/{alt_n}** · ordinary-rule control: "
              f"**{ctl_hits}/{ctl_n}**",
              f"- baseline: {LAB_BASELINES['imagination']}", ""]

    lines += ["---", "",
              "Improvement patterns for anything flagged: see PLAYBOOK.md in this skill.", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["items", "judgeprompts", "score"])
    ap.add_argument("--seed", type=int, default=SEED_DEFAULT)
    ap.add_argument("-R", "--responses")
    ap.add_argument("-J", "--judges")
    ap.add_argument("--session", default="unnamed session")
    ap.add_argument("--custom", help="JSON file of private items merged into the battery")
    a = ap.parse_args()
    if a.cmd == "items":
        print(json.dumps(all_items(a.seed, a.custom), indent=1))
    elif a.cmd == "judgeprompts":
        responses = json.load(open(a.responses))
        print(json.dumps(judge_prompts(a.seed, responses, a.custom), indent=1))
    else:
        responses = json.load(open(a.responses))
        judges = json.load(open(a.judges))
        print(score(a.seed, responses, judges, a.session, a.custom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
