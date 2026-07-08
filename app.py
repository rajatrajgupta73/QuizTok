"""QuizTok — ABC Company-branded team quiz platform.

Run with:  streamlit run app.py
Everything is local: Excel data files in ./data, no internet required.
"""
import streamlit as st

import config
from core import auth, game, seed, question_bank, storage
from ui import theme
from ui import components as ui
from ui import lobby_page, quiz_page, results_page, admin_page, host_page, transition_page, participant_hub_page

_DISCLAIMER = (
    "Disclaimer: QuizTok is a demo for entertainment only. All content is synthetically generated "
    "from public internet sources. No real employee or company data is collected or displayed. "
    "Not affiliated with or endorsed by any organization."
)

st.set_page_config(page_title="QuizTok · ABC Company Team Fun", page_icon="🎮",
                   layout="wide", initial_sidebar_state="collapsed")


@st.cache_resource
def _bootstrap() -> bool:
    """One-time setup: data folder, default admin, sample quizzes, 2000-question bank."""
    seed.run()
    question_bank.ensure_bank()
    return True


def _team_options() -> list[str]:
    """Return ['🎯 Solo'] + all teams from Excel (falling back to config list)."""
    try:
        df = storage.get_teams()
        names = df["name"].dropna().tolist() if not df.empty else []
    except Exception:
        names = []
    return ["Solo"] + (names if names else list(config.TEAM_SUGGESTIONS))


def _quiz_categories() -> list[str]:
    quizzes = storage.get_quizzes()
    if quizzes.empty:
        return ["All"]
    cats = sorted(quizzes["category"].dropna().unique().tolist())
    return ["All"] + cats


def _quiz_options(category: str = "All") -> list[tuple[str, str]]:
    """Return [(label, quiz_id), ...] for quizzes that have at least one question."""
    quizzes = storage.get_quizzes()
    if quizzes.empty:
        return []
    qdf = storage.read_sheet(config.QUIZZES_XLSX, "questions")
    opts: list[tuple[str, str]] = []
    for _, row in quizzes.iterrows():
        if category != "All" and row["category"] != category:
            continue
        n_q = int((qdf["quiz_id"].astype(str) == str(row["quiz_id"])).sum())
        if not n_q:
            continue
        label = f'{row["emoji"]} {row["title"]} · {row["category"]} · {n_q} Qs'
        opts.append((label, str(row["quiz_id"])))
    return opts


_BOT_PRESETS = {
    "🟢 Casual — 3 friendly bots": 3,
    "🟡 Standard — 6 bots": 6,
    "🔴 Challenge — 8 sharp bots": 8,
}


