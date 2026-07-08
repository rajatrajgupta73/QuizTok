"""Participant quiz performance reports — build, display, and export for learning."""
from __future__ import annotations

import base64
import csv
import io
from datetime import datetime

import config
from core import storage


def _mcq_accuracy(answers: list[dict]) -> str:
    mcqs = [a for a in answers if a.get("type") == "mcq"]
    if not mcqs:
        return "—"
    correct = sum(1 for a in mcqs if a.get("is_correct"))
    return f"{round(100 * correct / len(mcqs))}%"


def _learning_tips(report: dict) -> list[str]:
    tips: list[str] = []
    wrong = [q for q in report["questions"] if q.get("type") == "mcq" and q.get("is_correct") is False]
    slow = [q for q in report["questions"] if q.get("type") == "mcq" and q.get("is_correct")
            and (q.get("time_taken") or 99) > 12]
    subj = [q for q in report["questions"] if q.get("type") == "subjective"]
    if wrong:
        tips.append(f"Review {len(wrong)} missed MCQ(s) — compare your pick with the correct answer below.")
    if slow:
        tips.append("You nailed some answers but took a while — skim similar topics to answer faster next time.")
    if subj and report.get("votes_received", 0) == 0:
        tips.append("Try shorter, clearer subjective answers — the room votes on the most compelling replies.")
    elif subj and report.get("votes_received", 0) >= 5:
        tips.append("Great subjective rounds — your answers resonated with the room. Keep that style!")
    if report.get("best_streak", 0) >= 3:
        tips.append(f"Hot streak of {report['best_streak']} in a row — momentum matters, ride it early.")
    if not tips:
        tips.append("Solid run! Re-read the questions below to lock the facts in long-term memory.")
    return tips


def _question_rows_from_game(g: dict, nick: str) -> list[dict]:
    player = g["players"].get(nick, {})
    rows: list[dict] = []
    for a in sorted(player.get("answers", []), key=lambda x: x["q"]):
        q = g["questions"][a["q"]]
        row: dict = {
            "q_num": a["q"] + 1,
            "type": q["type"],
            "question": q["question"],
            "points": a.get("points", 0),
            "time_taken": a.get("time_taken"),
            "votes": a.get("votes", 0),
        }
        if q.get("media_type"):
            row["media_type"] = q["media_type"]
            row["media_file"] = q.get("media_file", "")
        if q["type"] == "mcq":
            picked = q["options"][a["choice"]] if a.get("choice") is not None else "(no answer)"
            row.update({
                "your_answer": picked,
                "correct_answer": q["options"][q["correct"]],
                "is_correct": bool(a.get("correct")),
                "options": list(q["options"]),
            })
        else:
            row.update({
                "your_answer": a.get("text") or "(no answer)",
                "correct_answer": "(subjective — scored by peer votes)",
                "is_correct": None,
            })
        rows.append(row)
    return rows


def build_report_from_game(g: dict, nick: str) -> dict | None:
    """Build a full performance report from a live/finished game dict."""
    if nick not in g.get("players", {}):
        return None
    from core import game

    p = g["players"][nick]
    board = game.leaderboard(g)
    rank = next((i + 1 for i, r in enumerate(board) if r["name"] == nick), 0)
    mcqs = [a for a in p["answers"] if a.get("correct") is not None]
    return {
        "player": nick,
        "avatar": p.get("avatar", "🎯"),
        "team": p.get("team", ""),
        "quiz_title": g.get("quiz_title", "Quiz"),
        "game_id": g.get("game_id", ""),
        "played_at": g.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "rank": rank,
        "total_players": len(g.get("players", {})),
        "score": p.get("score", 0),
        "correct": sum(1 for a in mcqs if a.get("correct")),
        "answered": len(p.get("answers", [])),
        "best_streak": p.get("best_streak", 0),
        "votes_received": p.get("votes_received", 0),
        "mcq_accuracy": _mcq_accuracy(_question_rows_from_game(g, nick)),
        "questions": _question_rows_from_game(g, nick),
    }


