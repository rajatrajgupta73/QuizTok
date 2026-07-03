"""Grand finale — confetti, champion, team battle result, funky awards."""
import streamlit as st

from core import game
from ui import components as ui


def render() -> None:
    g = game.load()
    nick = st.session_state.get("nick", "")

    if not g:
        st.warning("No finished game found.")
        if st.button("← Back to Login"):
            st.session_state.page = "login"
            st.rerun()
        return

    ui.confetti(100)
    ui.topbar(ui.pill("🎉 Game Over"))

    board = game.leaderboard(g)
    champ = board[0] if board else None

    if champ:
        st.markdown(
            f'<div style="text-align:center" class="qt-rise">'
            f'<div style="font-size:84px;animation:qtBounce 2.4s ease-in-out infinite">🏆</div>'
            f'<div class="qt-h1" style="background:linear-gradient(92deg,#ffd76e,#ff9d2e,#ff5d73);'
            f'-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">CHAMPION!</div>'
            f'<div style="font-size:22px;font-weight:700;margin-top:8px">{champ["avatar"]} {champ["name"]} takes the crown</div>'
            f'<div class="qt-sub" style="font-size:16px"><b style="color:#ffc233">{champ["score"]:,} points</b> · '
            f'best streak 🔥{champ["best_streak"]} · {champ["votes_received"]} votes received</div></div>',
            unsafe_allow_html=True)

    ui.podium(board)
    ui.rank_rows(board, me=nick)

    teams = game.team_leaderboard(g)
    if teams:
        st.markdown('<div class="qt-cat" style="margin-top:14px">🏁 TEAM BATTLE RESULT</div>',
                    unsafe_allow_html=True)
        ui.team_rows(teams)

    if g.get("awards"):
        st.markdown('<div class="qt-cat" style="margin-top:16px">— FUNKY AWARDS —</div>',
                    unsafe_allow_html=True)
        ui.awards_strip(g["awards"])

    st.markdown('<div class="qt-sub" style="margin:14px 0 4px">📊 Full results saved to '
                '<b style="color:#4db4ff">data/results.xlsx</b> — scores, every answer, votes and timings.</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("Play Again 🔁", use_container_width=True):
        st.session_state.page = "lobby" if st.session_state.get("role") == "participant" else "admin"
        st.rerun()
    if c2.button("Exit to Login", use_container_width=True, type="secondary"):
        st.session_state.page = "login"
        st.rerun()
    if st.session_state.get("role") == "admin":
        if c3.button("Command Center 🎛️", key="red_cc", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()
