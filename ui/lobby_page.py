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

    ui.topbar(ui.pill(f'🎮 {nick}'), ui.pill("Lobby open", live_dot=True))
    ui.pin_banner(g["pin"], f'Playing <b style="color:#4db4ff">{g["quiz_title"]}</b> · waiting for the host to launch')

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown('<div class="qt-card"><b>🎭 Pick your avatar</b></div>', unsafe_allow_html=True)
        me = g["players"][nick]
        grid = st.columns(6)
        for i, av in enumerate(config.AVATARS):
            sel = "✓" if me["avatar"] == av else ""
            if grid[i % 6].button(f"{av}{sel}", key=f"avat{i}", use_container_width=True):
                game.set_avatar(nick, av)
                st.rerun()
        team_note = f' · team <b style="color:#4db4ff">{me["team"]}</b>' if me["team"] else ""
        st.markdown(
            f'<div class="qt-card" style="margin-top:10px">'
            f'<span style="font-size:30px">{me["avatar"]}</span> <b>{nick}</b>{team_note} '
            f'{ui.pill("READY", live_dot=True)}</div>', unsafe_allow_html=True)
        if st.button("Leave game", type="secondary"):
            st.session_state.page = "login"
            st.rerun()

    with col_b:
        st.markdown(f'<div class="qt-card"><b>👥 In the lobby</b> '
                    f'{ui.pill(str(len(g["players"])) + " joined", live_dot=True)}</div>',
                    unsafe_allow_html=True)
        ui.player_chips(g["players"])
        st.markdown('<div class="qt-sub" style="text-align:center;margin-top:16px">'
                    'Waiting for host to launch… ⏳<br>'
                    '<span style="font-size:12px">Tip: answer <b style="color:#4db4ff">fast</b> — '
                    'speed multiplies your points ⚡</span></div>', unsafe_allow_html=True)

    ui.autorefresh(1.5)