def player_game_history(player: str) -> list[dict]:
    """Past games for a participant (newest first), humans only."""
    scores = storage.read_sheet(config.RESULTS_XLSX, "scores")
    games = storage.read_sheet(config.RESULTS_XLSX, "games")
    if scores.empty or games.empty:
        return []
    mine = scores[(scores["player"].astype(str) == player) & (scores["is_bot"] == False)]  # noqa: E712
    if mine.empty:
        return []
    merged = mine.merge(games, on="game_id", how="left", suffixes=("", "_game"))
    merged = merged.sort_values("played_at", ascending=False)
    out: list[dict] = []
    for _, r in merged.iterrows():
        out.append({
            "game_id": str(r["game_id"]),
            "quiz_title": str(r.get("quiz_title", "")),
            "played_at": str(r.get("played_at", "")),
            "rank": int(r["rank"]),
            "score": int(r["score"]),
            "correct": int(r["correct"]) if str(r["correct"]) not in ("", "nan") else 0,
            "answered": int(r["answered"]) if str(r["answered"]) not in ("", "nan") else 0,
            "best_streak": int(r["best_streak"]) if str(r["best_streak"]) not in ("", "nan") else 0,
            "votes_received": int(r["votes_received"]) if str(r["votes_received"]) not in ("", "nan") else 0,
            "team": str(r["team"]) if str(r.get("team", "")) not in ("", "nan") else "",
            "avatar": str(r["avatar"]) if str(r.get("avatar", "")) not in ("", "nan") else "🎯",
        })
    return out


def build_report_from_history(game_id: str, player: str) -> dict | None:
    """Rebuild a report from persisted Excel results."""
    scores = storage.read_sheet(config.RESULTS_XLSX, "scores")
    games = storage.read_sheet(config.RESULTS_XLSX, "games")
    answers = storage.read_sheet(config.RESULTS_XLSX, "answers")
    if scores.empty or answers.empty:
        return None
    score_row = scores[(scores["game_id"].astype(str) == game_id)
                       & (scores["player"].astype(str) == player)]
    if score_row.empty:
        return None
    s = score_row.iloc[0]
    game_row = games[games["game_id"].astype(str) == game_id]
    ans = answers[(answers["game_id"].astype(str) == game_id)
                  & (answers["player"].astype(str) == player)].sort_values("q_index")
    questions: list[dict] = []
    for _, a in ans.iterrows():
        qtype = "subjective" if str(a.get("correct_answer", "")).startswith("(subjective") else "mcq"
        is_correct = a["is_correct"]
        if str(is_correct) in ("", "nan", "None"):
            ic = None
        else:
            ic = bool(is_correct) if not isinstance(is_correct, bool) else is_correct
        row = {
            "q_num": int(a["q_index"]),
            "type": qtype,
            "question": str(a["question"]),
            "your_answer": str(a["picked"]),
            "correct_answer": str(a["correct_answer"]),
            "is_correct": ic,
            "points": int(a["points"]) if str(a["points"]) not in ("", "nan") else 0,
            "time_taken": float(a["time_taken_sec"]) if str(a["time_taken_sec"]) not in ("", "nan") else None,
            "votes": int(a["votes"]) if str(a["votes"]) not in ("", "nan") else 0,
        }
        questions.append(row)
    total_players = int(scores[scores["game_id"].astype(str) == game_id]["player"].nunique())
    mcq_acc = _mcq_accuracy(questions)
    report = {
        "player": player,
        "avatar": str(s["avatar"]) if str(s.get("avatar", "")) not in ("", "nan") else "🎯",
        "team": str(s["team"]) if str(s.get("team", "")) not in ("", "nan") else "",
        "quiz_title": str(game_row.iloc[0]["quiz_title"]) if not game_row.empty else "Quiz",
        "game_id": game_id,
        "played_at": str(game_row.iloc[0]["played_at"]) if not game_row.empty else "",
        "rank": int(s["rank"]),
        "total_players": total_players,
        "score": int(s["score"]),
        "correct": int(s["correct"]) if str(s["correct"]) not in ("", "nan") else 0,
        "answered": int(s["answered"]) if str(s["answered"]) not in ("", "nan") else 0,
        "best_streak": int(s["best_streak"]) if str(s["best_streak"]) not in ("", "nan") else 0,
        "votes_received": int(s["votes_received"]) if str(s["votes_received"]) not in ("", "nan") else 0,
        "mcq_accuracy": mcq_acc,
        "questions": questions,
    }
    report["learning_tips"] = _learning_tips(report)
    return report


