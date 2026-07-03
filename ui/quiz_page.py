"""Participant gameplay — MCQ rounds, subjective typing, voting wall and reveal."""
import streamlit as st

import config
from core import game
from ui import components as ui

SHAPES = ["▲", "◆", "●", "■"]


def render() -> None:
    nick = st.session_state.get("nick", "")
    g = game.load()

    if not g or nick not in g.get("players", {}):
        st.warning("The game closed. Head back and join again!")
        if st.button("← Back to Login"):
            st.session_state.page = "login"
            st.rerun()
        return

    g = game.tick(g)                                  # bots move + auto phase changes

    if g["status"] == "FINISHED":
        st.session_state.page = "results"
        st.rerun()
    if g["status"] == "LOBBY":
        st.session_state.page = "lobby"
        st.rerun()

    me = g["players"][nick]
    q = game.current_q(g)
    is_controller = g["host"] == "__solo__" or st.session_state.get("role") == "admin"

    ui.topbar(ui.pill(f'{me["avatar"]} {nick}'), ui.pill("LIVE", live_dot=True, red=True))
    ui.hud(g["q_index"] + 1, len(g["questions"]), me["streak"], me["score"])

    if g["status"] == "QUESTION":
        _render_question(g, q, nick)
    elif g["status"] == "VOTING":
        _render_voting(g, nick)
    elif g["status"] == "REVEAL":
        _render_reveal(g, q, nick, is_controller)


# ---------------- QUESTION ----------------

def _render_question(g: dict, q: dict, nick: str) -> None:
    tl = game.time_left(g)
    ui.timer_ring(tl, q["timer"])
    kind = "🗳️ SUBJECTIVE — BEST ANSWERS WIN VOTES" if q["type"] == "subjective" \
        else f'MCQ · {q["points"]} PTS · SPEED BONUS ON'
    ui.question_text(kind, q["question"])

    answered = game.has_answered(g, nick)

    if q["type"] == "mcq":
        if answered:
            rec = next(a for a in g["players"][nick]["answers"] if a["q"] == g["q_index"])
            st.markdown(
                f'<div class="qt-verdict"><div class="sub">🔒 Locked in: '
                f'<b>{q["options"][rec["choice"]] if rec["choice"] is not None else "—"}</b> · '
                f'waiting for the others…</div></div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns(2)
            for i, opt in enumerate(q["options"]):
                col = c1 if i % 2 == 0 else c2
                with col:
                    if st.button(f"{SHAPES[i]}  {opt}", key=f"ans{i}", use_container_width=True):
                        rec = game.submit_answer(nick, i)
                        if rec:
                            st.session_state.last_points = rec["points"]
                        st.rerun()
    else:                                             # subjective — type your answer
        if answered:
            st.success("Answer submitted! ✍️ Get ready to vote when everyone's done…")
        else:
            with st.form("subj_form", border=False):
                text = st.text_area("Your answer", max_chars=500, height=110,
                                    placeholder="Type something brilliant — the room votes on it! 🗳️")
                sent = st.form_submit_button("Submit Answer ✍️", use_container_width=True)
            if sent and text.strip():
                game.submit_text(nick, text)
                st.rerun()

    ui.autorefresh(1.0)


# ---------------- VOTING ----------------

def _render_voting(g: dict, nick: str) -> None:
    tl = game.time_left(g)
    ui.timer_ring(tl, config.VOTING_TIMER_SEC)
    ui.question_text("🗳️ VOTE FOR THE BEST ANSWER — NOT YOUR OWN 😄",
                     game.current_q(g)["question"])

    voted = game.has_voted(g, nick)
    answers = game.current_answers(g)

    for i, a in enumerate(answers):
        team = f' · {a["team"]}' if a["team"] else ""
        mine = " (you)" if a["name"] == nick else ""
        st.markdown(
            f'<div class="qt-vote" style="animation-delay:{i * 0.08:.2f}s">'
            f'<span class="cnt">{"❤️ " + str(a["votes"]) if voted else ""}</span>'
            f'<div class="who">{a["avatar"]} {a["name"]}{team}{mine}</div>'
            f'<div class="txt">{a["text"]}</div></div>', unsafe_allow_html=True)
        if not voted and a["name"] != nick:
            if st.button(f'🗳️ Vote for {a["name"]}', key=f'vote{i}', use_container_width=True):
                game.submit_vote(nick, a["name"])
                st.rerun()

    if voted:
        st.markdown('<div class="qt-sub" style="text-align:center;margin-top:10px">'
                    'Vote locked! 🗳️ Waiting for the rest of the room…</div>', unsafe_allow_html=True)

    ui.autorefresh(1.2)


# ---------------- REVEAL ----------------

def _render_reveal(g: dict, q: dict, nick: str, is_controller: bool) -> None:
    me = g["players"][nick]
    rec = next((a for a in me["answers"] if a["q"] == g["q_index"]), None)

    if q["type"] == "mcq":
        good = bool(rec and rec["correct"])
        if good:
            ui.verdict(True, "NAILED IT! 🎯",
                       f'+<b>{rec["points"]:,} pts</b> · streak 🔥{me["streak"]}')
        else:
            picked = "time ran out ⏰" if not rec or rec["choice"] is None else "wrong pick 💥"
            ui.verdict(False, "OOPS!",
                       f'{picked} — the answer was <b>{q["options"][q["correct"]]}</b>')
        ui.distribution_bars(game.answer_distribution(g), q["options"], q["correct"])
    else:
        votes = rec["votes"] if rec else 0
        pts = rec["points"] if rec else 0
        ui.verdict(votes > 0, "THE VOTES ARE IN! 🗳️",
                   f'You got <b>{votes} vote(s)</b> → +<b>{pts:,} pts</b>')
        top = sorted(game.current_answers(g), key=lambda a: -a["votes"])[:3]
        for a in top:
            st.markdown(f'<div class="qt-vote"><span class="cnt">❤️ {a["votes"]}</span>'
                        f'<div class="who">{a["avatar"]} {a["name"]}</div>'
                        f'<div class="txt">{a["text"]}</div></div>', unsafe_allow_html=True)

    board = game.leaderboard(g)
    ui.podium(board)
    ui.rank_rows(board, me=nick)
    teams = game.team_leaderboard(g)
    if teams:
        st.markdown('<div class="qt-cat" style="margin-top:10px">TEAM BATTLE</div>', unsafe_allow_html=True)
        ui.team_rows(teams)

    last = g["q_index"] + 1 >= len(g["questions"])
    if is_controller:
        label = "See Final Results 🎉" if last else "Next Question ▶"
        if st.button(label, key="gold_next", use_container_width=True):
            game.next_question(nick)
            st.rerun()
    else:
        st.markdown('<div class="qt-sub" style="text-align:center;margin-top:8px">'
                    'Host is lining up the next round… 🎬</div>', unsafe_allow_html=True)
        ui.autorefresh(1.5)
