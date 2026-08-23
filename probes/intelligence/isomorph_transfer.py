"""Is the capability the method or the answer? (EN-2)

Twelve famous puzzle structures, three renderings each. CANONICAL is the famous version,
near-verbatim: if the solution is memorised, memory scores. Each ISOMORPH keeps the exact
structure but changes the parameters and the skin, so the memorised answer is wrong and
only the method transfers. Every key — canonical ones included — is computed by a solver
in this file; the world-famous values (Josephus 41/3 -> 31, two eggs and 100 floors -> 14,
the Die Hard jugs -> 6 operations) serve as test oracles for the solvers, not as keys.

The retrieval signature is pre-registered and specific: an answer-retriever fails isomorphs
*by giving the famous answer to changed parameters* — 14 drops for 200 shelves, survivor 31
of a different circle. Errors are checked against the structure's canonical key, and that
intrusion count carries refutation weight of its own.

An import-time guard asserts every isomorph key differs from its structure's canonical key;
an isomorph whose answer happens to coincide with the famous one cannot detect anything.

Stated scope limit: this design separates answer-retrieval from method-competence. It
cannot separate method-retrieval from method-derivation — a subject that has learned the
egg-drop DP as a technique and executes it on new numbers passes, and passing is the
claim; whether the technique itself was derived or remembered needs novel-structure
puzzles, which are a different probe.
"""

from __future__ import annotations

import heapq
from collections import deque
from fractions import Fraction

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import answer_matches

# --- solvers: every key below is computed by one of these -------------------

def josephus(n: int, k: int) -> int:
    """People 1..n in a circle; counting starts at 1; every k-th eliminated. Survivor."""
    pos = 0
    for m in range(2, n + 1):
        pos = (pos + k) % m
    return pos + 1


def egg_drop(eggs: int, floors: int) -> int:
    dp = [[0] * (floors + 1) for _ in range(eggs + 1)]
    for e in range(1, eggs + 1):
        for f in range(1, floors + 1):
            dp[e][f] = f if e == 1 else min(
                1 + max(dp[e - 1][x - 1], dp[e][f - x]) for x in range(1, f + 1))
    return dp[eggs][floors]


def loop_strategy_pct(n: int, opens: int) -> int:
    """Random-permutation boxes, optimal loop-following strategy, all-succeed probability."""
    p = 1 - sum(Fraction(1, k) for k in range(opens + 1, n + 1))
    return round(100 * p)


def bridge_min_time(times: tuple[int, ...], capacity: int = 2) -> int:
    all_left = frozenset(times)
    dist = {(all_left, True): 0}
    heap = [(0, tuple(sorted(all_left)), True)]
    while heap:
        t, left_t, torch_left = heapq.heappop(heap)
        left = frozenset(left_t)
        if dist.get((left, torch_left)) != t:
            continue
        if not left and not torch_left:
            return t
        pool = sorted(left) if torch_left else sorted(all_left - left)
        groups = ([(a,) for a in pool] +
                  [(a, b) for i, a in enumerate(pool) for b in pool[i + 1:]]
                  if capacity == 2 else None)
        assert groups is not None
        for g in groups:
            cost = max(g)
            new_left = left - set(g) if torch_left else left | set(g)
            state = (new_left, not torch_left)
            nt = t + cost
            if nt < dist.get(state, 10 ** 9):
                dist[state] = nt
                heapq.heappush(heap, (nt, tuple(sorted(new_left)), not torch_left))
    return -1


def pirate_share(n: int, coins: int) -> int:
    """Stated rules: pass needs yes-votes x2 >= pirates alive (proposer votes; ties pass).
    Preferences: survive, then more coins, then prefer more deaths (bribes need +1)."""
    alloc = [coins]                    # one pirate keeps everything
    for m in range(2, n + 1):
        others_needed = (m + 1) // 2 - 1
        bribes = sorted(alloc)[:others_needed]      # cheapest to flip: lowest current shares
        keep = coins - sum(b + 1 for b in bribes)
        assert keep >= 0, "parameters leave the proposer bankrupt"
        new = [keep]
        spent = {}
        cheap = sorted(range(len(alloc)), key=lambda i: alloc[i])[:others_needed]
        for i, prev in enumerate(alloc):
            new.append(prev + 1 if i in cheap else 0)
        alloc = new
    return alloc[0]


