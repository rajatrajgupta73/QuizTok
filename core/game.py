"""Live game engine.

The single live game is stored in data/live_game.json so multiple browser tabs
(host + participants on the same machine or LAN) share one authoritative state.

State machine:
    LOBBY -> QUESTION -> REVEAL -> next QUESTION ... -> FINISHED         (MCQ)
    LOBBY -> QUESTION -> VOTING -> REVEAL -> next QUESTION ...          (subjective)

Scoring:
    MCQ:        base * (1 + time_left/timer) + streak bonus (50/level, capped)
    Subjective: VOTE_POINTS per vote received + VOTE_WINNER_BONUS for the top answer(s)

Teams are optional — players may join with a team name; the team leaderboard
aggregates member scores, and votes can effectively back a team via its players.
"""
import json
import os
import random
import time
import uuid
from datetime import datetime

import config
from core import storage, logger


# ---------------- persistence ----------------

def load() -> dict | None:
    for _ in range(3):  # tolerate a concurrent write
        try:
            if config.LIVE_GAME_JSON.exists():
                return json.loads(config.LIVE_GAME_JSON.read_text(encoding="utf-8"))
            return None
        except (json.JSONDecodeError, OSError):
            time.sleep(0.05)
    return None


def save(g: dict) -> None:
    """Atomic-ish write safe for concurrent sessions (host + participants on Windows).

    Each writer uses its own temp file, and os.replace is retried because Windows
    refuses to swap a file another process has open for a few milliseconds.
    A skipped save is harmless — every session re-ticks within a second.
    """
    storage.ensure_data_dir()
    tmp = config.LIVE_GAME_JSON.with_suffix(f".{os.getpid()}.{uuid.uuid4().hex[:6]}.tmp")
    tmp.write_text(json.dumps(g, ensure_ascii=False), encoding="utf-8")
    for attempt in range(6):
        try:
            os.replace(tmp, config.LIVE_GAME_JSON)
            return
        except PermissionError:
            time.sleep(0.03 * (attempt + 1))
    try:  # another session owned the file the whole time — drop this save
        tmp.unlink()
    except OSError:
        pass


def clear() -> None:
    if config.LIVE_GAME_JSON.exists():
        config.LIVE_GAME_JSON.unlink()


# ---------------- lifecycle ----------------

