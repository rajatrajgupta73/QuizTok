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

    if ui.page_header(ui.pill("HOST MODE", red=True),
                       ui.pill(f'PIN <b>{g["pin"]}</b>'),
                       ui.pill(f'{len(g["players"])} players', live_dot=True),
                       logout_label="Logout", logout_key="host_logout"):
        ui.begin_exit_transition("logout")
        st.rerun()

    # quick nav — jump back to the Command Center or swap to another game
    nav1, nav2, _ = st.columns([1.1, 1.2, 2.4])
    if nav1.button("🎛️ Command Center", key="host_nav_cc", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()
    if nav2.button("🔄 Change / New Game", key="red_newgame", use_container_width=True):
        if g["status"] != "LOBBY":
            game.finish(email)            # persist scores before switching
        game.clear()
        st.session_state.page = "admin"
        st.rerun()

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
    ui.team_grouped_chips(g["players"])

    with st.expander("➕ Add media question (image / audio / video)", expanded=False):
        st.caption("Upload a clip or image with an MCQ or subjective prompt — "
                   "participants will see it when that round plays.")
        q = ui.media_question_builder(
            key_prefix="host_lobby_mq", quiz_id=str(g["quiz_id"]), show_quiz_picker=False)
        if q:
            q.pop("quiz_id", None)
            ok, msg = game.append_question_in_lobby(email, q)
            if ok:
                st.success(f"{msg} 🎯")
                st.rerun()
            else:
                st.error(msg)

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


def _game_flow(g: dict) -> None:
    """Prototype-style timeline: done / current / upcoming questions."""
    st.markdown('<div class="qt-h3" style="font-size:19px">🗺️ Game Flow</div>', unsafe_allow_html=True)
    idx, total = g["q_index"], len(g["questions"])
    rows = ['<div class="qt-tl done"><span class="dot2"></span><div>'
            '<div class="txt">Lobby & warm-up</div>'
            f'<div class="mt">{len(g["players"])} joined</div></div></div>']
    if idx > 0:
        rows.append('<div class="qt-tl done"><span class="dot2"></span><div>'
                    f'<div class="txt">Q1 – Q{idx} · played</div>'
                    '<div class="mt">scores locked in</div></div></div>')
    rows.append('<div class="qt-tl now"><span class="dot2"></span><div>'
                f'<div class="txt">Q{idx + 1} (you are here)</div>'
                '<div class="mt">collecting answers…</div></div></div>')
    if idx + 1 < total:
        rows.append('<div class="qt-tl"><span class="dot2"></span><div>'
                    f'<div class="txt">Q{idx + 2} – Q{total} · coming up</div>'
                    '<div class="mt">keep the energy up ✨</div></div></div>')
    rows.append('<div class="qt-tl"><span class="dot2"></span><div>'
                '<div class="txt">Podium + Funky Awards 🎉</div>'
                '<div class="mt">saved to Excel</div></div></div>')
    st.markdown("".join(rows), unsafe_allow_html=True)


def _hype(g: dict) -> None:
    st.markdown('<div class="qt-h3" style="font-size:19px;margin-top:18px">💥 Hype the room</div>',
                unsafe_allow_html=True)
    cols = st.columns(6)
    for i, em in enumerate(["🎉", "🔥", "😂", "🤯", "👏", "🚀"]):
        if cols[i].button(em, key=f"hype{i}"):
            st.toast(f"{em} {em} {em} hype sent to the room!")
    st.markdown('<div class="qt-sub" style="font-size:12.5px;margin-top:4px">'
                'Blasts the emoji on every player\'s screen</div>', unsafe_allow_html=True)


def _live(g: dict, email: str) -> None:
    q = game.current_q(g)
    tl = game.time_left(g)
    phase = "VOTING 🗳️" if g["status"] == "VOTING" else \
        ("SUBJECTIVE ✍️" if q["type"] == "subjective" else "MCQ ⚡")

    stage, side = st.columns([1.5, 1], gap="medium")

    with stage:
        st.markdown(f'<div class="qt-now">● LIVE · QUESTION {g["q_index"] + 1} OF '
                    f'{len(g["questions"])} · {phase} · {int(tl)}s LEFT</div>', unsafe_allow_html=True)
        ui.timer_ring(tl, config.VOTING_TIMER_SEC if g["status"] == "VOTING" else q["timer"])
        ui.question_stage(
            "VOTING 🗳️" if g["status"] == "VOTING" else
            ("SUBJECTIVE ✍️" if q["type"] == "subjective" else ""),
            q,
        )

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

    with side:
        _game_flow(g)
        _hype(g)

    ui.autorefresh(1.0)


def _reveal(g: dict, email: str) -> None:
    q = game.current_q(g)
    st.markdown(f'<div class="qt-cat">Q{g["q_index"] + 1} RESULTS</div>', unsafe_allow_html=True)
    ui.question_stage("", q)

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
    if not last:
        ui.countdown_popup(g["q_index"], g.get("reveal_started", 0.0))

    c1, c2 = st.columns([2, 1])
    label = "🎉 Finish & Show Podium" if last else "Next Question ▶"
    if c1.button(label, key="gold_next", use_container_width=True):
        game.next_question(email)
        st.rerun()
    if c2.button("🏁 End game early", key="red_end", use_container_width=True):
        game.finish(email)
        st.session_state.page = "results"
        st.rerun()
    if not last:
        ui.autorefresh(0.5)