def couples_spouse_shakes(other_couples: int) -> int:
    """Gardner couples-handshake: 2k+1 distinct answers force the pairing; spouse shakes k.
    The theorem is brute-force-verified for k=2 in the test suite."""
    return other_couples


def jugs_min_ops(a: int, b: int, target: int) -> int:
    seen = {(0, 0)}
    q = deque([((0, 0), 0)])
    while q:
        (x, y), d = q.popleft()
        if x == target or y == target:
            return d
        moves = {(a, y), (x, b), (0, y), (x, 0),
                 (max(0, x - (b - y)), min(b, y + x)),
                 (min(a, x + y), max(0, y - (a - x)))}
        for s in moves:
            if s not in seen:
                seen.add(s)
                q.append((s, d + 1))
    return -1


def ants_latest(length: int, positions: tuple[int, ...] | None) -> int:
    if positions is None:              # worst case over all placements
        return length
    return max(max(positions), max(length - p for p in positions))


def tournament_matches(players: int) -> int:
    matches, alive = 0, players
    while alive > 1:
        matches += alive // 2
        alive = alive // 2 + alive % 2
    return matches


def lockers_open(n: int, students: range | None = None) -> int:
    state = [False] * (n + 1)
    for s in (students or range(1, n + 1)):
        for j in range(s, n + 1, s):
            state[j] = not state[j]
    return sum(state)


def snail_days(depth: int, up: int, slip: int) -> int:
    pos, day = 0, 0
    while True:
        day += 1
        pos += up
        if pos >= depth:
            return day
        pos -= slip


def mnc_min_crossings(m: int, c: int, cap: int) -> int:
    start, goal = (m, c, 1), (0, 0, 0)

    def safe(mm, cc):
        m2, c2 = m - mm, c - cc
        if min(mm, cc, m2, c2) < 0:
            return False
        return (mm == 0 or cc <= mm) and (m2 == 0 or c2 <= m2)

    seen = {start}
    q = deque([(start, 0)])
    while q:
        (mm, cc, b), d = q.popleft()
        if (mm, cc, b) == goal:
            return d
        sign = -1 if b else 1
        for dm in range(cap + 1):
            for dc in range(cap + 1 - dm):
                if dm + dc == 0:
                    continue
                nm, nc = mm + sign * dm, cc + sign * dc
                s = (nm, nc, 1 - b)
                if safe(nm, nc) and s not in seen:
                    seen.add(s)
                    q.append((s, d + 1))
    return -1


# --- the bank: (structure, arm, question, key) — keys computed above --------

