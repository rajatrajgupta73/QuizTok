"""Live host control room — lobby control, answer distribution, voting monitor, flow control."""
import streamlit as st

import config
from core import game
from ui import components as ui


def render() -> None:
    email = st.session_state.get("admin_email", "host")
    g = game.load()

    if not g:
        st.warning("No live game. Create one from the Quiz Library.")
        if st.button("← Command Center"):
            st.session_state.page = "admin"
            st.rerun()
        return

    g = game.tick(g)

    ui.topbar(ui.pill("HOST MODE", red=True),
              ui.pill(f'PIN <b>{g["pin"]}</b>'),
              ui.pill(f'{len(g["players"])} players', live_dot=True))

    if g["status"] == "LOBBY":
        _lobby(g, email)
    elif g["status"] in ("QUESTION", "VOTING"):
        _live(g, email)
    elif g["status"] == "REVEAL":
        _reveal(g, email)
    else:  # FINISHED
        st.session_state.page = "results"
        st.rerun()


def _lobby(g: dict, email: str) -> None:
    ui.pin_banner(g["pin"], f'Hosting <b style="color:#4db4ff">{g["quiz_title"]}</b> · '
                            f'{len(g["questions"])} questions · share the PIN with the room!')
    st.markdown('<div style="margin-top:14px"></div>', unsafe_allow_html=True)
    ui.player_chips(g["players"])

    c1, c2 = st.columns([2, 1])
    if c1.button("🚀 LAUNCH GAME", key="gold_launch", use_container_width=True,
                 disabled=len(g["players"]) == 0):
        game.start(email)
        st.rerun()
    if c2.button("Cancel game", key="red_cancel", use_container_width=True):
        game.clear()
        st.session_state.page = "admin"
        st.rerun()
    ui.autorefresh(1.5)


def _live(g: dict, email: str) -> None:
    q = game.current_q(g)
    tl = game.time_left(g)
    phase = "VOTING 🗳️" if g["status"] == "VOTING" else \
        ("SUBJECTIVE ✍️" if q["type"] == "subjective" else "MCQ ⚡")
    st.markdown(f'<div class="qt-cat">● LIVE · Q{g["q_index"] + 1} OF {len(g["questions"])} · '
                f'{phase} · {int(tl)}s LEFT</div>', unsafe_allow_html=True)
    ui.timer_ring(tl, config.VOTING_TIMER_SEC if g["status"] == "VOTING" else q["timer"])
    st.markdown(f'<div class="qt-question">{q["question"]}</div>', unsafe_allow_html=True)

    humans = [n for n, p in g["players"].items() if not p["is_bot"]]
    if g["status"] == "QUESTION":
        done = sum(1 for n in humans if game.has_answered(g, n))
        bots_done = sum(1 for n, p in g["players"].items()
                        if p["is_bot"] and game.has_answered(g, n))
        st.markdown(
            f'<div class="qt-sub" style="text-align:center">'
            f'<b style="color:#4db4ff">{done}/{len(humans)}</b> humans answered · '
            f'{bots_done} bots in 🤖</div>', unsafe_allow_html=True)
        st.progress(done / max(1, len(humans)))
        if st.button("⏭️ End answering now", key="red_skip", use_container_width=True):
            game.force_reveal(email)
            st.rerun()
    else:  # VOTING
        voted = sum(1 for n in humans if game.has_voted(g, n))
        st.markdown(f'<div class="qt-sub" style="text-align:center">'
                    f'<b style="color:#4db4ff">{voted}/{len(humans)}</b> humans voted</div>',
                    unsafe_allow_html=True)
        for a in sorted(game.current_answers(g), key=lambda x: -x["votes"]):
            st.markdown(f'<div class="qt-vote"><span class="cnt">❤️ {a["votes"]}</span>'
                        f'<div class="who">{a["avatar"]} {a["name"]}</div>'
                        f'<div class="txt">{a["text"]}</div></div>', unsafe_allow_html=True)
        if st.button("⏭️ Close voting now", key="red_endvote", use_container_width=True):
            game.force_end_voting(email)
            st.rerun()

    ui.autorefresh(1.0)


def _reveal(g: dict, email: str) -> None:
    q = game.current_q(g)
    st.markdown(f'<div class="qt-cat">Q{g["q_index"] + 1} RESULTS</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="qt-question">{q["question"]}</div>', unsafe_allow_html=True)

    if q["type"] == "mcq":
        ui.distribution_bars(game.answer_distribution(g), q["options"], q["correct"])
    else:
        for a in sorted(game.current_answers(g), key=lambda x: -x["votes"])[:5]:
            st.markdown(f'<div class="qt-vote"><span class="cnt">❤️ {a["votes"]}</span>'
                        f'<div class="who">{a["avatar"]} {a["name"]}</div>'
                        f'<div class="txt">{a["text"]}</div></div>', unsafe_allow_html=True)

    board = game.leaderboard(g)
    ui.podium(board)
    teams = game.team_leaderboard(g)
    if teams:
        ui.team_rows(teams)

    last = g["q_index"] + 1 >= len(g["questions"])
    c1, c2 = st.columns([2, 1])
    label = "🎉 Finish & Show Podium" if last else "Next Question ▶"
    if c1.button(label, key="gold_next", use_container_width=True):
        game.next_question(email)
        st.rerun()
    if c2.button("🏁 End game early", key="red_end", use_container_width=True):
        game.finish(email)
        st.session_state.page = "results"
        st.rerun()