def _render_login() -> None:
    """Participant join (PIN + first/last name + optional team) and admin/host sign-in."""
    st.markdown('<span class="qt-login-scope"></span>', unsafe_allow_html=True)
    ui.sound_effects()

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            f'<div class="qt-rise" style="padding-top:30px">'
            f'<div class="qt-h1" style="font-size:92px;line-height:0.95;margin-bottom:10px">'
            f'<span class="qt-brand" style="font-size:92px;display:inline-block;letter-spacing:-.5px;'
            f'background:linear-gradient(92deg,#4db4ff 0%,#9be1ff 45%,#ff5d73 100%);'
            f'-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">QuizTok</span></div>'
            f'{ui.red_arc(190)}'
            f'<span class="qt-sub" style="letter-spacing:2.5px;font-weight:600;font-size:13px;display:block;margin-bottom:22px">'
            f'TEAM ENGAGEMENT ARENA</span>'
            f'<div class="qt-h1" style="font-size:48px;line-height:1.1">Play.<br>'
            f'Learn.<br>'
            f'<span class="qt-brand" style="font-size:48px;letter-spacing:-.5px;'
            f'background:linear-gradient(92deg,#4db4ff 0%,#9be1ff 45%,#ff5d73 100%);'
            f'-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">QuizTok</span> it!</div>'
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

        with tab_play:
            st.markdown('<div class="qt-cat" style="margin-bottom:10px">🎭 PICK AVATAR</div>',
                        unsafe_allow_html=True)
            if "participant_avatar" not in st.session_state:
                st.session_state.participant_avatar = config.AVATARS[0]
            av_grid = st.columns(6)
            for i, av in enumerate(config.AVATARS):
                picked = st.session_state.participant_avatar == av
                if av_grid[i % 6].button(
                    av,
                    key=f"login_avat{i}",
                    type="primary" if picked else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.participant_avatar = av
                    st.rerun()

            with st.form("participant_profile", border=False):
                n1, n2 = st.columns(2)
                first = n1.text_input("FIRST NAME", max_chars=20, placeholder="e.g. rahul")
                last = n2.text_input("LAST NAME", max_chars=20, placeholder="e.g. sharma")
                funky = st.text_input(
                    "FUNNY NICKNAME (optional)",
                    max_chars=24,
                    placeholder="e.g. QuizZapper, Ops Ninja, KPI Crusher…",
                )
                enter = st.form_submit_button("Enter Arena 🚀", use_container_width=True)

            if enter:
                if not first.strip() or not last.strip():
                    st.error("Enter your first and last name to continue!")
                else:
                    formatted_name = f"{first.strip().title()} {last.strip().title()}"
                    display = funky.strip() if funky.strip() else formatted_name
                    st.session_state.update(
                        role="participant",
                        nick=display,
                        first_name=first.strip().title(),
                        last_name=last.strip().title(),
                        full_name=formatted_name,
                        avatar=st.session_state.participant_avatar,
                        team="",
                        dest_page="hub",
                        hub_section="join",
                        page="transition",
                    )
                    st.rerun()

            st.markdown(
                '<div class="qt-sub" style="text-align:center;font-size:12.5px;margin-top:8px">'
                'Set up your profile once — then join a live PIN, battle bots, or explore '
                'banking domain paths in your arena.</div>',
                unsafe_allow_html=True)

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


def _inject_login_chrome() -> None:
    """Disclaimer + creator credit on login — sync immediately and prune stale transition DOM."""
    text = _DISCLAIMER.replace("'", "\\'")
    st.components.v1.html(
        f"<script>"
        f"(function(){{"
        f"var P=window.parent, doc=P.document, TXT='{text}';"
        f"if(P.__qtCreditJanitor){{clearInterval(P.__qtCreditJanitor);P.__qtCreditJanitor=null;}}"
        f"if(P.__qtDisclaimerJanitor){{clearInterval(P.__qtDisclaimerJanitor);P.__qtDisclaimerJanitor=null;}}"
        f"function qtCleanupTransition(){{"
        f"  doc.querySelectorAll('#qt-tr,.qt-tr-pt').forEach(function(el){{el.remove();}});"
        f"  doc.querySelectorAll('[data-testid=\"stVerticalBlockBorderWrapper\"]').forEach(function(w){{"
        f"    if(w.querySelector('.qt-transition-scope')&&!w.querySelector('.qt-login-scope')){{"
        f"      w.style.display='none';"
        f"    }}"
        f"  }});"
        f"}}"
        f"function qtSyncLoginChrome(){{"
        f"  qtCleanupTransition();"
        f"  var scope=doc.querySelector('.qt-login-scope');"
        f"  var disc=doc.getElementById('qt-app-disclaimer');"
        f"  var cred=doc.getElementById('qt-creator-credit');"
        f"  if(!scope){{"
        f"    if(disc)disc.remove();"
        f"    if(cred)cred.remove();"
        f"    return;"
        f"  }}"
        f"  if(!disc){{"
        f"    disc=doc.createElement('div');"
        f"    disc.id='qt-app-disclaimer';"
        f"    disc.textContent=TXT;"
        f"    disc.style.cssText='position:fixed;bottom:14px;left:50%;transform:translateX(-50%);"
        f"max-width:min(920px,calc(100vw - 32px));z-index:9998;pointer-events:none;"
        f"font-family:Poppins,sans-serif;font-size:11px;line-height:1.45;color:#7a94b0;"
        f"text-align:center;padding:0 12px;opacity:0.82';"
        f"    doc.body.appendChild(disc);"
        f"  }}"
        f"  if(!cred){{"
        f"    cred=doc.createElement('div');"
        f"    cred.id='qt-creator-credit';"
        f"    cred.innerHTML=\"Created by <b style='color:#4db4ff'>Rajat Raj Gupta</b>\";"
        f"    cred.style.cssText=\"position:fixed;bottom:50px;right:32px;z-index:9999;"
        f"font-family:Poppins,sans-serif;font-size:25px;color:#9db4d0;"
        f"opacity:0.75;pointer-events:none;letter-spacing:0.3px\";"
        f"    doc.body.appendChild(cred);"
        f"  }}"
        f"}}"
        f"qtSyncLoginChrome();"
        f"if(!P.__qtLoginChromeJanitor){{"
        f"  P.__qtLoginChromeJanitor=setInterval(qtSyncLoginChrome,600);"
        f"}}"
        f"}})();"
        f"</script>",
        height=0)


_bootstrap()
theme.inject()

PAGES = {
    "login":      _render_login,
    "hub":        participant_hub_page.render,
    "lobby":      lobby_page.render,
    "quiz":       quiz_page.render,
    "results":    results_page.render,
    "admin":      admin_page.render,
    "host":       host_page.render,
    "transition": transition_page.render,
}

page = st.session_state.setdefault("page", "login")

if page in ("hub", "lobby", "quiz", "results") and st.session_state.get("role") == "participant":
    if page != "login" and not st.session_state.get("nick"):
        page = st.session_state["page"] = "login"

if page in ("admin", "host") and st.session_state.get("role") not in ("admin", "host"):
    page = st.session_state["page"] = "login"
if page == "transition" and not st.session_state.get("role"):
    if st.session_state.get("transition_mode") != "exit":
        page = st.session_state["page"] = "login"

if st.session_state.get("_last_page") != page:
    prev_page = st.session_state.get("_last_page")
    st.session_state["_last_page"] = page
    st.session_state["_settle"] = True
    if page == "hub" and prev_page != "hub":
        st.session_state["hub_section"] = "join"

PAGES.get(page, _render_login)()
if page == "login":
    _inject_login_chrome()