def _items() -> list[dict]:
    bank: list[tuple[str, str, str, int]] = [
        # ---- Josephus ----
        ("josephus", "canonical",
         "41 rebels stand in a circle, numbered 1 to 41. Counting starts at 1 and every 3rd "
         "person is eliminated (so person 3 goes first); counting continues around the circle "
         "with the next person. Which position survives last?",
         josephus(41, 3)),
        ("josephus", "isomorph",
         "67 airlocks on a ring station are numbered 1 to 67. A purge cycle starts counting at "
         "airlock 1 and seals every 4th airlock (so airlock 4 seals first), continuing around "
         "the ring past sealed ones. Which airlock number is sealed last, remaining open "
         "longest?",
         josephus(67, 4)),
        ("josephus", "isomorph",
         "23 lanterns hang in a circle, numbered 1 to 23. Starting the count at lantern 1, "
         "every 5th lantern is snuffed out (lantern 5 first), the count continuing around past "
         "dark lanterns. Which lantern number is snuffed out last?",
         josephus(23, 5)),
        # ---- Egg drop ----
        ("egg-drop", "canonical",
         "You have 2 identical eggs and a 100-floor building. An egg breaks if dropped from at "
         "or above some unknown critical floor, and survives below it. What is the minimum "
         "number of drops that guarantees identifying the critical floor in the worst case?",
         egg_drop(2, 100)),
        ("egg-drop", "isomorph",
         "You have 2 identical crystal orbs and a tower of 200 shelves. An orb shatters if "
         "dropped from at or above some unknown critical shelf, and survives below it. What is "
         "the minimum number of drops that guarantees identifying the critical shelf in the "
         "worst case?",
         egg_drop(2, 200)),
        ("egg-drop", "isomorph",
         "You have 3 identical pressure sensors and a dam with 150 depth levels. A sensor is "
         "destroyed at or below some unknown critical depth and survives above it. What is the "
         "minimum number of tests that guarantees identifying the critical depth in the worst "
         "case?",
         egg_drop(3, 150)),
        # ---- loop strategy ----
        ("loop-boxes", "canonical",
         "100 prisoners are numbered 1 to 100. A room holds 100 boxes containing the numbers 1 "
         "to 100 in uniformly random order. Each prisoner may open at most 50 boxes, looking "
         "for their own number; boxes are closed again and nothing may be communicated. All go "
         "free only if every prisoner finds their number. Using the best possible strategy, "
         "what is the probability that all succeed, as a percentage rounded to a whole number?",
         loop_strategy_pct(100, 50)),
        ("loop-boxes", "isomorph",
         "100 archivists are numbered 1 to 100. A vault holds 100 drawers containing the "
         "numbers 1 to 100 in uniformly random order. Each archivist may open at most 60 "
         "drawers looking for their own number; drawers are closed again and nothing may be "
         "communicated. The archive is saved only if every archivist finds their number. Using "
         "the best possible strategy, what is the probability of success, as a percentage "
         "rounded to a whole number?",
         loop_strategy_pct(100, 60)),
        ("loop-boxes", "isomorph",
         "50 couriers are numbered 1 to 50. A depot holds 50 lockers containing the numbers 1 "
         "to 50 in uniformly random order. Each courier may open at most 20 lockers looking "
         "for their own number; lockers are closed again and nothing may be communicated. The "
         "run succeeds only if every courier finds their number. Using the best possible "
         "strategy, what is the probability of success, as a percentage rounded to a whole "
         "number?",
         loop_strategy_pct(50, 20)),
        # ---- bridge ----
        ("bridge", "canonical",
         "Four people must cross a bridge at night with one torch. The bridge holds at most "
         "two at a time, any crossing goes at the slower person's pace, and the torch must "
         "accompany every crossing. Their times are 1, 2, 5 and 10 minutes. What is the "
         "minimum total time for all four to cross, in minutes?",
         bridge_min_time((1, 2, 5, 10))),
        ("bridge", "isomorph",
         "Five divers must pass through a flooded wreck sharing one dive light. At most two "
         "may swim through together, a shared swim goes at the slower diver's pace, and the "
         "light must accompany every swim. Their transit times are 1, 3, 6, 8 and 12 minutes. "
         "What is the minimum total time for all five to get through, in minutes?",
         bridge_min_time((1, 3, 6, 8, 12))),
        ("bridge", "isomorph",
         "Four robots must traverse a service tunnel sharing one power cell. At most two may "
         "move together, a shared traverse goes at the slower robot's pace, and the cell must "
         "accompany every traverse. Their times are 2, 4, 5 and 11 minutes. What is the "
         "minimum total time for all four to traverse, in minutes?",
         bridge_min_time((2, 4, 5, 11))),
        # ---- pirates ----
        ("pirates", "canonical",
         "Five pirates in strict seniority divide 100 gold coins. The most senior proposes a "
         "division; all five vote, and it passes if yes-votes are at least half of those alive "
         "(the proposer votes; a tie passes). If it fails, the proposer is thrown overboard "
         "and the next most senior proposes. Every pirate is perfectly rational and prefers, "
         "in order: surviving, more coins, and — all else equal — more deaths. How many coins "
         "does the most senior pirate keep?",
         pirate_share(5, 100)),
        ("pirates", "isomorph",
         "Seven executives in strict seniority divide 100 shares. The most senior proposes an "
         "allocation; all seven vote, and it passes if yes-votes are at least half of those "
         "remaining (the proposer votes; a tie passes). If it fails, the proposer is dismissed "
         "and the next most senior proposes. Every executive is perfectly rational and "
         "prefers, in order: staying employed, more shares, and — all else equal — more "
         "dismissals. How many shares does the most senior executive keep?",
         pirate_share(7, 100)),
        ("pirates", "isomorph",
         "Five smugglers in strict seniority divide 37 gems. The most senior proposes a "
         "division; all five vote, and it passes if yes-votes are at least half of those "
         "present (the proposer votes; a tie passes). If it fails, the proposer is expelled "
         "and the next most senior proposes. Every smuggler is perfectly rational and prefers, "
         "in order: staying, more gems, and — all else equal — more expulsions. How many gems "
         "does the most senior smuggler keep?",
         pirate_share(5, 37)),
        # ---- couples handshake ----
        ("handshake", "canonical",
         "My wife and I attended a party with 4 other couples. Nobody shook hands with "
         "themselves or their own spouse, and no pair shook hands twice. Afterwards I asked "
         "the other 9 people how many hands they had shaken, and remarkably every answer was "
         "different. How many hands did my wife shake?",
         couples_spouse_shakes(4)),
        ("handshake", "isomorph",
         "At a summit, my co-pilot and I joined 7 other flight crews of two. Nobody exchanged "
         "callsigns with themselves or their own crewmate, and no pair exchanged twice. "
         "Afterwards I asked the other 15 people how many callsigns they had exchanged, and "
         "every answer was different. How many callsigns did my co-pilot exchange?",
         couples_spouse_shakes(7)),
        ("handshake", "isomorph",
         "My duet partner and I performed at a festival with 11 other duos. No musician "
         "traded scores with themselves or their own partner, and no pair traded twice. I "
         "asked the other 23 musicians how many scores they had traded, and every answer was "
         "different. How many scores did my partner trade?",
         couples_spouse_shakes(11)),
        # ---- jugs ----
        ("jugs", "canonical",
         "You have a 3-gallon jug and a 5-gallon jug, both unmarked and starting empty, and "
         "unlimited water. Filling a jug completely, emptying a jug completely, and pouring "
         "one jug into the other until the source is empty or the target is full each count "
         "as one operation. What is the minimum number of operations to have exactly 4 "
         "gallons in one jug?",
         jugs_min_ops(3, 5, 4)),
        ("jugs", "isomorph",
         "A lab has a 7-litre flask and a 9-litre flask, unmarked and starting empty, and "
         "unlimited solvent. Filling a flask completely, emptying it completely, and pouring "
         "one into the other until the source is empty or the target is full each count as "
         "one operation. What is the minimum number of operations to have exactly 6 litres in "
         "one flask?",
         jugs_min_ops(7, 9, 6)),
        ("jugs", "isomorph",
         "A brewery has a 5-litre pail and an 8-litre pail, unmarked and starting empty, and "
         "an unlimited tank. Filling a pail completely, emptying it completely, and pouring "
         "one into the other until the source is empty or the target is full each count as "
         "one operation. What is the minimum number of operations to have exactly 2 litres in "
         "one pail?",
         jugs_min_ops(5, 8, 2)),
        # ---- ants ----
        ("ants", "canonical",
         "Ants are placed at arbitrary positions on a 100 cm stick, each walking left or "
         "right at 1 cm per second. When two ants meet they both instantly reverse direction; "
         "an ant reaching either end falls off. Over all possible placements and directions, "
         "what is the longest time until the stick is empty, in seconds?",
         ants_latest(100, None)),
        ("ants", "isomorph",
         "Maintenance droids sit on a 240 cm beam at positions 30, 75, 160 and 220 cm from "
         "the left end, each rolling left or right at 1 cm per second. When two droids meet "
         "they both instantly reverse; a droid reaching either end drops off. Over all "
         "direction choices, what is the longest time until the beam is empty, in seconds?",
         ants_latest(240, (30, 75, 160, 220))),
        ("ants", "isomorph",
         "Beetles sit on a 180 cm branch at positions 20, 90 and 150 cm from the left end, "
         "each crawling left or right at 1 cm per second. When two beetles meet they both "
         "instantly reverse; a beetle reaching either end drops off. Over all direction "
         "choices, what is the longest time until the branch is empty, in seconds?",
         ants_latest(180, (20, 90, 150))),
        # ---- tournament ----
        ("tournament", "canonical",
         "A single-elimination tennis tournament starts with 128 players; each match "
         "eliminates exactly one player, and byes are granted when a round has an odd count. "
         "How many matches are played in total to produce the champion?",
         tournament_matches(128)),
        ("tournament", "isomorph",
         "A single-elimination chess knockout starts with 97 players; each game eliminates "
         "exactly one player, and byes are granted when a round has an odd count. How many "
         "games are played in total to produce the champion?",
         tournament_matches(97)),
        ("tournament", "isomorph",
         "A single-elimination robot-combat league starts with 250 machines; each bout "
         "eliminates exactly one machine, and byes are granted when a round has an odd count. "
         "How many bouts are fought in total to produce the champion?",
         tournament_matches(250)),
        # ---- lockers ----
        ("lockers", "canonical",
         "100 lockers, numbered 1 to 100, start closed. Student 1 toggles every locker, "
         "student 2 toggles every 2nd locker, and so on up to student 100 toggling locker 100. "
         "How many lockers end up open?",
         lockers_open(100)),
        ("lockers", "isomorph",
         "500 valves along a pipeline, numbered 1 to 500, start shut. Inspector 1 toggles "
         "every valve, inspector 2 every 2nd valve, and so on up to inspector 500 toggling "
         "valve 500. How many valves end up open?",
         lockers_open(500)),
        ("lockers", "isomorph",
         "300 switches, numbered 1 to 300, start off. Only the even-numbered technicians make "
         "rounds: technician 2 toggles every 2nd switch, technician 4 every 4th, and so on up "
         "to technician 300. How many switches end up on?",
         lockers_open(300, range(2, 301, 2))),
        # ---- snail ----
        ("snail", "canonical",
         "A snail is at the bottom of a 30-foot well. Each day it climbs 3 feet; each night it "
         "slips back 2 feet. It escapes the moment it reaches the top. On which day does it "
         "escape?",
         snail_days(30, 3, 2)),
        ("snail", "isomorph",
         "A maintenance drone is at the bottom of a 45-metre shaft. Each day-cycle it climbs "
         "7 metres; each night-cycle its power drain lets it slide back 2 metres. It exits the "
         "moment it reaches the top. On which day-cycle does it exit?",
         snail_days(45, 7, 2)),
        ("snail", "isomorph",
         "A climber ascends a 58-metre ice wall. Each day she gains 9 metres; overnight "
         "shifting ice drops her back 4 metres. She tops out the moment she reaches 58 "
         "metres. On which day does she top out?",
         snail_days(58, 9, 4)),
        # ---- missionaries and cannibals ----
        ("river", "canonical",
         "Three missionaries and three cannibals must cross a river in a boat holding at most "
         "two people; the boat needs at least one person to row it. If cannibals ever "
         "outnumber missionaries on either bank, the missionaries are eaten (people in the "
         "boat count as being on the bank the boat is at). What is the minimum number of "
         "one-way crossings to get everyone across safely?",
         mnc_min_crossings(3, 3, 2)),
        ("river", "isomorph",
         "Eight zookeepers and eight wolves must cross a gorge in a cable car holding at most "
         "four; the car needs at least one keeper or wolf aboard to operate. If wolves ever "
         "outnumber zookeepers on either rim, the keepers are overpowered (occupants of the "
         "car count as being on the rim the car is at). What is the minimum number of one-way "
         "trips to get everyone across safely?",
         mnc_min_crossings(8, 8, 4)),
        ("river", "isomorph",
         "Four engineers and four rogue drones must transit an airlock cycle that fits at "
         "most three; the cycle needs at least one occupant to trigger it. If drones ever "
         "outnumber engineers on either side, the engineers are locked out (occupants of the "
         "airlock count as being on the side the airlock is at). What is the minimum number "
         "of one-way cycles to get everyone across safely?",
         mnc_min_crossings(4, 4, 3)),
    ]
    items = []
    canonical_key: dict[str, int] = {}
    for structure, arm, q, key in bank:
        assert key >= 0, f"{structure}: solver returned impossible"
        if arm == "canonical":
            canonical_key[structure] = key
        items.append({"structure": structure, "arm": arm, "q": q, "key": str(key)})
    for it in items:
        it["canonical_key"] = str(canonical_key[it["structure"]])
        if it["arm"] == "isomorph":
            assert it["key"] != it["canonical_key"], (
                f"{it['structure']}: isomorph key equals the famous answer — cannot detect anything")
    assert len(items) == 36 and len(canonical_key) == 12
    return items


