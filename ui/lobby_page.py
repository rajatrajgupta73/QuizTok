"""Participant lobby — avatar picker, live roster, waits for host to launch."""
import streamlit as st

import config
from core import game
from ui import components as ui


def render() -> None:
    g = game.load()
    nick = st.session_state.get("nick", "")

    if not g or nick not in g.get("players", {}):
        st.warning("The game closed. Head back and join again!")
        if st.button("← Back to Login"):
            st.session_state.page = "login"
            st.rerun()
        return

    if g["status"] != "LOBBY":                       # host launched → play!
        st.session_state.page = "quiz"
        st.rerun()

    # Add playful sound effects for avatar selection
    ui.sound_effects()

    ui.topbar(ui.pill(f'🎮 {nick}'), ui.pill("Lobby open", live_dot=True))
    ui.pin_banner(g["pin"], f'Playing <b style="color:#4db4ff">{g["quiz_title"]}</b> · waiting for the host to launch')

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown('<div class="qt-h3">🎭 Pick your avatar</div>', unsafe_allow_html=True)
        me = g["players"][nick]
        grid = st.columns(6)
        for i, av in enumerate(config.AVATARS):
            sel = "✓" if me["avatar"] == av else ""
            if grid[i % 6].button(f"{av}{sel}", key=f"avat{i}", use_container_width=True):
                game.set_avatar(nick, av)
                st.rerun()
        team_note = f' · team <b style="color:#4db4ff">{me["team"]}</b>' if me["team"] else ""
        st.markdown(
            f'<div class="qt-mestrip">'
            f'<span class="av">{me["avatar"]}</span>'
            f'<span><span class="name">{nick}</span><br>'
            f'<span class="tag">You · ready to rumble{team_note}</span></span>'
            f'<span class="ready">{ui.pill("READY", live_dot=True)}</span></div>',
            unsafe_allow_html=True)
        if st.button("Leave game", type="secondary"):
            st.session_state.page = "login"
            st.rerun()

    with col_b:
        st.markdown(f'<div class="qt-h3">👥 In the lobby '
                    f'<span class="count">{len(g["players"])}</span></div>',
                    unsafe_allow_html=True)
        ui.player_chips(g["players"])
        ui.waiting_dots("Waiting for host to launch")
        st.markdown('<div class="qt-sub" style="text-align:center;font-size:12px">'
                    'Tip: answer <b style="color:#4db4ff">fast</b> — '
                    'speed multiplies your points ⚡</div>', unsafe_allow_html=True)

    ui.autorefresh(1.5)