def create_game(quiz_id: str, host: str, with_bots: bool = True, bot_count: int = 6) -> dict:
    quizzes = storage.get_quizzes()
    row = quizzes[quizzes["quiz_id"] == quiz_id].iloc[0]
    questions = storage.get_questions(quiz_id)
    if not questions:
        raise ValueError("This quiz has no questions yet — add some in the Question Builder.")

    g = {
        "game_id": uuid.uuid4().hex[:10],
        "pin": "".join(random.choices("123456789", k=config.PIN_LENGTH)),
        "quiz_id": quiz_id,
        "quiz_title": f'{row["emoji"]} {row["title"]}',
        "host": host,
        "status": "LOBBY",
        "q_index": -1,
        "question_started": 0.0,
        "voting_started": 0.0,
        "questions": questions,
        "players": {},
        "bot_plan": {},
        "votes": {},          # voter -> target (current subjective question)
        "awards": {},
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if with_bots:
        bots = random.sample(config.BOT_ROSTER, k=min(bot_count, len(config.BOT_ROSTER)))
        for i, (name, avatar, skill) in enumerate(bots):
            team = config.BOT_TEAMS[i % len(config.BOT_TEAMS)]
            g["players"][name] = _new_player(avatar, is_bot=True, skill=skill, team=team)
    save(g)
    logger.log(host, "admin" if host != "__solo__" else "participant",
               "game_created", f'pin={g["pin"]} quiz={quiz_id} bots={with_bots}')
    return g


def _new_player(avatar: str, is_bot: bool = False, skill: float = 0.0, team: str = "") -> dict:
    return {"avatar": avatar, "is_bot": is_bot, "skill": skill, "team": team,
            "score": 0, "streak": 0, "best_streak": 0, "votes_received": 0, "answers": []}


def join(pin: str, nick: str, avatar: str, team: str = "") -> tuple[bool, str]:
    g = load()
    if not g:
        return False, "No live game right now — ask your host to start one (or play the solo demo)."
    if g["pin"] != pin.strip():
        return False, "Wrong PIN — check the host screen and try again."
    if g["status"] != "LOBBY":
        return False, "This game already started — wait for the next round!"
    nick = nick.strip()
    if nick in g["players"]:
        return False, f'"{nick}" is taken — pick another nickname.'
    g["players"][nick] = _new_player(avatar, team=team.strip())
    save(g)
    logger.log(nick, "participant", "joined_game", f'pin={pin} team={team or "-"}')
    return True, "ok"


def set_avatar(nick: str, avatar: str) -> None:
    g = load()
    if g and nick in g["players"]:
        g["players"][nick]["avatar"] = avatar
        save(g)


def start(actor: str) -> None:
    g = load()
    if g and g["status"] == "LOBBY":
        _begin_question(g, 0)
        save(g)
        logger.log(actor, "host", "game_started", f'pin={g["pin"]} players={len(g["players"])}')


def _begin_question(g: dict, idx: int) -> None:
    q = g["questions"][idx]
    g["status"] = "QUESTION"
    g["q_index"] = idx
    g["question_started"] = time.time()
    g["votes"] = {}
    g["bot_plan"] = {}
    for name, p in g["players"].items():
        if p["is_bot"]:
            plan = {"delay": round(random.uniform(2.0, max(3.0, q["timer"] * 0.75)), 1), "done": False}
            if q["type"] == "mcq":
                plan["will_correct"] = random.random() < p["skill"]
            else:
                plan["text"] = random.choice(config.BOT_SUBJECTIVE_ANSWERS)
            g["bot_plan"][name] = plan


# ---------------- helpers ----------------

def current_q(g: dict) -> dict:
    return g["questions"][g["q_index"]]


def time_left(g: dict) -> float:
    if g["status"] == "VOTING":
        return max(0.0, config.VOTING_TIMER_SEC - (time.time() - g["voting_started"]))
    return max(0.0, current_q(g)["timer"] - (time.time() - g["question_started"]))


def has_answered(g: dict, nick: str) -> bool:
    return any(a["q"] == g["q_index"] for a in g["players"][nick]["answers"])


def _answer_of(p: dict, q_idx: int) -> dict | None:
    return next((a for a in p["answers"] if a["q"] == q_idx), None)


# ---------------- answering: MCQ ----------------

def _score_mcq(g: dict, nick: str, choice: int | None, tl: float) -> dict:
    q = current_q(g)
    p = g["players"][nick]
    correct = choice is not None and choice == q["correct"]
    points = 0
    if correct:
        p["streak"] += 1
        p["best_streak"] = max(p["best_streak"], p["streak"])
        speed = 1 + tl / q["timer"]
        bonus = min(p["streak"], config.STREAK_BONUS_CAP) * config.STREAK_BONUS_PER_LEVEL
        points = round(q["points"] * speed) + bonus
        p["score"] += points
    else:
        p["streak"] = 0
    rec = {"q": g["q_index"], "choice": choice, "text": "", "correct": correct,
           "time_taken": round(q["timer"] - tl, 1), "points": points, "votes": 0}
    p["answers"].append(rec)
    return rec


def submit_answer(nick: str, choice: int) -> dict | None:
    """Human MCQ answer. Returns the answer record (with points) or None if rejected."""
    g = load()
    if not g or g["status"] != "QUESTION" or nick not in g["players"] or has_answered(g, nick):
        return None
    tl = time_left(g)
    if tl <= 0:
        return None
    rec = _score_mcq(g, nick, choice, tl)
    save(g)
    logger.log(nick, "participant", "answer_submitted",
               f'q={g["q_index"] + 1} correct={rec["correct"]} points={rec["points"]}')
    return rec


# ---------------- answering: subjective ----------------

def submit_text(nick: str, text: str) -> bool:
    g = load()
    if not g or g["status"] != "QUESTION" or nick not in g["players"] or has_answered(g, nick):
        return False
    text = text.strip()
    if not text:
        return False
    q = current_q(g)
    rec = {"q": g["q_index"], "choice": None, "text": text[:500], "correct": None,
           "time_taken": round(q["timer"] - time_left(g), 1), "points": 0, "votes": 0}
    g["players"][nick]["answers"].append(rec)
    save(g)
    logger.log(nick, "participant", "subjective_answer", f'q={g["q_index"] + 1}')
    return True


def current_answers(g: dict) -> list[dict]:
    """All submitted answers for the current subjective question (for the voting wall)."""
    out = []
    for name, p in g["players"].items():
        a = _answer_of(p, g["q_index"])
        if a and a["text"]:
            out.append({"name": name, "avatar": p["avatar"], "team": p["team"],
                        "text": a["text"], "votes": a["votes"]})
    return out


def submit_vote(voter: str, target: str) -> bool:
    """One vote per player per subjective question. Can't vote for yourself."""
    g = load()
    if not g or g["status"] != "VOTING" or voter == target:
        return False
    if voter in g["votes"] or target not in g["players"]:
        return False
    a = _answer_of(g["players"][target], g["q_index"])
    if not a:
        return False
    g["votes"][voter] = target
    a["votes"] += 1
    save(g)
    logger.log(voter, "participant", "vote_cast", f'for={target} q={g["q_index"] + 1}')
    return True


def has_voted(g: dict, nick: str) -> bool:
    return nick in g["votes"]


def _begin_voting(g: dict) -> None:
    g["status"] = "VOTING"
    g["voting_started"] = time.time()
    g["votes"] = {}
    # bots vote a bit later, for a random other player's answer
    g["bot_plan"] = {
        name: {"delay": round(random.uniform(3.0, config.VOTING_TIMER_SEC * 0.7), 1), "done": False}
        for name, p in g["players"].items() if p["is_bot"]
    }


def _finish_voting(g: dict) -> None:
    """Award vote points and the winner bonus, then reveal."""
    answers = current_answers(g)
    if answers:
        top = max(a["votes"] for a in answers)
        for a in answers:
            p = g["players"][a["name"]]
            rec = _answer_of(p, g["q_index"])
            pts = a["votes"] * config.VOTE_POINTS
            if top > 0 and a["votes"] == top:
                pts += config.VOTE_WINNER_BONUS
            rec["points"] = pts
            p["score"] += pts
            p["votes_received"] += a["votes"]
    g["status"] = "REVEAL"


# ---------------- tick: bots + auto transitions ----------------

def tick(g: dict) -> dict:
    """Advance bots and auto-transition phases. Call on every page refresh."""
    changed = False

    if g["status"] == "QUESTION":
        q = current_q(g)
        elapsed = time.time() - g["question_started"]
        for name, plan in g["bot_plan"].items():
            if not plan["done"] and elapsed >= plan["delay"]:
                if q["type"] == "mcq":
                    choice = q["correct"] if plan["will_correct"] else random.choice(
                        [i for i in range(4) if i != q["correct"]])
                    _score_mcq(g, name, choice, max(0.0, q["timer"] - plan["delay"]))
                else:
                    g["players"][name]["answers"].append(
                        {"q": g["q_index"], "choice": None, "text": plan["text"], "correct": None,
                         "time_taken": plan["delay"], "points": 0, "votes": 0})
                plan["done"] = True
                changed = True

        humans = [n for n, p in g["players"].items() if not p["is_bot"]]
        all_done = humans and all(has_answered(g, n) for n in humans)
        if time_left(g) <= 0 or all_done:
            if q["type"] == "mcq":
                _reveal_mcq(g)
            else:
                _materialize_bot_answers(g)
                _begin_voting(g)
            changed = True

    elif g["status"] == "VOTING":
        for name, plan in g["bot_plan"].items():
            if not plan["done"] and (time.time() - g["voting_started"]) >= plan["delay"]:
                targets = [a["name"] for a in current_answers(g) if a["name"] != name]
                if targets and name not in g["votes"]:
                    target = random.choice(targets)
                    a = _answer_of(g["players"][target], g["q_index"])
                    g["votes"][name] = target
                    a["votes"] += 1
                plan["done"] = True
                changed = True

        humans = [n for n, p in g["players"].items() if not p["is_bot"]]
        all_voted = humans and all(n in g["votes"] for n in humans)
        if time_left(g) <= 0 or all_voted:
            _finish_voting(g)
            changed = True

    if changed:
        save(g)
    return g


def _materialize_bot_answers(g: dict) -> None:
    """Any bot that hadn't answered yet answers at the buzzer (subjective)."""
    for name, plan in g["bot_plan"].items():
        if not plan["done"]:
            g["players"][name]["answers"].append(
                {"q": g["q_index"], "choice": None, "text": plan.get("text", "Great question!"),
                 "correct": None, "time_taken": current_q(g)["timer"], "points": 0, "votes": 0})
            plan["done"] = True


def _reveal_mcq(g: dict) -> None:
    q = current_q(g)
    for name, p in g["players"].items():
        if not any(a["q"] == g["q_index"] for a in p["answers"]):
            if p["is_bot"]:
                plan = g["bot_plan"].get(name, {"will_correct": False})
                choice = q["correct"] if plan.get("will_correct") else random.choice(
                    [i for i in range(4) if i != q["correct"]])
                _score_mcq(g, name, choice, 0.5)
            else:
                _score_mcq(g, name, None, 0.0)  # timed out
    g["status"] = "REVEAL"


def force_reveal(actor: str) -> None:
    """Host ends the answer window early."""
    g = load()
    if g and g["status"] == "QUESTION":
        if current_q(g)["type"] == "mcq":
            _reveal_mcq(g)
        else:
            _materialize_bot_answers(g)
            _begin_voting(g)
        save(g)
        logger.log(actor, "host", "force_reveal", f'q={g["q_index"] + 1}')


def force_end_voting(actor: str) -> None:
    g = load()
    if g and g["status"] == "VOTING":
        _finish_voting(g)
        save(g)
        logger.log(actor, "host", "force_end_voting", f'q={g["q_index"] + 1}')


def next_question(actor: str) -> None:
    g = load()
    if not g or g["status"] != "REVEAL":
        return
    if g["q_index"] + 1 < len(g["questions"]):
        _begin_question(g, g["q_index"] + 1)
        save(g)
    else:
        finish(actor)


# ---------------- leaderboards & awards ----------------

def leaderboard(g: dict) -> list[dict]:
    rows = [{"name": n, **p} for n, p in g["players"].items()]
    return sorted(rows, key=lambda r: -r["score"])


def team_leaderboard(g: dict) -> list[dict]:
    teams: dict[str, dict] = {}
    for n, p in g["players"].items():
        if not p["team"]:
            continue
        t = teams.setdefault(p["team"], {"team": p["team"], "score": 0, "members": [], "votes": 0})
        t["score"] += p["score"]
        t["votes"] += p["votes_received"]
        t["members"].append(f'{p["avatar"]} {n}')
    return sorted(teams.values(), key=lambda t: -t["score"])


def answer_distribution(g: dict) -> list[int]:
    counts = [0, 0, 0, 0]
    for p in g["players"].values():
        for a in p["answers"]:
            if a["q"] == g["q_index"] and a["choice"] is not None:
                counts[a["choice"]] += 1
    return counts


def compute_awards(g: dict) -> dict:
    stats = []
    for n, p in g["players"].items():
        answered = [a for a in p["answers"] if a["choice"] is not None or a["text"]]
        mcqs = [a for a in p["answers"] if a["correct"] is not None]
        correct = [a for a in mcqs if a["correct"]]
        stats.append({
            "name": n,
            "avg_time": sum(a["time_taken"] for a in answered) / len(answered) if answered else 99,
            "best_streak": p["best_streak"],
            "accuracy": len(correct) / len(mcqs) if mcqs else 0,
            "votes": p["votes_received"],
        })
    if not stats:
        return {}
    awards = {
        "⚡ Speed Demon": min(stats, key=lambda s: s["avg_time"])["name"],
        "🔥 Longest Streak": max(stats, key=lambda s: s["best_streak"])["name"],
        "🎯 Sharp Shooter": max(stats, key=lambda s: s["accuracy"])["name"],
    }
    if any(s["votes"] > 0 for s in stats):
        awards["🗳️ Crowd Favourite"] = max(stats, key=lambda s: s["votes"])["name"]
    return awards


def finish(actor: str) -> None:
    g = load()
    if not g or g["status"] == "FINISHED":
        return
    g["awards"] = compute_awards(g)
    g["status"] = "FINISHED"
    save(g)
    _persist_results(g)
    logger.log(actor, "host", "game_ended", f'pin={g["pin"]}')


def _persist_results(g: dict) -> None:
    board = leaderboard(g)
    teams = team_leaderboard(g)
    mcq_answers = [a for p in g["players"].values() for a in p["answers"] if a["correct"] is not None]
    total_correct = sum(1 for a in mcq_answers if a["correct"])

    game_row = {
        "game_id": g["game_id"], "quiz_title": g["quiz_title"],
        "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "players": len(g["players"]),
        "winner": board[0]["name"] if board else "—",
        "winner_score": board[0]["score"] if board else 0,
        "winning_team": teams[0]["team"] if teams else "—",
        "avg_accuracy_pct": round(100 * total_correct / max(1, len(mcq_answers)), 1),
    }
    score_rows, answer_rows = [], []
    for rank, r in enumerate(board, start=1):
        mcqs = [a for a in r["answers"] if a["correct"] is not None]
        score_rows.append({
            "game_id": g["game_id"], "rank": rank, "player": r["name"], "team": r["team"],
            "avatar": r["avatar"], "score": r["score"],
            "correct": sum(1 for a in mcqs if a["correct"]),
            "answered": sum(1 for a in r["answers"] if a["choice"] is not None or a["text"]),
            "best_streak": r["best_streak"], "votes_received": r["votes_received"],
            "is_bot": r["is_bot"],
        })
        for a in r["answers"]:
            q = g["questions"][a["q"]]
            if q["type"] == "mcq":
                picked = q["options"][a["choice"]] if a["choice"] is not None else "(no answer)"
                correct_answer = q["options"][q["correct"]]
            else:
                picked = a["text"] or "(no answer)"
                correct_answer = "(subjective — scored by votes)"
            answer_rows.append({
                "game_id": g["game_id"], "player": r["name"], "q_index": a["q"] + 1,
                "question": q["question"], "picked": picked, "correct_answer": correct_answer,
                "is_correct": a["correct"], "votes": a["votes"],
                "time_taken_sec": a["time_taken"], "points": a["points"],
            })
    try:
        storage.save_game_results(game_row, score_rows, answer_rows)
    except PermissionError:
        pass  # results.xlsx open in Excel — game still finishes


# ---------------- solo demo ----------------

def start_solo_demo(nick: str, avatar: str, team: str = "") -> None:
    quizzes = storage.get_quizzes()
    quiz_id = str(quizzes.iloc[0]["quiz_id"])
    g = create_game(quiz_id, host="__solo__", with_bots=True, bot_count=6)
    g["players"][nick] = _new_player(avatar, team=team)
    save(g)
    start(nick)