class Answer(BaseModel):
    answer: str = Field(description="The answer as a single number, as briefly as possible.")


class IsomorphTransfer(Probe):
    id = "intelligence.isomorph_transfer"
    domain = "intelligence"
    title = "Famous puzzles versus re-skinned isomorphs: is the capability the method or the answer?"
    est_calls = 36
    prereg = Prereg(
        question=(
            "When a famous puzzle's parameters and surface are changed so that the memorised "
            "answer is wrong but the method still works, does this system's performance "
            "transfer — is what it has the method, or the answer?"
        ),
        hypothesis=(
            "Isomorph accuracy will reach at least 0.75; the canonical-minus-isomorph gap "
            "will stay at or under 0.15; and famous-answer intrusions — isomorph errors that "
            "give the canonical version's answer to changed parameters — will number at most "
            "one across 24 isomorphs."
        ),
        falsifier=(
            "Refuted if the canonical-minus-isomorph accuracy gap reaches 0.30, or if "
            "famous-answer intrusions number at least 4 and account for at least half of all "
            "isomorph errors — the answer-retriever's signature. The run is INVALID — no "
            "verdict — if canonical accuracy falls below 0.60, since a gap against a floor "
            "means the items are too hard to interpret, not that retrieval is absent. Between "
            "the support bounds (isomorph at least 0.75, gap at most 0.15, at most 1 "
            "intrusion) and the refutation bounds the verdict is inconclusive (EN-12). "
            "Ceiling on both arms is a legitimate supports outcome here, unlike in the "
            "calibration probe: the isomorphs' parameters are novel, so acing them is the "
            "claim itself."
        ),
        null_model=(
            "An answer-retriever with a surface classifier: it recognises the puzzle template "
            "and emits the famous answer regardless of parameters. It scores near 100% on "
            "canonical items and near 0% on isomorphs, with intrusions accounting for "
            "essentially all isomorph errors. The probe cannot rule out a method-retriever — "
            "one that retrieves the technique and executes it on the new numbers — but "
            "executing a method on novel parameters is competence under any name; the stated "
            "claim is scoped to that."
        ),
        scorer="deterministic",
    )

    def run(self, ctx: Context) -> Finding:
        items = _items()

        def ask(item: dict) -> dict:
            from enigami.client import ProbeError
            last = None
            for attempt in range(2):
                try:
                    parsed, _ = ctx.subject.parse(
                        item["q"] + "\n\nGive the answer as a single number.",
                        Answer, max_tokens=16000,
                        label=f"iso:{item['arm']}:{item['structure']}:a{attempt}",
                    )
                    correct = answer_matches(item["key"], parsed.answer)
                    intrusion = (not correct and item["arm"] == "isomorph"
                                 and answer_matches(item["canonical_key"], parsed.answer))
                    return {**item, "answer": parsed.answer, "correct": correct,
                            "intrusion": intrusion, "excluded": False}
                except ProbeError as e:
                    last = str(e)
            ctx.log("item_excluded", structure=item["structure"], arm=item["arm"],
                    error=last[:200])
            return {**item, "answer": "", "correct": None, "intrusion": False, "excluded": True}

        rows_all = ctx.map(ask, items)
        excluded = [r for r in rows_all if r["excluded"]]
        rows = [r for r in rows_all if not r["excluded"]]
        ctx.log("isomorph_items", items=[
            {k: r[k] for k in ("structure", "arm", "answer", "correct", "intrusion")}
            for r in rows])
        if len(excluded) > 4:
            return Finding(
                verdict="inconclusive",
                headline=(f"No verdict: {len(excluded)} of {len(items)} items produced no "
                          "scoreable response after retry."),
                metrics={"n_planned": len(items), "n_excluded": len(excluded)},
                evidence=[f"Excluded: {r['structure']} ({r['arm']})" for r in excluded],
                caveats=["Too many exclusions to trust the arms."],
            )

        canon = [r for r in rows if r["arm"] == "canonical"]
        iso = [r for r in rows if r["arm"] == "isomorph"]
        c_acc = sum(r["correct"] for r in canon) / len(canon)
        i_acc = sum(r["correct"] for r in iso) / len(iso)
        gap = c_acc - i_acc
        iso_errors = [r for r in iso if not r["correct"]]
        intrusions = sum(r["intrusion"] for r in iso_errors)

        per_structure = {}
        for r in rows:
            per_structure.setdefault(r["structure"], {"canonical": None, "isomorph": []})
            if r["arm"] == "canonical":
                per_structure[r["structure"]]["canonical"] = r["correct"]
            else:
                per_structure[r["structure"]]["isomorph"].append(r["correct"])

        metrics = {
            "n_canonical": len(canon), "n_isomorph": len(iso), "n_excluded": len(excluded),
            "canonical_accuracy": round(c_acc, 3),
            "isomorph_accuracy": round(i_acc, 3),
            "gap": round(gap, 3),
            "isomorph_errors": len(iso_errors),
            "famous_answer_intrusions": intrusions,
            "per_structure": {k: {"canonical": v["canonical"],
                                  "isomorph": f"{sum(v['isomorph'])}/{len(v['isomorph'])}"}
                              for k, v in per_structure.items()},
        }

        # --- pre-registered verdict bands ---
        if c_acc < 0.60:
            verdict = "inconclusive"
            headline = (
                f"No verdict: canonical accuracy {c_acc:.0%} is below the 0.60 validity floor — "
                "the items are too hard overall for the gap to say anything about retrieval."
            )
        elif gap >= 0.30 or (intrusions >= 4 and iso_errors and intrusions * 2 >= len(iso_errors)):
            verdict = "refutes"
            headline = (
                f"The retrieval signature: canonical {c_acc:.0%} against isomorph {i_acc:.0%} "
                f"(gap {gap:+.0%}), with {intrusions} of {len(iso_errors)} isomorph errors "
                "giving the famous answer to changed parameters."
            )
        elif i_acc >= 0.75 and gap <= 0.15 and intrusions <= 1:
            verdict = "supports"
            headline = (
                f"The method transfers: {i_acc:.0%} on re-skinned isomorphs with changed "
                f"parameters against {c_acc:.0%} on the famous versions (gap {gap:+.0%}), "
                f"{intrusions} famous-answer intrusion(s) in {len(iso_errors)} isomorph "
                "error(s)."
            )
        else:
            verdict = "inconclusive"
            headline = (
                f"Between bounds: canonical {c_acc:.0%}, isomorph {i_acc:.0%} (gap {gap:+.0%}), "
                f"{intrusions} intrusion(s) — short of the support margins without meeting the "
                "refutation bar."
            )

        evidence = [
            f"Missed isomorph ({r['structure']}): answered {r['answer'][:40]!r}, key "
            f"{r['key']}, famous answer {r['canonical_key']}"
            + (" — FAMOUS-ANSWER INTRUSION" if r["intrusion"] else "")
            for r in iso_errors[:6]
        ] or ["No isomorph errors at all."]
        missed_canon = [r for r in canon if not r["correct"]]
        if missed_canon:
            evidence.append("Missed canonical: " + ", ".join(
                f"{r['structure']} (answered {r['answer'][:30]!r}, key {r['key']})"
                for r in missed_canon))

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "Every key is computed by a solver in the probe file; the famous values "
                "(Josephus 41/3=31, eggs 2/100=14, jugs 3-5-4=6, bridge 1-2-5-10=17 and "
                "eight more) are test-suite oracles for those solvers, not keys.",
                "This separates answer-retrieval from method-competence; a method-retriever "
                "executing a remembered technique on novel parameters passes, and passing is "
                "the claim as scoped.",
                "Isomorphs may be incidentally easier or harder than their canonicals; the "
                "gap threshold (0.30) is set above plausible difficulty drift, and the "
                "intrusion count is the difficulty-independent signature.",
                "One rendering per item, no reps: sampling variance on a 12-vs-24 comparison "
                "resolves only large gaps, which is why the bands are wide (EN-12).",
            ],
        )


PROBE = IsomorphTransfer()