def finalize_report(report: dict) -> dict:
    report = dict(report)
    report.setdefault("learning_tips", _learning_tips(report))
    return report


def report_to_csv(report: dict) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["QuizTok Performance Report"])
    w.writerow(["Player", report.get("player", "")])
    w.writerow(["Quiz", report.get("quiz_title", "")])
    w.writerow(["Played", report.get("played_at", "")])
    w.writerow(["Score", report.get("score", 0)])
    w.writerow(["Rank", f'{report.get("rank", "—")}/{report.get("total_players", "—")}'])
    w.writerow(["MCQ Accuracy", report.get("mcq_accuracy", "—")])
    w.writerow(["Best Streak", report.get("best_streak", 0)])
    w.writerow(["Votes Received", report.get("votes_received", 0)])
    w.writerow([])
    w.writerow(["#", "Type", "Question", "Your Answer", "Correct Answer", "Result",
                "Points", "Time (s)", "Votes"])
    for q in report.get("questions", []):
        if q.get("type") == "mcq":
            result = "Correct" if q.get("is_correct") else "Incorrect"
        else:
            result = f'{q.get("votes", 0)} vote(s)'
        w.writerow([
            q.get("q_num", ""),
            q.get("type", ""),
            q.get("question", ""),
            q.get("your_answer", ""),
            q.get("correct_answer", ""),
            result,
            q.get("points", 0),
            q.get("time_taken", ""),
            q.get("votes", 0),
        ])
    w.writerow([])
    w.writerow(["Learning Tips"])
    for tip in report.get("learning_tips", []):
        w.writerow([tip])
    return buf.getvalue().encode("utf-8-sig")


def _media_img_tag(media_file: str) -> str:
    path = storage.media_path(media_file)
    if not path or path.stat().st_size > 2 * 1024 * 1024:
        return f'<p class="media-note">📎 Media file: {media_file}</p>'
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    ext = path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
    return f'<img class="q-media" src="data:{mime};base64,{b64}" alt="Question media"/>'


