"""Login page — participant join (PIN + nickname + optional team) and admin sign-in."""
import streamlit as st

import config
from core import auth, game, logger
from ui import components as ui


def render() -> None:
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            f'<div class="qt-rise" style="padding-top:30px">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">{ui.citi_logo(70)}'
            f'<span class="qt-sub" style="letter-spacing:2.5px;font-weight:700">· TEAM ENGAGEMENT ARENA</span></div>'
            f'<div class="qt-h1">Play. Learn.<br>'
            f'<span class="qt-brand" style="font-size:46px">QuizTok</span> it!</div>'
            f'{ui.red_arc()}'
            f'<p class="qt-sub" style="font-size:16px;line-height:1.7">The <b style="color:#eef5ff">funkiest way</b> '
            f'to quiz with your team — live battles, streaks, voting rounds and podium glory.<br>'
            f'Built with 💙 for <b style="color:#eef5ff">Citi teams</b>.</p>'
            f'<div style="margin-top:14px">{ui.pill("⚡ Live Battles")} {ui.pill("🔥 Streak Bonuses")} '
            f'{ui.pill("🗳️ Voting Rounds")} {ui.pill("🏆 Team Podiums")}</div></div>',
            unsafe_allow_html=True)

    with right:
        tab_play, tab_admin = st.tabs(["🎮  Participant", "🛠️  Admin"])

        # ---------------- participant ----------------
        with tab_play:
            with st.form("join_form", border=False):
                pin = st.text_input("GAME PIN", max_chars=6, placeholder="••••••", key="pinbox")
                nick = st.text_input("YOUR NICKNAME", max_chars=20, placeholder="e.g. QuizNinja_Rahul")
                team = st.selectbox("TEAM (optional — vote & win together)",
                                    ["— solo player —"] + config.TEAM_SUGGESTIONS + ["✏️ Custom team…"])
                custom = st.text_input("Custom team name", max_chars=24,
                                       placeholder="only if you picked Custom")
                join = st.form_submit_button("Join the Fun 🚀", use_container_width=True)

            if join:
                team_name = "" if team == "— solo player —" else (custom.strip() if team.startswith("✏️") else team)
                if len(pin.strip()) < 4 or not nick.strip():
                    st.error("Enter the game PIN and a nickname to jump in!")
                else:
                    ok, msg = game.join(pin, nick, "🦊", team_name)
                    if ok:
                        st.session_state.update(role="participant", nick=nick.strip(),
                                                team=team_name, page="lobby")
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown('<div class="qt-sub" style="text-align:center;margin:6px 0">— or —</div>',
                        unsafe_allow_html=True)
            solo_nick = st.text_input("Nickname for solo demo", max_chars=20, value="",
                                      placeholder="Try it alone vs 6 bots 🤖", label_visibility="collapsed")
            if st.button("🤖 Play Solo Demo vs Bots", use_container_width=True, type="secondary"):
                nickname = solo_nick.strip() or "QuizNinja"
                game.start_solo_demo(nickname, "🦊")
                st.session_state.update(role="participant", nick=nickname, team="", page="quiz")
                st.rerun()

        # ---------------- admin ----------------
        with tab_admin:
            with st.form("admin_form", border=False):
                email = st.text_input("CITI EMAIL", placeholder="you@citi.com")
                pwd = st.text_input("PASSWORD", type="password", placeholder="••••••••")
                go = st.form_submit_button("Enter Command Center 🎛️", use_container_width=True)
            if go:
                ok, name = auth.verify_admin(email, pwd)
                if ok:
                    st.session_state.update(role="admin", admin_email=email.strip(),
                                            admin_name=name, page="admin")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Default: admin@citi.com / citi123")
            st.markdown(
                f'<div class="qt-sub" style="text-align:center;font-size:12.5px">First run? '
                f'Sign in with <b style="color:#4db4ff">admin@citi.com / citi123</b></div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="qt-sub" style="text-align:center;margin-top:34px;font-size:12.5px">'
        'QuizTok · An internal team-engagement game for <b style="color:#4db4ff">Citi</b> · '
        'runs 100% locally · all data saved to Excel 📊</div>', unsafe_allow_html=True)
