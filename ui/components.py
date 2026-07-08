"""Reusable HTML components rendered with st.markdown (all offline)."""
import json
import random
import time

import streamlit as st

import config


# Official Citi wordmark vectors (public-domain extraction of the real logo,
# assets/citi_logo.svg). Letters take `ink` so the reversed (white) version
# can sit on our dark background; the arc keeps Citi's exact red #d9261c.
_CITI_LETTERS = (
    "m38.400442,64.214842-0.213828,0.206921c-3.446638,3.511502-7.435859,5.372563-11.546423,5.372563"
    "-8.580217,0-14.808582-6.436766-14.808582-15.318118,0-8.86532,6.228365-15.311212,14.808582-15.311212,"
    "4.110564,0,8.099785,1.868707,11.546423,5.38958l0.213828,0.213088,5.518073-6.672297-0.147484-0.181026"
    "c-4.589023-5.422875-10.095258-8.06279-16.86448-8.06279-6.792652,0-13.002027,2.286003-17.4771072,6.408651"
    "-4.8622878,4.464475-7.4294475,10.760663-7.4294475,18.216006,0,7.451645,2.5671597,13.76337,7.4294475,18.229079,"
    "4.4750802,4.141638,10.6844552,6.415063,17.4771072,6.415063,6.769222,0,12.275457-2.638436,16.86448-8.063531"
    "l0.147484-0.168447-5.518073-6.67353z|"
    "m49.494547,78.212262,9.748252,0,0-47.58753-9.748252,0,0,47.58753z|"
    "m97.427357,67.864702c-2.600701,1.583604-5.021116,2.379722-7.194656,2.379722-3.149451,0-4.572746-1.662278"
    "-4.572746-5.364917v-25.250109h9.928044v-8.961259h-9.928044v-14.807103l-9.554648,5.113356v9.693747h-8.242583"
    "v8.961259h8.242583v26.860842c0,7.318218,4.334995,12.317631,10.806043,12.447604,4.393939,0.08607,7.042733"
    "-1.222785,8.651493-2.179705l0.09421-0.07004,2.346921-9.17558-0.576619,0.352186z|"
    "m105.50125,78.212262,9.75466,0,0-47.58753-9.75466,0,0,47.58753z"
)
_CITI_ARC = (
    "M121.09485,22.1809c-8.92353-12.6397281-23.742961-20.1808984-38.820616-20.1808984"
    "-15.071489,0-29.893883,7.5411703-38.80261,20.1808984l-0.457003,0.650361h11.235917l0.124547-0.134906"
    "c7.647468-7.89311,17.63051-12.067303,27.899149-12.067303,10.269872,0,20.250946,4.174193,27.913206,12.067303"
    "l0.1243,0.134906h11.23247l-0.44936-0.650361z"
)


def citi_logo(width: int = 56, ink: str = "#ffffff") -> str:
    """The real Citi wordmark. ink='#003b70' for the official blue on light chips."""
    height = round(width * 195 / 300)
    letters = "".join(f'<path d="{d}" fill-rule="nonzero" fill="{ink}"/>'
                      for d in _CITI_LETTERS.split("|"))
    return (f'<svg viewBox="0 0 300 195" width="{width}" height="{height}" '
            f'style="vertical-align:middle" aria-label="citi">'
            f'<g transform="matrix(2.4760713,0,0,2.4760713,-2.9521334,-2.9521466)">'
            f'{letters}<path d="{_CITI_ARC}" fill-rule="evenodd" fill="#d9261c"/></g></svg>')


def red_arc(width: int = 170) -> str:
    return f'''<svg class="qt-arc" viewBox="0 0 190 26" width="{width}">
      <path d="M8 22 Q 95 -14 182 22" stroke="#e21836" stroke-width="7" fill="none" stroke-linecap="round"/>
    </svg>'''


_LUCIDE_PATHS = {
    "users": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "presentation": (
        '<path d="M2 3h20"/>'
        '<path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/>'
        '<path d="m7 21 5-5 5 5"/>'
    ),
    "shield-check": (
        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
        '<path d="m9 12 2 2 4-4"/>'
    ),
    "gamepad-2": (
        '<line x1="6" x2="10" y1="11" y2="11"/>'
        '<line x1="8" x2="8" y1="9" y2="13"/>'
        '<line x1="15" x2="15.01" y1="12" y2="12"/>'
        '<line x1="18" x2="18.01" y1="10" y2="10"/>'
        '<path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.062 1.013-.088 2.026-.007 3.04C2.879 13.365 4.12 15 6.32 15h11.36c2.2 0 3.441-1.635 3.629-3.43.081-1.014.055-2.027-.007-3.04A4 4 0 0 0 17.32 5z"/>'
    ),
    "bot": (
        '<path d="M12 8V4H8"/>'
        '<rect width="16" height="12" x="4" y="8" rx="2"/>'
        '<path d="M2 14h2"/>'
        '<path d="M20 14h2"/>'
        '<path d="M15 13v2"/>'
        '<path d="M9 13v2"/>'
    ),
    "book-open": (
        '<path d="M12 7v14"/>'
        '<path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>'
    ),
    "clipboard-list": (
        '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
        '<path d="M12 11h4"/>'
        '<path d="M12 16h4"/>'
        '<path d="M8 11h.01"/>'
        '<path d="M8 16h.01"/>'
    ),
    "user": (
        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),
    "message-square": (
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
    ),
    "compass": (
        '<path d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"/>'
        '<circle cx="12" cy="12" r="10"/>'
    ),
    "menu": (
        '<line x1="4" x2="20" y1="12" y2="12"/>'
        '<line x1="4" x2="20" y1="6" y2="6"/>'
        '<line x1="4" x2="20" y1="18" y2="18"/>'
    ),
}


def lucide_icon(name: str, size: int = 16, css_class: str = "qt-tab-ico",
                stroke: str = "currentColor") -> str:
    """Inline Lucide SVG icon (offline, stroke style)."""
    paths = _LUCIDE_PATHS.get(name, "")
    return (
        f'<span class="{css_class}" aria-hidden="true">'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg></span>'
    )


_HUB_NAV_TONE_COLORS = {
    "blue": "#4db4ff",
    "violet": "#a78bfa",
    "teal": "#2ee4c6",
    "gold": "#ffc233",
    "rose": "#ff6b84",
    "slate": "#94a3b8",
    "sky": "#4db4ff",
}


def hub_nav_icon(icon: str, tone: str, size: int = 18) -> str:
    """Coloured Lucide icon for participant hub nav (no background tile)."""
    color = _HUB_NAV_TONE_COLORS.get(tone, "#4db4ff")
    return lucide_icon(icon, size, "qt-hub-nav-ico", stroke=color)


