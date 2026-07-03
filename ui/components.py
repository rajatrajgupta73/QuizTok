"""Reusable HTML components rendered with st.markdown (all offline)."""
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


def topbar(*pills_html: str) -> None:
    pills = "".join(pills_html)
    st.markdown(
        f'<div class="qt-topbar"><span class="qt-brand">QuizTok</span>'
        f'<span class="qt-div"></span>{citi_logo()}<span class="qt-spacer"></span>{pills}</div>',
        unsafe_allow_html=True)


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


def hud(q_no: int, q_total: int, streak: int, score: int) -> None:
    pct = int(100 * q_no / q_total)
    st.markdown(
        f'<div class="qt-hud"><span class="qno">Q{q_no} / {q_total}</span>'
        f'<span class="bar"><i style="width:{pct}%"></i></span>'
        f'<span class="qt-streak"><span class="fl">🔥</span>{streak} streak</span>'
        f'<span class="qt-score">⭐ <b>{score:,}</b></span></div>', unsafe_allow_html=True)


def timer_ring(seconds_left: float, total: int) -> None:
    r, circ = 38, 2 * 3.14159 * 38
    frac = max(0.0, min(1.0, seconds_left / total)) if total else 0
    color = "#e21836" if seconds_left <= 5 else "#4db4ff"
    danger = "danger" if seconds_left <= 5 else ""
    st.markdown(
        f'<div class="qt-timerwrap"><div class="qt-timer {danger}">'
        f'<svg width="86" height="86"><circle cx="43" cy="43" r="{r}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="7"/>'
        f'<circle cx="43" cy="43" r="{r}" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" '
        f'stroke-dasharray="{circ:.0f}" stroke-dashoffset="{circ * (1 - frac):.0f}"/></svg>'
        f'<span class="num">{int(seconds_left)}</span></div></div>', unsafe_allow_html=True)


def question_text(category: str, text: str) -> None:
    st.markdown(f'<div class="qt-cat">{category}</div>'
                f'<div class="qt-question">{text}</div>', unsafe_allow_html=True)


def verdict(good: bool, title: str, sub: str) -> None:
    cls = "good" if good else "bad"
    st.markdown(f'<div class="qt-verdict"><div class="big {cls}">{title}</div>'
                f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)


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


def team_rows(teams: list[dict]) -> None:
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️", "🎖️"]
    rows = []
    for i, t in enumerate(teams):
        rows.append(
            f'<div class="qt-row" style="animation-delay:{i * 0.08:.2f}s">'
            f'<span class="em">{medals[min(i, 5)]}</span>'
            f'<span class="nm">{t["team"]}<span class="tm">{len(t["members"])} players · {t["votes"]} votes</span></span>'
            f'<span class="pt">{t["score"]:,}</span></div>')
    st.markdown("".join(rows), unsafe_allow_html=True)


def distribution_bars(counts: list[int], options: list[str], correct: int) -> None:
    colors = ["linear-gradient(180deg,#4db4ff,#0088ce)", "linear-gradient(180deg,#ff5d73,#e21836)",
              "linear-gradient(180deg,#3fe0c5,#00c9a7)", "linear-gradient(180deg,#ffc46e,#ff9d2e)"]
    mx = max(max(counts), 1)
    cols = []
    for i, (c, opt) in enumerate(zip(counts, options)):
        h = int(20 + 130 * c / mx)
        win = "win" if i == correct else ""
        tick = " ✓" if i == correct else ""
        cols.append(
            f'<div class="qt-barcol {win}"><div class="qt-bar" style="height:{h}px;background:{colors[i]}">{c}</div>'
            f'<span class="lb">{opt[:26]}{tick}</span></div>')
    st.markdown(f'<div class="qt-bars">{"".join(cols)}</div>', unsafe_allow_html=True)


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


def awards_strip(awards: dict) -> None:
    chips = [f'<span class="qt-award" style="animation-delay:{i * 0.15:.2f}s">{title} · <b>{who}</b></span>'
             for i, (title, who) in enumerate(awards.items())]
    st.markdown("".join(chips), unsafe_allow_html=True)


def kpi_card(col, number: str, label: str) -> None:
    col.markdown(f'<div class="qt-kpi"><div class="n">{number}</div><div class="l">{label}</div></div>',
                 unsafe_allow_html=True)


def autorefresh(seconds: float = 1.0) -> None:
    """Poll the shared game state: sleep then rerun."""
    time.sleep(seconds)
    st.rerun()
