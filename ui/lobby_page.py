"""Participant lobby — live roster, team chat, waits for host to launch."""
import streamlit as st

from core import game
from ui import components as ui


def render() -> None:
    g = game.load()
    nick = st.session_state.get("nick", "")

    if not g or nick not in g.get("players", {}):
        st.warning("The game closed. Head back to your profile arena.")
        if st.button("← Back to Profile"):
            st.session_state.page = "hub"
            st.rerun()
        return

    if g["status"] != "LOBBY":                       # host launched → play!
        st.session_state.page = "quiz"
        st.rerun()

    ui.sound_effects()

    if ui.page_header(ui.pill(f'🎮 {nick}'), ui.pill("Lobby open", live_dot=True),
                       logout_label="Back to profile", logout_key="lobby_leave"):
        st.session_state.page = "hub"
        st.rerun()

    ui.pin_banner(g["pin"], f'Playing <b style="color:#4db4ff">{g["quiz_title"]}</b> · waiting for the host to launch')

    st.markdown(f'<div class="qt-h3">👥 In the lobby '
                f'<span class="count">{len(g["players"])}</span></div>',
                unsafe_allow_html=True)
    ui.team_grouped_chips(g["players"])
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    if g["host"] != "__solo__":
        ui.team_chat_rail(g, nick)
    ui.waiting_dots("Waiting for host to launch")
    st.markdown('<div class="qt-sub" style="text-align:center;font-size:12px">'
                'Tip: answer <b style="color:#4db4ff">fast</b> — '
                'speed multiplies your points ⚡</div>', unsafe_allow_html=True)

    ui.autorefresh(1.5)
