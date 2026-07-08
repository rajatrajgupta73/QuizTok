"""Login page — participant join (PIN + nickname + optional team) and admin sign-in."""
import streamlit as st

import config
from core import auth, game, logger, storage
from ui import components as ui


def _team_options() -> list[str]:
    """Return ['🎯 Solo'] + all teams from Excel (falling back to config list)."""
    try:
        df = storage.get_teams()
        names = df["name"].dropna().tolist() if not df.empty else []
    except Exception:
        names = []
    return ["\U0001f3af Solo"] + (names if names else list(config.TEAM_SUGGESTIONS))


def render() -> None:
    st.markdown('<span class="qt-login-scope"></span>', unsafe_allow_html=True)
    
    # Add fun sound for Join button
    ui.sound_effects()
    
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            f'<div class="qt-rise" style="padding-top:30px">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:26px">{ui.citi_logo(72)}'
            f'<span class="qt-sub" style="letter-spacing:2.5px;font-weight:600;font-size:13px">· TEAM ENGAGEMENT ARENA</span></div>'
            f'<div class="qt-brand" style="font-size:74px;line-height:1.1">QuizTok</div>'
            f'<div class="qt-h1" style="font-size:28px;line-height:1.4;margin-top:6px">Play.<br>Learn.<br>QuizTok it!</div>'
            f'{ui.red_arc()}'
            f'<p class="qt-sub" style="font-size:18px;line-height:1.65;margin-bottom:30px">The <b style="color:#eef5ff">funkiest way</b> '
            f'to play, learn, quiz with teams — live battles, streaks, power-ups and podium glory. '
            f'Built with 💙 for <b style="color:#eef5ff">teams</b>.</p>'
            f'<div style="display:flex;gap:14px;flex-wrap:wrap">'
            f'<div class="qt-badge"><span class="ico">⚡</span> Live Battles</div>'
            f'<div class="qt-badge"><span class="ico">🔥</span> Streak Bonuses</div>'
            f'<div class="qt-badge"><span class="ico">🏆</span> Team Podiums</div>'
            f'<div class="qt-badge"><span class="ico">💬</span> Team Chat</div>'
            f'</div></div>',
            unsafe_allow_html=True)

    with right:
        st.markdown('<span class="qt-login-card"></span>', unsafe_allow_html=True)
        tab_play, tab_host, tab_admin = st.tabs(["Participant", "Host", "Admin"])
        ui.inject_login_tab_icons()

        # ---------------- participant ----------------
        with tab_play:
            with st.form("join_form", border=False):
                pin = st.text_input("GAME PIN", max_chars=6, placeholder="••••••", key="pinbox")
                n1, n2 = st.columns(2)
                first = n1.text_input("FIRST NAME", max_chars=20, placeholder="e.g. rahul")
                last = n2.text_input("LAST NAME", max_chars=20, placeholder="e.g. sharma")
                team_opts = _team_options()
                p_team_sel = st.selectbox("SELECT TEAM", team_opts, key="p_team_sel")
                join = st.form_submit_button("Join the Fun 🚀", use_container_width=True)

            if join:
                if len(pin.strip()) < 4 or not first.strip() or not last.strip():
                    st.error("Enter the game PIN, your first name and last name to jump in!")
                else:
                    # any input case accepted — shown in proper case after login
                    formatted_name = f"{first.strip().title()} {last.strip().title()}"
                    selected_team = "" if p_team_sel == "\U0001f3af Solo" else p_team_sel

                    ok, result = game.join(pin, formatted_name, "🦊", selected_team, "")
                    if ok:
                        # result is the actual nick (may have number appended if duplicate)
                        st.session_state.update(role="participant", nick=result,
                                                soeid="", team=selected_team,
                                                dest_page="lobby", page="transition")
                        st.rerun()
                    else:
                        st.error(result)

        # ---------------- host ----------------
        with tab_host:
            with st.form("host_form", border=False):
                h_email = st.text_input("WORK EMAIL", placeholder="host@abc.com", key="host_email")
                h_pwd = st.text_input("PASSWORD", type="password", placeholder="••••••••", key="host_pwd")
                h_go = st.form_submit_button("Enter Host Dashboard", use_container_width=True)
            if h_go:
                ok, name = auth.verify_host(h_email, h_pwd)
                if ok:
                    st.session_state.update(role="host", admin_email=h_email.strip(),
                                            admin_name=name, team="",
                                            dest_page="admin", page="transition")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Default: host@abc.com / host123")
            st.markdown(
                f'<div class="qt-sub" style="text-align:center;font-size:12.5px">First run? '
                f'Sign in with <b style="color:#4db4ff">host@abc.com / host123</b></div>',
                unsafe_allow_html=True)

        # ---------------- admin ----------------
        with tab_admin:
            with st.form("admin_form", border=False):
                email = st.text_input("WORK EMAIL", placeholder="you@abc.com")
                pwd = st.text_input("PASSWORD", type="password", placeholder="••••••••")
                go = st.form_submit_button("Enter Command Center", use_container_width=True)
            if go:
                ok, name = auth.verify_admin(email, pwd)
                if ok:
                    st.session_state.update(role="admin", admin_email=email.strip(),
                                            admin_name=name, dest_page="admin", page="transition")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Default: admin@abc.com / admin123")
            st.markdown(
                f'<div class="qt-sub" style="text-align:center;font-size:12.5px">First run? '
                f'Sign in with <b style="color:#4db4ff">admin@abc.com / admin123</b></div>',
                unsafe_allow_html=True)

    # Creator credit — bottom-right corner, slightly elevated
    # Uses parent-realm injection with janitor-style cleanup so it doesn't leak
    # to other pages (same pattern as mascot/glow-ring in theme.py)
    st.components.v1.html(
        '<script>'
        'var P=window.parent, doc=P.document;'
        'if (!P.__qtCreditJanitor) {'
        '  P.__qtCreditJanitor = setInterval(function(){'
        '    var scope = doc.querySelector(".qt-login-scope");'
        '    var el = doc.getElementById("qt-creator-credit");'
        '    if (!scope) {'
        '      if (el) el.remove();'
        '    } else if (!el) {'
        '      el = doc.createElement("div");'
        '      el.id = "qt-creator-credit";'
        '      el.innerHTML = "Created by <b style=\'color:#4db4ff\'>Rajat Raj Gupta</b>";'
        '      el.style.cssText = "position:fixed;bottom:50px;right:32px;z-index:9999;'
        'font-family:Poppins,sans-serif;font-size:25px;color:#9db4d0;'
        'opacity:0.75;pointer-events:none;letter-spacing:0.3px";'
        '      doc.body.appendChild(el);'
        '    }'
        '  }, 600);'
        '}'
        '</script>',
        height=0)

