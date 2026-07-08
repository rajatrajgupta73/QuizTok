"""Participant gameplay — MCQ rounds, subjective typing, voting wall and reveal."""
import streamlit as st

import config
from core import domain_knowledge, game
from ui import components as ui
from ui import learn_panel

SHAPES = ["▲", "◆", "●", "■"]


def render() -> None:
    nick = st.session_state.get("nick", "")
    g = game.load()

    if not g or nick not in g.get("players", {}):
        st.warning("Session ended. Return to your profile arena.")
        if st.button("← Back to Profile"):
            st.session_state.page = "hub"
            st.rerun()
        return

    # Add playful sound effects for participant interactions
    ui.sound_effects()

    g = game.tick(g)                                  # bots move + auto phase changes

    if g["status"] == "FINISHED":
        st.session_state.page = "results"
        st.rerun()
    if g["status"] == "LOBBY":
        st.session_state.page = "lobby"
        st.rerun()

    me = g["players"][nick]
    q = game.current_q(g)
    is_solo = g["host"] == "__solo__"

    st.markdown('<span class="qt-quiz-scope"></span>', unsafe_allow_html=True)

    if ui.page_header(ui.pill(f'{me["avatar"]} {nick}'), ui.pill("LIVE", live_dot=True, red=True),
                       logout_label="Logout", logout_key="quiz_logout"):
        ui.begin_exit_transition("logout")
        st.rerun()
    
    ui.hud(g["q_index"] + 1, len(g["questions"]), me["streak"], me["score"])

    # live stats rail (left) · game stage (centre) · team chat (right, live games only)
    if is_solo:
        rail_l, stage = st.columns([1.55, 2.45], gap="medium")
    else:
        rail_l, stage, rail_r = st.columns([1.55, 1.7, 1.25], gap="medium")
    with rail_l:
        st.markdown('<span class="qt-quiz-stats-col"></span>', unsafe_allow_html=True)
        ui.stats_rail(game.team_leaderboard(g), game.leaderboard(g)[:3], me["team"], nick)
    if not is_solo:
        with rail_r:
            st.markdown('<span class="qt-quiz-chat-col"></span>', unsafe_allow_html=True)
            ui.team_chat_rail(g, nick)
    with stage:
        st.markdown('<span class="qt-quiz-stage-col"></span>', unsafe_allow_html=True)
        if g["status"] == "QUESTION":
            _render_question(g, q, nick)
        elif g["status"] == "VOTING":
            _render_voting(g, nick)
        elif g["status"] == "REVEAL":
            _render_reveal(g, q, nick)

    learn_panel.domain_drawer_inject(g.get("quiz_title", ""))


# ---------------- QUESTION ----------------

def _render_question(g: dict, q: dict, nick: str) -> None:
    tl = game.time_left(g)
    ui.timer_ring(tl, q["timer"])
    kind = "🗳️ SUBJECTIVE — BEST ANSWERS WIN VOTES" if q["type"] == "subjective" else ""
    ui.question_stage(kind, q)

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
    ui.question_stage("🗳️ VOTE FOR THE BEST ANSWER — NOT YOUR OWN 😄", game.current_q(g))

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

def _render_reveal(g: dict, q: dict, nick: str) -> None:
    me = g["players"][nick]
    rec = next((a for a in me["answers"] if a["q"] == g["q_index"]), None)

    if q.get("media_type"):
        ui.question_media(q)

    if q["type"] == "mcq":
        good = bool(rec and rec["correct"])
        correct_idx = q["correct"]
        correct_text = q["options"][correct_idx]
        domain_knowledge.track_question_outcome(nick, q["question"], good if rec else False)
        if good:
            ui.verdict(True, "NAILED IT! 🎯",
                       f'+<b>{rec["points"]:,} pts</b> · streak 🔥{me["streak"]}',
                       answer=correct_text, answer_idx=correct_idx)
            ui.points_pop(rec["points"])
        else:
            picked = "Time ran out ⏰" if not rec or rec["choice"] is None else "Wrong pick 💥"
            ui.verdict(False, "OOPS!",
                       f'{picked} — streak reset, comeback time!',
                       answer=correct_text, answer_idx=correct_idx)
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

    # Add spacing and keep focus on player's performance
    st.markdown('<div style="margin-top:30px;margin-bottom:10px;"></div>', unsafe_allow_html=True)

    last = g["q_index"] + 1 >= len(g["questions"])

    if not last:
        ui.countdown_popup(g["q_index"], g.get("reveal_started", 0.0))
    elif g["host"] != "__solo__":
        st.markdown('<div class="qt-sub" style="text-align:center;margin-top:8px">'
                    'Host is wrapping up the game… 🎬</div>', unsafe_allow_html=True)

    ui.autorefresh(0.5)
