"""Excel storage layer — every read/write of users, quizzes, results goes through here.

Files live in QuizTok/data/ and are plain .xlsx so they can be opened in Excel anytime.
Question media (image / audio / video) lives in data/media/ and is referenced from Excel.
"""
import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

import config

# canonical sheet schemas
SCHEMAS = {
    (config.USERS_XLSX, "admins"): ["email", "name", "password_hash", "created_at"],
    (config.QUIZZES_XLSX, "quizzes"): ["quiz_id", "title", "emoji", "category", "timer_sec", "status", "created_by", "created_at"],
    (config.QUIZZES_XLSX, "questions"): [
        "quiz_id", "q_index", "qtype", "question", "opt_a", "opt_b", "opt_c", "opt_d",
        "correct", "timer_sec", "points", "media_type", "media_file",
    ],
    (config.RESULTS_XLSX, "games"): ["game_id", "quiz_title", "played_at", "players", "winner", "winner_score", "winning_team", "avg_accuracy_pct"],
    (config.RESULTS_XLSX, "scores"): ["game_id", "rank", "player", "team", "avatar", "score", "correct", "answered", "best_streak", "votes_received", "is_bot"],
    (config.RESULTS_XLSX, "answers"): ["game_id", "player", "q_index", "question", "picked", "correct_answer", "is_correct", "votes", "time_taken_sec", "points"],
    (config.ACTIVITY_XLSX, "log"): ["timestamp", "actor", "role", "action", "details"],
    (config.TEAMS_XLSX, "teams"): ["name", "emoji", "color", "created_by", "created_at"],
    (config.DOMAIN_TREE_XLSX, "nodes"): ["node_id", "parent_id", "label", "emoji", "category", "sort_order", "node_type"],
    (config.DOMAIN_TREE_XLSX, "terms"): ["term_id", "node_id", "abbr", "expansion", "definition", "example", "related_qids"],
    (config.LEARNING_PROGRESS_XLSX, "progress"): ["player_key", "term_id", "status", "source", "updated_at"],
    (config.LEARNING_PROGRESS_XLSX, "achievements"): ["player_key", "achievement_id", "earned_at"],
    (config.FEEDBACK_XLSX, "feedback"): ["feedback_id", "player", "role", "category", "page", "message", "status", "created_at"],
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
        media_type = ""
        media_file = ""
        if "media_type" in r.index and pd.notna(r["media_type"]):
            media_type = str(r["media_type"]).strip().lower()
        if "media_file" in r.index and pd.notna(r["media_file"]):
            media_file = str(r["media_file"]).strip()
        if media_type and media_file:
            q["media_type"] = media_type
            q["media_file"] = media_file
        if qtype == "mcq":
            q["options"] = [str(r["opt_a"]), str(r["opt_b"]), str(r["opt_c"]), str(r["opt_d"])]
            q["correct"] = "ABCD".index(str(r["correct"]).strip().upper()[:1])
        else:  # subjective — answered in free text, scored by votes
            q["options"] = []
            q["correct"] = None
        out.append(q)
    return out


def media_type_for_ext(ext: str) -> str:
    ext = ext.lower()
    if ext in config.MEDIA_IMAGE_EXT:
        return "image"
    if ext in config.MEDIA_AUDIO_EXT:
        return "audio"
    if ext in config.MEDIA_VIDEO_EXT:
        return "video"
    return ""


def save_question_media(quiz_id: str, filename: str, data: bytes) -> tuple[str, str]:
    """Persist uploaded bytes under data/media/{quiz_id}/. Returns (media_type, relative_path)."""
    ext = Path(filename).suffix.lower()
    media_type = media_type_for_ext(ext)
    if not media_type:
        raise ValueError("Unsupported file type — use PNG/JPG/GIF/WebP, MP3/WAV/OGG, or MP4/WebM.")
    if len(data) > config.MEDIA_MAX_BYTES:
        raise ValueError(f"File too large — max {config.MEDIA_MAX_BYTES // (1024 * 1024)} MB.")

    safe = re.sub(r"[^\w.\-]+", "_", Path(filename).name).strip("._") or "upload"
    rel = f"{quiz_id}/{uuid.uuid4().hex[:8]}_{safe}"
    dest = config.MEDIA_DIR / rel
    ensure_data_dir()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return media_type, rel


def media_path(relative: str) -> Path | None:
    if not relative:
        return None
    path = (config.MEDIA_DIR / relative).resolve()
    try:
        path.relative_to(config.MEDIA_DIR.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def add_quiz(quiz_id: str, title: str, emoji: str, category: str, timer_sec: int, created_by: str) -> None:
    append_rows(config.QUIZZES_XLSX, "quizzes", [{
        "quiz_id": quiz_id, "title": title, "emoji": emoji, "category": category,
        "timer_sec": timer_sec, "status": "READY", "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])


def add_question(quiz_id: str, question: str, options: list[str], correct_letter: str,
                 timer_sec: int, points: int, qtype: str = "mcq",
                 media_type: str = "", media_file: str = "") -> int:
    df = read_sheet(config.QUIZZES_XLSX, "questions")
    next_idx = int(df[df["quiz_id"] == quiz_id]["q_index"].max() + 1) if not df[df["quiz_id"] == quiz_id].empty else 0
    append_rows(config.QUIZZES_XLSX, "questions", [{
        "quiz_id": quiz_id, "q_index": next_idx, "qtype": qtype, "question": question,
        "opt_a": options[0], "opt_b": options[1], "opt_c": options[2], "opt_d": options[3],
        "correct": correct_letter, "timer_sec": timer_sec, "points": points,
        "media_type": media_type or "", "media_file": media_file or "",
    }])
    return next_idx


def question_count(quiz_id: str) -> int:
    df = read_sheet(config.QUIZZES_XLSX, "questions")
    return int((df["quiz_id"] == quiz_id).sum())


def get_quiz_row(quiz_id: str) -> dict | None:
    df = get_quizzes()
    sub = df[df["quiz_id"].astype(str) == str(quiz_id)]
    if sub.empty:
        return None
    return sub.iloc[0].to_dict()


def mark_quiz_ready(quiz_id: str) -> None:
    """Ensure quiz appears as READY in the library once it has content."""
    df = get_quizzes()
    mask = df["quiz_id"].astype(str) == str(quiz_id)
    if not mask.any():
        return
    n = question_count(quiz_id)
    df.loc[mask, "status"] = "READY" if n else "DRAFT"
    write_sheet(config.QUIZZES_XLSX, "quizzes", df)


def delete_quiz(quiz_id: str) -> None:
    """Remove a quiz and all its questions. Past results are kept."""
    q = read_sheet(config.QUIZZES_XLSX, "quizzes")
    write_sheet(config.QUIZZES_XLSX, "quizzes", q[q["quiz_id"].astype(str) != str(quiz_id)])
    qs = read_sheet(config.QUIZZES_XLSX, "questions")
    write_sheet(config.QUIZZES_XLSX, "questions", qs[qs["quiz_id"].astype(str) != str(quiz_id)])


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


def clear_player_history(player: str, game_id: str | None = None) -> tuple[int, int]:
    """Remove a participant's saved scores and answers. Other players' data is kept."""
    scores = read_sheet(config.RESULTS_XLSX, "scores")
    answers = read_sheet(config.RESULTS_XLSX, "answers")
    player = str(player).strip()
    mask_s = (scores["player"].astype(str) == player) & (scores["is_bot"] == False)  # noqa: E712
    mask_a = answers["player"].astype(str) == player
    if game_id:
        gid = str(game_id)
        mask_s &= scores["game_id"].astype(str) == gid
        mask_a &= answers["game_id"].astype(str) == gid
    n_scores = int(mask_s.sum())
    n_answers = int(mask_a.sum())
    if n_scores:
        write_sheet(config.RESULTS_XLSX, "scores", scores[~mask_s])
    if n_answers:
        write_sheet(config.RESULTS_XLSX, "answers", answers[~mask_a])
    return n_scores, n_answers


# ---------------- Teams ----------------

def get_teams() -> pd.DataFrame:
    return read_sheet(config.TEAMS_XLSX, "teams")


def upsert_team(name: str, emoji: str, color: str, created_by: str) -> bool:
    """Insert a new team; returns False if name already exists."""
    df = get_teams()
    if not df.empty and not df[df["name"].str.lower() == name.strip().lower()].empty:
        return False
    append_rows(config.TEAMS_XLSX, "teams", [{
        "name": name.strip(),
        "emoji": emoji,
        "color": color,
        "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    return True


def delete_team(name: str) -> None:
    df = get_teams()
    df = df[df["name"].str.lower() != name.strip().lower()]
    write_sheet(config.TEAMS_XLSX, "teams", df)


def get_team_scoreboard() -> pd.DataFrame:
    """Aggregate total scores per team across all games (humans only)."""
    scores = read_sheet(config.RESULTS_XLSX, "scores")
    if scores.empty:
        return pd.DataFrame(columns=["Team", "Games", "Players", "Total Score", "Avg Score"])
    humans = scores[scores["is_bot"] == False]  # noqa: E712
    teams = humans[humans["team"].notna() & (humans["team"].astype(str).str.strip() != "")]
    if teams.empty:
        return pd.DataFrame(columns=["Team", "Games", "Players", "Total Score", "Avg Score"])
    agg = teams.groupby("team").agg(
        Games=("game_id", "nunique"),
        Players=("player", "nunique"),
        Total_Score=("score", "sum"),
    ).reset_index().rename(columns={"team": "Team", "Total_Score": "Total Score"})
    agg["Avg Score"] = (agg["Total Score"] / agg["Players"]).round(0).astype(int)
    return agg.sort_values("Total Score", ascending=False).reset_index(drop=True)