def inject_login_tab_icons() -> None:
    """Prepend Lucide icons to Participant / Host / Admin login tabs."""
    icons = json.dumps([
        lucide_icon("users"),
        lucide_icon("presentation"),
        lucide_icon("shield-check"),
    ])
    st.components.v1.html(
        f"<script>"
        f"(function(){{"
        f"var P=window.parent,doc=P.document,ICONS={icons};"
        f"function paint(){{"
        f"  if(!doc.querySelector('.qt-login-scope'))return;"
        f"  var m=doc.querySelector('.qt-login-card');"
        f"  if(!m)return;"
        f"  var root=m.closest('[data-testid=\"stColumn\"],[data-testid=\"column\"]');"
        f"  if(!root)return;"
        f"  root.querySelectorAll('[data-baseweb=\"tab\"]').forEach(function(tab,i){{"
        f"    if(tab.querySelector('.qt-tab-ico')||!ICONS[i])return;"
        f"    tab.insertAdjacentHTML('afterbegin',ICONS[i]);"
        f"  }});"
        f"}}"
        f"paint();"
        f"if(P.__qtTabIconJanitor)clearInterval(P.__qtTabIconJanitor);"
        f"P.__qtTabIconJanitor=setInterval(paint,400);"
        f"}})();"
        f"</script>",
        height=0,
    )

def topbar(*pills_html: str) -> None:
    pills = "".join(pills_html)
    st.markdown(
        f'<div class="qt-topbar"><span class="qt-brand">QuizTok</span>'
        f'<span class="qt-spacer"></span>{pills}</div>',
        unsafe_allow_html=True)


def page_header(*pills_html: str, logout_label: str = "Logout",
                logout_key: str = "qt_logout", show_logout: bool = True) -> bool:
    """Brand bar on the left; leave/logout button pinned top-right."""
    bar_l, bar_r = st.columns([5, 1.45], gap="small", vertical_alignment="center")
    with bar_l:
        topbar(*pills_html)
    if show_logout:
        with bar_r:
            return st.button(logout_label, type="secondary", key=logout_key,
                             use_container_width=True)
    return False


def pill(text: str, live_dot: bool = False, red: bool = False) -> str:
    dot = '<span class="dot"></span>' if live_dot else ''
    cls = "qt-pill red" if red else "qt-pill"
    return f'<span class="{cls}">{dot}{text}</span>'


def pin_banner(pin: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="qt-card qt-rise" style="text-align:center">'
        f'<div class="qt-sub" style="letter-spacing:3px;font-weight:700">GAME PIN</div>'
        f'<div class="qt-pin">{pin}</div>'
        f'<div class="qt-sub">{subtitle}</div></div>', unsafe_allow_html=True)


def player_chips(players: dict) -> None:
    chips = []
    for i, (name, p) in enumerate(players.items()):
        team = f'<span class="tm">· {p["team"]}</span>' if p.get("team") else ""
        chips.append(
            f'<span class="qt-chip" style="animation-delay:{i * 0.06:.2f}s">'
            f'<span class="em">{p["avatar"]}</span>{name}{team}</span>')
    st.markdown(f'<div class="qt-chips">{"".join(chips)}</div>', unsafe_allow_html=True)