def report_to_html(report: dict) -> bytes:
    tips = report.get("learning_tips") or _learning_tips(report)
    q_blocks: list[str] = []
    for q in report.get("questions", []):
        media_html = ""
        if q.get("media_type") == "image" and q.get("media_file"):
            media_html = _media_img_tag(q["media_file"])
        elif q.get("media_type"):
            media_html = f'<p class="media-note">{q["media_type"].upper()} round — shown during live quiz</p>'
        if q.get("type") == "mcq":
            status = "correct" if q.get("is_correct") else "wrong"
            badge = "✓ Correct" if q.get("is_correct") else "✗ Incorrect"
            opts = ""
            if q.get("options"):
                opts = "<ul class='opts'>" + "".join(
                    f"<li>{o}</li>" for o in q["options"]) + "</ul>"
        else:
            status = "subjective"
            badge = f'🗳️ {q.get("votes", 0)} vote(s) · +{q.get("points", 0)} pts'
            opts = ""
        q_blocks.append(
            f'<article class="q-card {status}">'
            f'<div class="q-head"><span class="q-num">Q{q.get("q_num")}</span>'
            f'<span class="badge">{badge}</span></div>'
            f'{media_html}'
            f'<p class="q-text">{q.get("question", "")}</p>'
            f'{opts}'
            f'<div class="ans"><span class="lbl">Your answer</span>'
            f'<p>{q.get("your_answer", "")}</p></div>'
            f'<div class="ans correct-ans"><span class="lbl">Correct / scoring</span>'
            f'<p>{q.get("correct_answer", "")}</p></div>'
            f'<div class="meta">+{q.get("points", 0)} pts'
            f'{f" · {q.get('time_taken')}s" if q.get("time_taken") is not None else ""}</div>'
            f'</article>'
        )
    tips_html = "".join(f"<li>{t}</li>" for t in tips)
    team = f' · {report["team"]}' if report.get("team") else ""
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>QuizTok Report — {report.get("player", "")}</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background:#0a1628; color:#eef5ff;
    margin:0; padding:32px 20px; line-height:1.5; }}
  .wrap {{ max-width:820px; margin:0 auto; }}
  h1 {{ font-size:28px; margin:0 0 6px; }}
  .sub {{ color:#7a94b0; margin-bottom:24px; }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin-bottom:28px; }}
  .stat {{ background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1);
    border-radius:14px; padding:14px; text-align:center; }}
  .stat b {{ display:block; font-size:22px; color:#4db4ff; }}
  .stat span {{ font-size:12px; letter-spacing:1px; text-transform:uppercase; color:#7a94b0; }}
  h2 {{ font-size:18px; margin:28px 0 12px; color:#ffc233; }}
  .q-card {{ background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08);
    border-radius:16px; padding:18px 20px; margin-bottom:14px; }}
  .q-card.correct {{ border-left:4px solid #00c9a7; }}
  .q-card.wrong {{ border-left:4px solid #e21836; }}
  .q-card.subjective {{ border-left:4px solid #ffc233; }}
  .q-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }}
  .q-num {{ font-weight:800; color:#4db4ff; }}
  .badge {{ font-size:13px; font-weight:700; }}
  .q-text {{ font-size:17px; font-weight:600; margin:8px 0 12px; }}
  .q-media {{ max-width:100%; border-radius:12px; margin:8px 0 12px; }}
  .media-note {{ font-size:13px; color:#ffc233; }}
  .opts {{ margin:8px 0 12px 18px; color:#b8cce0; font-size:14px; }}
  .ans {{ margin-top:10px; }}
  .lbl {{ font-size:11px; letter-spacing:1.5px; text-transform:uppercase; color:#7a94b0; }}
  .ans p {{ margin:4px 0 0; }}
  .correct-ans p {{ color:#00c9a7; }}
  .meta {{ margin-top:10px; font-size:13px; color:#7a94b0; }}
  .tips {{ background:rgba(0,136,206,.12); border-radius:14px; padding:16px 20px; }}
  .tips li {{ margin:6px 0; }}
  footer {{ margin-top:32px; font-size:12px; color:#5a7390; text-align:center; }}
</style></head><body><div class="wrap">
  <h1>{report.get("avatar", "🎯")} {report.get("player", "")}{team}</h1>
  <p class="sub">{report.get("quiz_title", "")} · {report.get("played_at", "")}</p>
  <div class="stats">
    <div class="stat"><b>{report.get("score", 0):,}</b><span>Total score</span></div>
    <div class="stat"><b>#{report.get("rank", "—")}</b><span>of {report.get("total_players", "—")}</span></div>
    <div class="stat"><b>{report.get("mcq_accuracy", "—")}</b><span>MCQ accuracy</span></div>
    <div class="stat"><b>{report.get("best_streak", 0)}</b><span>Best streak</span></div>
    <div class="stat"><b>{report.get("votes_received", 0)}</b><span>Votes received</span></div>
  </div>
  <h2>📚 Question-by-question review</h2>
  {"".join(q_blocks)}
  <h2>💡 Learning tips</h2>
  <ul class="tips">{tips_html}</ul>
  <footer>Generated by QuizTok · {config.APP_NAME} — study this anytime offline.</footer>
</div></body></html>"""
    return html.encode("utf-8")


def download_filename(report: dict, ext: str) -> str:
    safe_player = "".join(c if c.isalnum() or c in "-_" else "_" for c in report.get("player", "player"))
    stamp = datetime.now().strftime("%Y%m%d")
    return f"QuizTok_{safe_player}_{stamp}.{ext}"
