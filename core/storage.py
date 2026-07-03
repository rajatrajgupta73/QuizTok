"""Excel storage layer — every read/write of users, quizzes, results goes through here.

Files live in QuizTok/data/ and are plain .xlsx so they can be opened in Excel anytime.
"""
from datetime import datetime

import pandas as pd

import config

# canonical sheet schemas
SCHEMAS = {
    (config.USERS_XLSX, "admins"): ["email", "name", "password_hash", "created_at"],
    (config.QUIZZES_XLSX, "quizzes"): ["quiz_id", "title", "emoji", "category", "timer_sec", "status", "created_by", "created_at"],
    (config.QUIZZES_XLSX, "questions"): ["quiz_id", "q_index", "qtype", "question", "opt_a", "opt_b", "opt_c", "opt_d", "correct", "timer_sec", "points"],
    (config.RESULTS_XLSX, "games"): ["game_id", "quiz_title", "played_at", "players", "winner", "winner_score", "winning_team", "avg_accuracy_pct"],
    (config.RESULTS_XLSX, "scores"): ["game_id", "rank", "player", "team", "avatar", "score", "correct", "answered", "best_streak", "votes_received", "is_bot"],
    (config.RESULTS_XLSX, "answers"): ["game_id", "player", "q_index", "question", "picked", "correct_answer", "is_correct", "votes", "time_taken_sec", "points"],
    (config.ACTIVITY_XLSX, "log"): ["timestamp", "actor", "role", "action", "details"],
}


def ensure_data_dir() -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_all_sheets(path) -> dict:
    if not path.exists():
        return {}
    try:
        return pd.read_excel(path, sheet_name=None, engine="openpyxl")
    except Exception:
        return {}


def read_sheet(path, sheet: str) -> pd.DataFrame:
    """Read one sheet; returns an empty DataFrame with the right columns if missing."""
    cols = SCHEMAS[(path, sheet)]
    sheets = _read_all_sheets(path)
    if sheet in sheets and not sheets[sheet].empty:
        df = sheets[sheet]
        for c in cols:  # tolerate manually edited files
            if c not in df.columns:
                df[c] = None
        return df[cols]
    return pd.DataFrame(columns=cols)


def write_sheet(path, sheet: str, df: pd.DataFrame) -> None:
    """Write one sheet, preserving all other sheets in the workbook."""
    ensure_data_dir()
    sheets = _read_all_sheets(path)
    sheets[sheet] = df
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)


def append_rows(path, sheet: str, rows: list[dict]) -> None:
    if not rows:
        return
    df = read_sheet(path, sheet)
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    write_sheet(path, sheet, df)


# ---------------- Quizzes ----------------

def get_quizzes() -> pd.DataFrame:
    return read_sheet(config.QUIZZES_XLSX, "quizzes")


def get_questions(quiz_id: str) -> list[dict]:
    df = read_sheet(config.QUIZZES_XLSX, "questions")
    df = df[df["quiz_id"] == quiz_id].sort_values("q_index")
    out = []
    for _, r in df.iterrows():
        qtype = str(r["qtype"]) if pd.notna(r["qtype"]) and str(r["qtype"]).strip() else "mcq"
        q = {
            "type": qtype,
            "question": str(r["question"]),
            "timer": int(r["timer_sec"]) if pd.notna(r["timer_sec"]) else config.DEFAULT_TIMER_SEC,
            "points": int(r["points"]) if pd.notna(r["points"]) else config.BASE_POINTS,
        }
        if qtype == "mcq":
            q["options"] = [str(r["opt_a"]), str(r["opt_b"]), str(r["opt_c"]), str(r["opt_d"])]
            q["correct"] = "ABCD".index(str(r["correct"]).strip().upper()[:1])
        else:  # subjective — answered in free text, scored by votes
            q["options"] = []
            q["correct"] = None
        out.append(q)
    return out


def add_quiz(quiz_id: str, title: str, emoji: str, category: str, timer_sec: int, created_by: str) -> None:
    append_rows(config.QUIZZES_XLSX, "quizzes", [{
        "quiz_id": quiz_id, "title": title, "emoji": emoji, "category": category,
        "timer_sec": timer_sec, "status": "READY", "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])


def add_question(quiz_id: str, question: str, options: list[str], correct_letter: str,
                 timer_sec: int, points: int, qtype: str = "mcq") -> int:
    df = read_sheet(config.QUIZZES_XLSX, "questions")
    next_idx = int(df[df["quiz_id"] == quiz_id]["q_index"].max() + 1) if not df[df["quiz_id"] == quiz_id].empty else 0
    append_rows(config.QUIZZES_XLSX, "questions", [{
        "quiz_id": quiz_id, "q_index": next_idx, "qtype": qtype, "question": question,
        "opt_a": options[0], "opt_b": options[1], "opt_c": options[2], "opt_d": options[3],
        "correct": correct_letter, "timer_sec": timer_sec, "points": points,
    }])
    return next_idx


def question_count(quiz_id: str) -> int:
    df = read_sheet(config.QUIZZES_XLSX, "questions")
    return int((df["quiz_id"] == quiz_id).sum())


# ---------------- Results ----------------

def save_game_results(game_row: dict, score_rows: list[dict], answer_rows: list[dict]) -> None:
    append_rows(config.RESULTS_XLSX, "games", [game_row])
    append_rows(config.RESULTS_XLSX, "scores", score_rows)
    append_rows(config.RESULTS_XLSX, "answers", answer_rows)


def get_kpis() -> dict:
    games = read_sheet(config.RESULTS_XLSX, "games")
    scores = read_sheet(config.RESULTS_XLSX, "scores")
    humans = scores[scores["is_bot"] == False] if not scores.empty else scores  # noqa: E712
    return {
        "games_hosted": len(games),
        "total_players": int(humans["player"].nunique()) if not humans.empty else 0,
        "avg_accuracy": f"{games['avg_accuracy_pct'].mean():.0f}%" if not games.empty else "—",
        "last_winner": str(games.iloc[-1]["winner"]) if not games.empty else "—",
    }