def team_grouped_chips(players: dict) -> None:
    """Lobby roster grouped by team (teams A→Z, names A→Z inside; solo last)."""
    groups: dict[str, list] = {}
    for name, p in players.items():
        groups.setdefault(p.get("team") or "", []).append((name, p))
    solo = groups.pop("", [])
    html = []
    for team in sorted(groups, key=str.lower):
        members = sorted(groups[team], key=lambda x: x[0].lower())
        chips = "".join(f'<span class="qt-chip"><span class="em">{p["avatar"]}</span>{n}</span>'
                        for n, p in members)
        html.append(f'<div class="qt-cat" style="text-align:left;margin:10px 0 6px">🛡️ {team} '
                    f'<span style="color:#9db4d0">· {len(members)}</span></div>'
                    f'<div class="qt-chips">{chips}</div>')
    if solo:
        chips = "".join(f'<span class="qt-chip"><span class="em">{p["avatar"]}</span>{n}</span>'
                        for n, p in sorted(solo, key=lambda x: x[0].lower()))
        html.append(f'<div class="qt-cat" style="text-align:left;margin:10px 0 6px">🎯 Solo '
                    f'<span style="color:#9db4d0">· {len(solo)}</span></div>'
                    f'<div class="qt-chips">{chips}</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def hud(q_no: int, q_total: int, streak: int, score: int) -> None:
    pct = int(100 * q_no / q_total)
    hot = ""
    if streak >= 10:
        hot = " streak-hot-10"
    elif streak >= 5:
        hot = " streak-hot-5"
    elif streak >= 3:
        hot = " streak-hot-3"
    st.markdown(
        f'<div class="qt-hud"><span class="qno">Q{q_no} / {q_total}</span>'
        f'<span class="bar"><i style="width:{pct}%"></i></span>'
        f'<span class="qt-streak{hot}"><span class="fl">🔥</span>{streak} streak</span>'
        f'<span class="qt-score">⭐ <b>{score:,}</b></span></div>', unsafe_allow_html=True)


def timer_ring(seconds_left: float, total: int) -> None:
    r, circ = 38, 2 * 3.14159 * 38
    frac = max(0.0, min(1.0, seconds_left / total)) if total else 0
    color = "#e21836" if seconds_left <= 5 else "#4db4ff"
    danger = "danger" if seconds_left <= 5 else ""
    # qt-timer-stroke uses CSS transition (0.52s linear) for smooth sweep between rerenders
    st.markdown(
        f'<div class="qt-timerwrap"><div class="qt-timer {danger}">'
        f'<svg viewBox="0 0 86 86" aria-hidden="true">'
        f'<circle cx="43" cy="43" r="{r}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="7"/>'
        f'<circle class="qt-timer-stroke" cx="43" cy="43" r="{r}" fill="none" stroke="{color}" '
        f'stroke-width="7" stroke-linecap="round" '
        f'stroke-dasharray="{circ:.0f}" stroke-dashoffset="{circ * (1 - frac):.0f}"/></svg>'
        f'<span class="num">{int(seconds_left)}</span></div></div>', unsafe_allow_html=True)


def question_text(category: str, text: str) -> None:
    cat = f'<div class="qt-cat">{category}</div>' if category else ""
    st.markdown(f'<div class="qt-card qt-qcard qt-rise">{cat}'
                f'<div class="qt-question" style="margin-bottom:0">{text}</div></div>',
                unsafe_allow_html=True)


def question_media(q: dict) -> None:
    """Render image / audio / video attachment for a question (participants + host)."""
    from core import storage

    media_type = q.get("media_type", "")
    media_file = q.get("media_file", "")
    if not media_type or not media_file:
        return
    path = storage.media_path(media_file)
    if not path:
        return
    if media_type == "audio":
        st.markdown('<div class="qt-qmedia-label">🎧 Listen carefully</div>', unsafe_allow_html=True)
        st.audio(str(path))
    elif media_type == "image":
        st.image(str(path), use_container_width=True)
    elif media_type == "video":
        st.video(str(path))


def question_stage(category: str, q: dict) -> None:
    """Question card with optional media + prompt text."""
    cat = f'<div class="qt-cat">{category}</div>' if category else ""
    media_type = q.get("media_type", "")
    media_label = ""
    if media_type == "image":
        media_label = '<div class="qt-qmedia-badge">🖼️ IMAGE ROUND</div>'
    elif media_type == "audio":
        media_label = '<div class="qt-qmedia-badge">🎧 AUDIO ROUND</div>'
    elif media_type == "video":
        media_label = '<div class="qt-qmedia-badge">🎬 VIDEO ROUND</div>'
    st.markdown(f'<div class="qt-card qt-qcard qt-rise">{cat}{media_label}',
                unsafe_allow_html=True)
    question_media(q)
    st.markdown(f'<div class="qt-question" style="margin-bottom:0">{q["question"]}</div></div>',
                unsafe_allow_html=True)


def performance_review_panel(report: dict, *, key_prefix: str = "perf") -> None:
    """On-screen Q-by-Q review + download buttons for a participant report."""
    from core import participant_report

    report = participant_report.finalize_report(report)
    team = f' · {report["team"]}' if report.get("team") else ""
    st.markdown(
        f'<div class="qt-perf-summary">'
        f'<span class="av">{report.get("avatar", "🎯")}</span>'
        f'<span><span class="name">{report.get("player", "")}{team}</span>'
        f'<span class="meta">{report.get("quiz_title", "")} · '
        f'Rank <b>#{report.get("rank", "—")}</b> of {report.get("total_players", "—")} · '
        f'<b>{report.get("score", 0):,}</b> pts · MCQ {report.get("mcq_accuracy", "—")}</span></span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, str(report.get("correct", 0)), "MCQ CORRECT", tone="teal")
    kpi_card(c2, str(report.get("best_streak", 0)), "BEST STREAK", tone="gold")
    kpi_card(c3, str(report.get("votes_received", 0)), "VOTES WON", tone="pink")
    kpi_card(c4, str(len(report.get("questions", []))), "QUESTIONS", spark="📚")

    tips = report.get("learning_tips", [])
    if tips:
        st.markdown('<div class="qt-cat" style="margin-top:14px">💡 LEARNING TIPS</div>',
                    unsafe_allow_html=True)
        for tip in tips:
            st.markdown(f'<div class="qt-perf-tip">{tip}</div>', unsafe_allow_html=True)

    st.markdown('<div class="qt-cat" style="margin-top:16px">📋 QUESTION REVIEW</div>',
                unsafe_allow_html=True)
    for q in report.get("questions", []):
        if q.get("type") == "mcq":
            ok = q.get("is_correct")
            icon = "✅" if ok else "❌"
            result = f'<span style="color:{"#00c9a7" if ok else "#e21836"}">{icon} '
            result += "Correct" if ok else "Incorrect"
            result += f' · +{q.get("points", 0)} pts</span>'
            if q.get("time_taken") is not None:
                result += f' <span style="color:#7a94b0">· {q["time_taken"]}s</span>'
        else:
            result = (f'<span style="color:#ffc233">🗳️ {q.get("votes", 0)} vote(s) · '
                      f'+{q.get("points", 0)} pts</span>')
        media = ""
        if q.get("media_type"):
            icons = {"image": "🖼️", "audio": "🎧", "video": "🎬"}
            media = f' <span style="color:#ffc233;font-size:11px">'
            media += icons.get(q["media_type"], "📎") + f' {q["media_type"]}</span>'
        st.markdown(
            f'<div class="qt-perf-q {"good" if q.get("is_correct") else "bad" if q.get("type") == "mcq" else "subj"}">'
            f'<div class="qtop"><b>Q{q.get("q_num")}.</b> {q.get("question", "")}{media}</div>'
            f'<div class="qans"><span class="lbl">Your answer</span> {q.get("your_answer", "")}</div>'
            f'<div class="qans"><span class="lbl">Correct / scoring</span> '
            f'{q.get("correct_answer", "")}</div>'
            f'<div class="qres">{result}</div></div>',
            unsafe_allow_html=True,
        )

    d1, d2 = st.columns(2)
    html_bytes = participant_report.report_to_html(report)
    csv_bytes = participant_report.report_to_csv(report)
    fname_html = participant_report.download_filename(report, "html")
    fname_csv = participant_report.download_filename(report, "csv")
    d1.download_button(
        "📥 Download study guide (HTML)",
        data=html_bytes,
        file_name=fname_html,
        mime="text/html",
        use_container_width=True,
        key=f"{key_prefix}_dl_html",
        help="Open offline in any browser — full Q&A review with tips.",
    )
    d2.download_button(
        "📥 Download spreadsheet (CSV)",
        data=csv_bytes,
        file_name=fname_csv,
        mime="text/csv",
        use_container_width=True,
        key=f"{key_prefix}_dl_csv",
        help="Import into Excel for your own notes.",
    )


_MEDIA_ACCEPT = {
    "image": list(config.MEDIA_IMAGE_EXT),
    "audio": list(config.MEDIA_AUDIO_EXT),
    "video": list(config.MEDIA_VIDEO_EXT),
}


def media_question_builder(*, key_prefix: str = "mq", quiz_id: str | None = None,
                           quiz_labels: dict[str, str] | None = None,
                           show_quiz_picker: bool = True,
                           allow_create_quiz: bool = False,
                           created_by: str = "") -> dict | None:
    """Shared admin/host form — returns question dict on submit, else None."""
    from core import bulk_import, storage

    create_new = False
    if allow_create_quiz:
        dest = st.radio(
            "Save to",
            ["Existing quiz", "Create new quiz"],
            horizontal=True,
            key=f"{key_prefix}_dest",
        )
        create_new = dest == "Create new quiz"
        if create_new:
            c1, c2 = st.columns([3, 1])
            new_title = c1.text_input("New quiz title", value="Media Quiz Pack", key=f"{key_prefix}_new_title")
            new_emoji = c2.selectbox("Emoji", ["🖼️", "🎬", "🎧", "📦", "🏦", "⚡"], key=f"{key_prefix}_new_emoji")
        elif show_quiz_picker and quiz_labels:
            target_label = st.selectbox("Add to quiz", list(quiz_labels.keys()), key=f"{key_prefix}_quiz")
            quiz_id = quiz_labels[target_label]
        elif not quiz_id:
            st.info("Pick **Create new quiz** or add a quiz from the Question Bank first.")
            return None
    elif show_quiz_picker and quiz_labels:
        target_label = st.selectbox("Add to quiz", list(quiz_labels.keys()), key=f"{key_prefix}_quiz")
        quiz_id = quiz_labels[target_label]
    elif not quiz_id:
        st.warning("No quiz selected.")
        return None

    qtype = st.radio("Question type", ["MCQ", "Subjective (voting round)"], horizontal=True,
                     key=f"{key_prefix}_qtype")
    media_kind = st.radio("Media attachment", ["None", "Image", "Audio", "Video"], horizontal=True,
                          key=f"{key_prefix}_mkind")
    uploaded = None
    if media_kind != "None":
        exts = _MEDIA_ACCEPT[media_kind.lower()]
        uploaded = st.file_uploader(
            f"Upload {media_kind.lower()}",
            type=[e.lstrip(".") for e in exts],
            key=f"{key_prefix}_upload",
            help=f"Max {config.MEDIA_MAX_BYTES // (1024 * 1024)} MB · "
                 f"{', '.join(exts)}",
        )
        if uploaded:
            st.caption(f"Selected: {uploaded.name} ({uploaded.size // 1024} KB)")

    with st.form(f"{key_prefix}_form", border=False):
        question = st.text_area(
            "Question prompt",
            height=80,
            placeholder="e.g. What acronym is shown in this slide? / Describe what you hear…",
        )
        opts = ["", "", "", ""]
        correct = "A"
        if qtype == "MCQ":
            c1, c2 = st.columns(2)
            opts[0] = c1.text_input("Option A")
            opts[1] = c2.text_input("Option B")
            opts[2] = c1.text_input("Option C")
            opts[3] = c2.text_input("Option D")
            correct = st.radio("Correct answer", ["A", "B", "C", "D"], horizontal=True)
        t1, t2 = st.columns(2)
        timer = t1.number_input(
            "Timer (seconds)", 10, 120,
            config.DEFAULT_TIMER_SEC if qtype == "MCQ" else config.SUBJECTIVE_TIMER_SEC,
        )
        points = t2.number_input("Points", 100, 5000, config.BASE_POINTS, step=100)
        add = st.form_submit_button("Add Question ➕", use_container_width=True)

    if not add:
        return None
    if not question.strip():
        st.error("Enter a question prompt.")
        return None
    if qtype == "MCQ" and not all(o.strip() for o in opts):
        st.error("Fill the question and all four MCQ options.")
        return None
    if media_kind != "None" and not uploaded:
        st.error(f"Upload an {media_kind.lower()} file or choose None.")
        return None

    if create_new:
        if not new_title.strip():
            st.error("Enter a title for the new quiz.")
            return None
        quiz_id = bulk_import.create_import_quiz(new_title.strip(), new_emoji, created_by or "admin")

    media_type, media_file = "", ""
    if uploaded:
        try:
            media_type, media_file = storage.save_question_media(
                quiz_id, uploaded.name, uploaded.getvalue())
        except ValueError as e:
            st.error(str(e))
            return None

    qtype_key = "mcq" if qtype == "MCQ" else "subjective"
    storage.add_question(
        quiz_id, question.strip(), opts, correct, int(timer), int(points),
        qtype=qtype_key, media_type=media_type, media_file=media_file,
    )
    return {
        "type": qtype_key,
        "question": question.strip(),
        "timer": int(timer),
        "points": int(points),
        "options": list(opts) if qtype_key == "mcq" else [],
        "correct": "ABCD".index(correct) if qtype_key == "mcq" else None,
        "quiz_id": quiz_id,
        **({"media_type": media_type, "media_file": media_file} if media_type else {}),
    }


_ANSWER_LABELS = ["A", "B", "C", "D"]
_ANSWER_GRADS = [
    "linear-gradient(135deg,#60a5fa,#2563eb)",
    "linear-gradient(135deg,#f472b6,#db2777)",
    "linear-gradient(135deg,#34d399,#059669)",
    "linear-gradient(135deg,#fbbf24,#d97706)",
]


def verdict(good: bool, title: str, sub: str, *,
            answer: str | None = None, answer_idx: int | None = None) -> None:
    cls = "good" if good else "bad"
    answer_html = ""
    if answer is not None:
        idx = answer_idx if answer_idx is not None else 0
        letter = _ANSWER_LABELS[idx % 4]
        grad = _ANSWER_GRADS[idx % 4]
        answer_html = (
            f'<div class="qt-verdict-answer">'
            f'<span class="qt-verdict-ans-tag">✓ Correct answer</span>'
            f'<div class="qt-verdict-ans-row">'
            f'<span class="qt-verdict-ans-letter" style="background:{grad}">{letter}</span>'
            f'<span class="qt-verdict-ans-text">{answer}</span>'
            f'</div></div>'
        )
    st.markdown(f'<div class="qt-verdict"><div class="big {cls}">{title}</div>'
                f'<div class="sub">{sub}</div>{answer_html}</div>', unsafe_allow_html=True)


def podium(board: list[dict]) -> None:
    """board = leaderboard rows (dicts with name/avatar/score), top 3 used."""
    if not board:
        return
    slots = []
    order = [(1, "p2", ""), (0, "p1", '<span class="crown">👑</span>'), (2, "p3", "")]
    for idx, cls, crown in order:
        if idx >= len(board):
            continue
        r = board[idx]
        slots.append(
            f'<div class="qt-step {cls}">{crown}<div class="av">{r["avatar"]}</div>'
            f'<div class="who">{r["name"]}</div><div class="pts">{r["score"]:,}</div>'
            f'<div class="blk">{idx + 1}</div></div>')
    st.markdown(f'<div class="qt-podium">{"".join(slots)}</div>', unsafe_allow_html=True)


def rank_rows(board: list[dict], me: str = "", start: int = 3, limit: int = 8) -> None:
    rows = []
    for i, r in enumerate(board[start:start + limit], start=start + 1):
        cls = "qt-row me" if r["name"] == me else "qt-row"
        team = f'<span class="tm">{r["team"]}</span>' if r.get("team") else ""
        rows.append(
            f'<div class="{cls}" style="animation-delay:{(i - start) * 0.08:.2f}s">'
            f'<span class="rk">#{i}</span><span class="em">{r["avatar"]}</span>'
            f'<span class="nm">{r["name"]}{team}</span><span class="pt">{r["score"]:,}</span></div>')
    st.markdown("".join(rows), unsafe_allow_html=True)


def team_rows(teams: list[dict], emj: dict[str, str] | None = None) -> None:
    medals = ["🥇", "🥈", "🥉"]
    rows = []
    for i, t in enumerate(teams):
        rank = medals[i] if i < 3 else f"#{i + 1}"
        icon = (emj or {}).get(t["team"], "🛡️")
        rows.append(
            f'<div class="qt-row" style="animation-delay:{i * 0.08:.2f}s">'
            f'<span class="rk">{rank}</span>'
            f'<span class="em">{icon}</span>'
            f'<span class="nm">{t["team"]}<span class="tm">{len(t["members"])} players · {t["votes"]} votes</span></span>'
            f'<span class="pt">{t["score"]:,}</span></div>')
    st.markdown(f'<div class="qt-team-results">{"".join(rows)}</div>', unsafe_allow_html=True)


def distribution_bars(counts: list[int], options: list[str], correct: int) -> None:
    labels = ["A", "B", "C", "D"]
    colors = [
        ("linear-gradient(135deg,#60a5fa,#2563eb)", "rgba(96,165,250,.25)"),
        ("linear-gradient(135deg,#f472b6,#db2777)", "rgba(244,114,182,.25)"),
        ("linear-gradient(135deg,#34d399,#059669)", "rgba(52,211,153,.25)"),
        ("linear-gradient(135deg,#fbbf24,#d97706)", "rgba(251,191,36,.25)"),
    ]
    total = max(sum(counts), 1)
    mx = max(max(counts), 1)
    html = ['<div class="qt-kbc-poll">']
    for i, (c, opt) in enumerate(zip(counts, options)):
        pct = int(100 * c / total)
        bar_w = max(4, int(100 * c / mx))
        is_win = i == correct
        bar_grad, bg_glow = colors[i % 4]
        glow_style = f"box-shadow:0 0 18px {bg_glow},0 0 40px {bg_glow};" if is_win else ""
        tick = "✓" if is_win else ""
        html.append(
            f'<div class="qt-kbc-row{" win" if is_win else ""}">'
            f'  <div class="qt-kbc-label" style="background:{bar_grad}">{labels[i]}</div>'
            f'  <div class="qt-kbc-track">'
            f'    <div class="qt-kbc-fill" style="width:{bar_w}%;background:{bar_grad};{glow_style}"></div>'
            f'    <span class="qt-kbc-opt">{opt[:32]}{" " + tick if tick else ""}</span>'
            f'  </div>'
            f'  <div class="qt-kbc-pct">{pct}%<br><span class="qt-kbc-cnt">({c})</span></div>'
            f'</div>'
        )
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def confetti(n: int = 90) -> None:
    colors = ["#0088ce", "#4db4ff", "#e21836", "#ffc233", "#00c9a7", "#ffffff", "#7c5cff"]
    bits = []
    rng = random.Random()
    for _ in range(n):
        bits.append(
            f'<div class="qt-cf" style="left:{rng.uniform(0, 100):.1f}vw;'
            f'width:{rng.uniform(7, 15):.0f}px;height:{rng.uniform(10, 20):.0f}px;'
            f'background:{rng.choice(colors)};animation-duration:{rng.uniform(2.6, 6):.1f}s;'
            f'animation-delay:{rng.uniform(0, 1.2):.1f}s"></div>')
    st.markdown("".join(bits), unsafe_allow_html=True)


def neon_divider() -> None:
    st.markdown('<div class="qt-neon-rule"></div>', unsafe_allow_html=True)


def section_heading(title: str) -> None:
    st.markdown(f'<div class="qt-section-h">{title}</div>', unsafe_allow_html=True)


def champion_banner(champ: dict) -> None:
    name = champ.get("name", "")
    avatar = champ.get("avatar", "🏆")
    st.markdown(
        f'<div class="qt-champ-hero qt-rise">'
        f'<div class="qt-champ-trophy">🏆</div>'
        f'<div class="qt-champ-headline">CHAMPION!</div>'
        f'<div class="qt-champ-spotlight">'
        f'<div class="qt-champ-glow"></div>'
        f'<span class="qt-champ-avatar">{avatar}</span>'
        f'<div class="qt-champ-identity">'
        f'<span class="qt-champ-name">{name}</span>'
        f'<span class="qt-champ-tagline">takes the crown</span>'
        f'</div>'
        f'<span class="qt-champ-crown" aria-hidden="true">👑</span>'
        f'</div></div>',
        unsafe_allow_html=True)


def awards_strip(awards: dict) -> None:
    chips = [f'<span class="qt-award" style="animation-delay:{i * 0.12:.2f}s">{title} · <b>{who}</b></span>'
             for i, (title, who) in enumerate(awards.items())]
    st.markdown(
        f'<div class="qt-awards-scroll"><div class="qt-awards-row">{"".join(chips)}</div></div>',
        unsafe_allow_html=True)


def kpi_card(col, number: str, label: str, spark: str = "", tone: str = "") -> None:
    sp = f'<span class="spark">{spark}</span>' if spark else ""
    col.markdown(f'<div class="qt-kpi {tone}"><div class="n">{number}</div>'
                 f'<div class="l">{label}</div>{sp}</div>', unsafe_allow_html=True)


def waiting_dots(text: str) -> None:
    st.markdown(f'<div class="qt-sub" style="text-align:center;margin-top:16px">{text}'
                '<div class="qt-dots"><span>●</span><span>●</span><span>●</span></div></div>',
                unsafe_allow_html=True)


def begin_exit_transition(exit_label: str = "logout") -> None:
    """Route through the neon exit overlay before clearing session and returning to login."""
    st.session_state["transition_mode"] = "exit"
    st.session_state["exit_label"] = exit_label
    st.session_state["dest_page"] = "login"
    st.session_state["page"] = "transition"


def page_settle(delay_ms: int = 400) -> bool:
    """First run after a page switch: complete a prune cycle, then rerun.

    Returns True when this run should stop early (settle in progress).
    """
    import streamlit.components.v1 as st_components
    if st.session_state.pop("_settle", False):
        st.button("·", key="qt_settle")
        st_components.html(
            "<script>setTimeout(function(){"
            "var b=window.parent.document.querySelector('div[class*=\"st-key-qt_settle\"] button');"
            "if(b) b.click();}, %d);</script>" % max(400, delay_ms),
            height=0)
        return True
    return False


def autorefresh(seconds: float = 1.0) -> None:
    """Poll the shared game state: sleep then rerun.

    On the first run after a page switch (app.py sets "_settle") the run must
    COMPLETE so Streamlit prunes the previous page's stale elements — so
    instead of sleeping, an invisible button (hidden via CSS, clicked by a JS
    timer) schedules the next rerun.
    """
    if page_settle(max(400, int(seconds * 1000))):
        return
    time.sleep(seconds)
    st.rerun()


_HUB_NAV_ITEMS = (
    ("join", "gamepad-2", "Join the game", "blue"),
    ("bots", "bot", "Play with bot", "violet"),
    ("learn", "book-open", "Learn business terms", "teal"),
    ("history", "clipboard-list", "My quiz history", "sky"),
    ("profile", "user", "Profile", "gold"),
    ("feedback", "message-square", "Feedback", "rose"),
)


def inject_hub_nav_icons(collapsed: bool = False) -> None:
    """Place coloured Lucide icons inside each hub nav button label row."""
    size = 22 if collapsed else 18
    items = {
        key: {"html": hub_nav_icon(icon, tone, size), "label": label}
        for key, icon, label, tone in _HUB_NAV_ITEMS
    }
    toggle = hub_nav_icon("menu", "slate", size)
    payload = json.dumps({"items": items, "toggle": toggle, "collapsed": collapsed})
    st.components.v1.html(
        f"<script>"
        f"(function(){{"
        f"var P=window.parent,doc=P.document,CFG={payload};"
        f"function innerHtml(iconHtml,label,showLabel){{"
        f"  var lbl=showLabel&&label?'<span class=\"qt-hub-nav-label\">'+label+'</span>':'';"
        f"  return '<span class=\"qt-hub-nav-inner\">'+iconHtml+lbl+'</span>';"
        f"}}"
        f"function paint(){{"
        f"  if(!doc.querySelector('.qt-hub-nav-col'))return;"
        f"  Object.keys(CFG.items).forEach(function(key){{"
        f"    var wrap=doc.querySelector('[class*=\"st-key-hub_nav_'+key+'\"]');"
        f"    if(!wrap)return;"
        f"    var btn=wrap.querySelector('button');"
        f"    var p=btn&&btn.querySelector('p');"
        f"    if(!p)return;"
        f"    var item=CFG.items[key];"
        f"    p.innerHTML=innerHtml(item.html,item.label,!CFG.collapsed);"
        f"    var ico=p.querySelector('.qt-hub-nav-ico');"
        f"    if(ico&&btn.getAttribute('kind')==='primary')ico.classList.add('is-active');"
        f"  }});"
        f"  var tw=doc.querySelector('[class*=\"st-key-hub_nav_toggle\"]');"
        f"  if(tw){{"
        f"    var tb=tw.querySelector('button');"
        f"    var tp=tb&&tb.querySelector('p');"
        f"    if(tp)tp.innerHTML=innerHtml(CFG.toggle,'',false);"
        f"  }}"
        f"}}"
        f"paint();"
        f"if(P.__qtHubNavIconJanitor)clearInterval(P.__qtHubNavIconJanitor);"
        f"P.__qtHubNavIconJanitor=setInterval(paint,400);"
        f"}})();"
        f"</script>",
        height=0,
    )


HUB_NAV_TOGGLE = "__toggle__"


def participant_hub_nav(active: str, avatar: str = "", nick: str = "",
                        collapsed: bool = False) -> str | None:
    """Left rail menu on the participant profile hub. Returns section key if
    changed, or HUB_NAV_TOGGLE when the collapse/expand control is pressed."""
    from html import escape
    scope = "qt-hub-nav-collapsed" if collapsed else "qt-hub-nav-open"
    st.markdown(f'<span class="qt-hub-nav-col {scope}"></span>', unsafe_allow_html=True)

    toggle_clicked = st.button("\u00a0", key="hub_nav_toggle", type="secondary",
                               use_container_width=True,
                               help="Open menu" if collapsed else "Collapse menu")

    if not collapsed:
        who = escape(f"{avatar} {nick}".strip())
        who_html = f'<div class="qt-hub-nav-who">{who}</div>' if who else ""
        st.markdown(
            f'<div class="qt-rail qt-hub-nav-rail">'
            f'<div class="qt-cat qt-hub-nav-title" style="text-align:left">'
            f'{hub_nav_icon("compass", "sky", 16)} ARENA MENU</div>'
            f'<div class="qt-sub" style="font-size:11.5px;margin-bottom:4px">Pick where to go</div>'
            f'{who_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    picked = None
    for key, _icon, label, _tone in _HUB_NAV_ITEMS:
        btn_type = "primary" if key == active else "secondary"
        if st.button("\u00a0", key=f"hub_nav_{key}", type=btn_type,
                     use_container_width=True, help=label):
            picked = key
    inject_hub_nav_icons(collapsed)
    if toggle_clicked:
        return HUB_NAV_TOGGLE
    return picked


def stats_rail(teams: list[dict], top3: list[dict], my_team: str = "", me: str = "") -> None:
    """Left rail on the participant screen: live team standings + top-3 players."""
    html = ['<div class="qt-rail qt-stats-rail">',
            '<div class="qt-cat" style="text-align:left">🏆 LIVE TEAM STANDINGS</div>']
    if teams:
        top = max(t["score"] for t in teams) or 1
        for t in teams[:3]:
            hl = ' style="color:#4db4ff"' if t["team"] == my_team else ""
            html.append(f'<div class="qt-rl"><span class="nm"{hl}>{t["team"]}</span>'
                        f'<span class="bar"><i style="width:{max(5, int(100 * t["score"] / top))}%"></i></span>'
                        f'<span class="pt">{t["score"]:,}</span></div>')
    else:
        html.append('<div class="qt-sub" style="font-size:12px;padding:4px 0">No teams this game</div>')
    html.append('<div class="qt-cat" style="text-align:left;margin-top:12px">⭐ TOP 3 PLAYERS</div>')
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(top3[:3]):
        hl = ' style="color:#4db4ff"' if r["name"] == me else ""
        html.append(f'<div class="qt-rl"><span class="em">{medals[i]} {r["avatar"]}</span>'
                    f'<span class="nm"{hl}>{r["name"]}</span><span class="pt">{r["score"]:,}</span></div>')
    html.append('<div class="qt-stats-rail-fill" aria-hidden="true"></div></div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def stats_rail_team_challenge(nick: str) -> None:
    """Compact team domain challenge banner under stats rail."""
    from core import domain_knowledge
    from html import escape
    terms = domain_knowledge.team_challenge_terms()
    pk = domain_knowledge.player_key(nick)
    prog = domain_knowledge.progress_for_player(pk)
    done = sum(1 for t in terms if prog.get(t) == "mastered")
    chips = " · ".join(escape(t) for t in terms)
    st.markdown(
        f'<div class="qt-rail qt-team-challenge qt-rise" style="margin-top:10px">'
        f'<div class="qt-cat" style="font-size:10px;text-align:left">🎯 TEAM DOMAIN CHALLENGE</div>'
        f'<div class="qt-sub" style="font-size:11.5px;line-height:1.45">Master: {chips}'
        f'<br><b style="color:#ffc233">{done}/{len(terms)}</b> done by you</div></div>',
        unsafe_allow_html=True)


def points_pop(points: int) -> None:
    """Floating +points animation on MCQ reveal (parent-realm)."""
    import streamlit.components.v1 as st_components
    st_components.html(
        f'<script>'
        f'(function(){{'
        f'var doc=window.parent.document;'
        f'var el=doc.createElement("div");'
        f'el.className="qt-points-pop";'
        f'el.textContent="+{int(points):,}";'
        f'doc.body.appendChild(el);'
        f'requestAnimationFrame(function(){{el.classList.add("show");}});'
        f'setTimeout(function(){{el.remove();}},1400);'
        f'}})();'
        f'</script>',
        height=0,
    )


def team_chat_rail(g: dict, nick: str) -> None:
    """Team-only chat wall + composer. Messages live in live_game.json and die
    with the game. column-reverse keeps the view glued to the newest message."""
    from html import escape
    from core import game as _game
    team = g["players"][nick]["team"]
    st.markdown('<div class="qt-cat qt-chat-head">💬 TEAM CHAT</div>', unsafe_allow_html=True)
    if not team:
        st.markdown('<div class="qt-rail qt-sub qt-chat-solo">You joined solo — '
                    'pick a team next game to unlock the private team chat 💬</div>',
                    unsafe_allow_html=True)
        return
    msgs = g.get("chat", {}).get(team, [])
    rows = [f'<div class="qt-msg{" me" if m["n"] == nick else ""}">'
            f'<span class="who">{m["av"]} {escape(m["n"])} · {m["ts"]}</span>'
            f'<span class="txt">{escape(m["t"])}</span></div>'
            for m in reversed(msgs)]
    if not rows:
        rows = ['<div class="qt-sub" style="font-size:12px;text-align:center;margin:auto">'
                f'Only <b style="color:#4db4ff">{escape(team)}</b> sees this room — say hi 👋</div>']
    st.markdown(f'<div class="qt-chatbox">{"".join(rows)}</div>', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True, border=False):
        c1, c2 = st.columns([4, 1.2])
        msg = c1.text_input("chat", label_visibility="collapsed", max_chars=200,
                            placeholder=f"Message {team}…")
        if c2.form_submit_button("➤", use_container_width=True) and msg.strip():
            _game.post_chat(nick, msg)
            st.rerun()


def countdown_popup(q_index: int, reveal_started: float, reveal_duration: float = 8.0) -> None:
    """Self-contained JS countdown (3→2→1→GO!) with sounds.

    Injects into window.parent once per question (deduplicated via
    window.parent.qtCdActive).  JS schedules all steps internally via
    setTimeout so there's zero gap between numbers and no dependency on
    Streamlit rerenders.  Each number plays a distinct Web Audio beep.

    Args:
        q_index: current question index (used as dedup key).
        reveal_started: Unix timestamp (time.time()) when REVEAL phase began.
        reveal_duration: total reveal phase length in seconds (default 8.0).
    """
    import time as _time
    if not reveal_started:
        reveal_started = _time.time()
    elapsed = _time.time() - reveal_started
    remaining = reveal_duration - elapsed
    if remaining < -1.5:
        return

    reveal_end_ms = int((reveal_started + reveal_duration) * 1000)

    st.components.v1.html(f"""
<script>
(function() {{
    // ── Dedup: only one countdown per question ──────────────────────────────
    var KEY = 'qtCdActive_{q_index}';
    var parWin = window.parent;
    if (parWin[KEY]) return;
    parWin[KEY] = true;
    Object.keys(parWin).forEach(function(k) {{
        if (k.indexOf('qtCdActive_') === 0 && k !== KEY) delete parWin[k];
    }});

    var par       = window.parent.document;
    var endMs     = {reveal_end_ms};
    var STEPS     = [
        {{ label:'3',   color:'#93c5fd', glow:'rgba(147,197,253,0.85)',  hz:[600],            sub:'NEXT QUESTION STARTS IN...' }},
        {{ label:'2',   color:'#3b82f6', glow:'rgba(59,130,246,0.85)',   hz:[740],            sub:'NEXT QUESTION STARTS IN...' }},
        {{ label:'1',   color:'#1e3a8a', glow:'rgba(30,58,138,0.85)',    hz:[880],            sub:'NEXT QUESTION STARTS IN...' }},
        {{ label:'GO!', color:'#22c55e', glow:'rgba(34,197,94,0.85)',    hz:[880,1100,1320],  sub:'GET READY!' }}
    ];

    // ── Inject shared styles once ───────────────────────────────────────────
    if (!par.getElementById('qt-cd-styles')) {{
        var sty = par.createElement('style');
        sty.id  = 'qt-cd-styles';
        sty.textContent =
            '@keyframes qtCdIn  {{from{{opacity:0}}to{{opacity:1}}}}' +
            '@keyframes qtCdPop {{0%{{transform:scale(0.35);opacity:0}}' +
            '45%{{transform:scale(1.18);opacity:1}}70%{{transform:scale(0.96)}}' +
            '100%{{transform:scale(1);opacity:1}}}}' +
            '@keyframes qtCdShrink {{to{{transform:scale(0.55);opacity:0}}}}' +
            '@keyframes qtCdOut {{to{{opacity:0;transform:scale(1.06)}}}}';
        par.head.appendChild(sty);
    }}

    var _root = null, _num = null, _sub = null;

    function ensureRoot() {{
        if (_root) return;
        _root = par.createElement('div');
        _root.id = 'qt-countdown-root';
        _root.style.cssText = 'position:fixed;inset:0;z-index:9999;pointer-events:none;' +
            'background:rgba(0,11,26,0.88);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);' +
            'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;' +
            'animation:qtCdIn 0.2s ease both';
        _num = par.createElement('div');
        _num.style.cssText = 'font-family:\\'Baloo 2\\',cursive;font-weight:900;line-height:1;' +
            'font-size:clamp(90px,16vw,172px);will-change:transform,opacity';
        _sub = par.createElement('div');
        _sub.style.cssText = 'font-family:\\'Poppins\\',sans-serif;font-size:15px;font-weight:700;' +
            'letter-spacing:5px;text-transform:uppercase;color:rgba(255,255,255,0.58);transition:opacity .15s ease';
        _root.appendChild(_num); _root.appendChild(_sub);
        par.body.appendChild(_root);
    }}

    // ── Audio helper (runs in iframe context) ──────────────────────────────
    var _actx = null;
    function getACtx() {{
        if (!_actx) {{
            try {{ _actx = new (window.AudioContext || window.webkitAudioContext)(); }} catch(e) {{}}
        }}
        return _actx;
    }}
    function playBeep(freqs) {{
        var ac = getACtx();
        if (!ac) return;
        try {{
            freqs.forEach(function(f, i) {{
                var osc  = ac.createOscillator();
                var gain = ac.createGain();
                osc.connect(gain); gain.connect(ac.destination);
                osc.type            = 'sine';
                osc.frequency.value = f;
                var t = ac.currentTime + i * 0.07;
                gain.gain.setValueAtTime(0.0, t);
                gain.gain.linearRampToValueAtTime(0.22, t + 0.012);
                gain.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
                osc.start(t); osc.stop(t + 0.2);
            }});
        }} catch(e) {{}}
    }}

    // ── Show one countdown step (persistent backdrop, swap number only) ─────
    function applyStep(step) {{
        _num.textContent = step.label;
        _num.style.color = step.color;
        _num.style.textShadow = '0 0 50px ' + step.glow + ',0 0 100px ' + step.glow + ',0 6px 0 rgba(0,0,0,0.5)';
        _sub.textContent = step.sub;
    }}

    function showStep(step, idx, total) {{
        playBeep(step.hz);
        ensureRoot();

        var isFirst = idx === 0;
        var isLast  = idx === total - 1;

        function popIn() {{
            _num.style.animation = 'none';
            _num.offsetHeight; // reflow
            _num.style.animation = 'qtCdPop 0.42s cubic-bezier(0.34,1.56,0.64,1) both';
            applyStep(step);
            _sub.style.opacity = '1';
        }}

        if (isFirst) {{
            popIn();
        }} else {{
            _sub.style.opacity = '0.35';
            _num.style.animation = 'qtCdShrink 0.16s ease forwards';
            setTimeout(popIn, 160);
        }}

        if (isLast) {{
            setTimeout(function() {{
                if (!_root) return;
                _root.style.animation = 'qtCdOut 0.28s ease forwards';
                setTimeout(function() {{
                    if (_root) {{ _root.remove(); _root = _num = _sub = null; }}
                }}, 280);
            }}, 720);
        }}
    }}

    // ── Schedule each step precisely (1 s apart, no per-step overlay teardown) ─
    var now = Date.now();
    var firstAt = endMs - 3000;
    STEPS.forEach(function(step, idx) {{
        var delay = firstAt + idx * 1000 - now;
        if (delay >= -800) {{
            setTimeout(function() {{ showStep(step, idx, STEPS.length); }}, Math.max(0, delay));
        }}
    }});

    // ── Cleanup flag after the whole sequence ───────────────────────────────
    setTimeout(function() {{ delete window.parent[KEY]; }}, endMs - now + 2000);
}})();
</script>
""", height=0)


def sound_effects() -> None:
    """Inject playful sound effects for participant interactions using Web Audio API."""
    st.components.v1.html("""
    <script>
    (function() {
        if (window.qtSoundsLoaded) return;
        window.qtSoundsLoaded = true;
        
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Playful hover sound (quick high beep - 60ms)
        function playHover() {
            try {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                
                osc.frequency.value = 900;
                osc.type = 'sine';
                gain.gain.setValueAtTime(0.08, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.06);
                
                osc.start(ctx.currentTime);
                osc.stop(ctx.currentTime + 0.06);
            } catch(e) {}
        }
        
        // Success click sound (cheerful 3-note ascending - 150ms total)
        function playClick() {
            try {
                [700, 850, 1000].forEach((freq, i) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    
                    osc.frequency.value = freq;
                    osc.type = 'sine';
                    const time = ctx.currentTime + (i * 0.045);
                    gain.gain.setValueAtTime(0.09, time);
                    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.06);
                    
                    osc.start(time);
                    osc.stop(time + 0.06);
                });
            } catch(e) {}
        }
        
        // Vote sound (cute pop - 80ms)
        function playVote() {
            try {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                
                osc.frequency.setValueAtTime(1200, ctx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(500, ctx.currentTime + 0.08);
                osc.type = 'sine';
                gain.gain.setValueAtTime(0.11, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);
                
                osc.start(ctx.currentTime);
                osc.stop(ctx.currentTime + 0.08);
            } catch(e) {}
        }
        
        // Avatar/Join sound (playful beep - 50ms)
        function playSelect() {
            try {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                
                osc.frequency.value = 750;
                osc.type = 'sine';
                gain.gain.setValueAtTime(0.1, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05);
                
                osc.start(ctx.currentTime);
                osc.stop(ctx.currentTime + 0.05);
            } catch(e) {}
        }
        
        // Attach to buttons with retry mechanism
        function attachSounds() {
            const allBtns = window.parent.document.querySelectorAll(`button[kind="secondary"], button[kind="primary"]`);
            allBtns.forEach(btn => {
                if (!btn.qtSoundAdded) {
                    const text = btn.textContent;
                    const parent = btn.closest('[data-testid="stButton"]');
                    const key = parent ? parent.className : '';
                    
                    // Answer buttons (MCQ options with shapes)
                    if (text.includes('▲') || text.includes('◆') || text.includes('●') || text.includes('■')) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('mouseenter', playHover);
                        btn.addEventListener('click', playClick);
                    }
                    // Avatar buttons (emoji buttons)
                    else if (key.includes('avat') || /^[🦊🐼🦁🐸🦄🐙🐯🦉🐨🐵🦖🐳]/.test(text)) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('mouseenter', playHover);
                        btn.addEventListener('click', playSelect);
                    }
                    // Join the Fun button
                    else if (text.includes('Join the Fun')) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('mouseenter', playHover);
                        btn.addEventListener('click', playClick);
                    }
                    // Submit answer button
                    else if (text.includes('Submit Answer')) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('mouseenter', playHover);
                        btn.addEventListener('click', playClick);
                    }
                    // Vote buttons
                    else if (text.includes('Vote for') || text.includes('🗳️')) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('mouseenter', playHover);
                        btn.addEventListener('click', playVote);
                    }
                    // Learn panel / Got it
                    else if (text.includes('Got it') || text.includes('Mark viewed') || key.includes('learn_')) {
                        btn.qtSoundAdded = true;
                        btn.addEventListener('click', playClick);
                    }
                }
            });
            // Domain guide FAB + tree expand clicks
            window.parent.document.querySelectorAll('.qt-learn-fab, .qt-tree-summary').forEach(el => {
                if (!el.qtSoundAdded) {
                    el.qtSoundAdded = true;
                    el.addEventListener('click', playSelect);
                }
            });
        }
        
        // Keep checking for new buttons (Streamlit rerenders)
        attachSounds();
        const interval = setInterval(attachSounds, 400);
        
        // Cleanup after 5 minutes to prevent memory leaks
        setTimeout(() => clearInterval(interval), 300000);
    })();
    </script>
    """, height=0)



