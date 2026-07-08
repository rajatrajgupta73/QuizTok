"""Participant profile hub — play options + banking domain academy (pre-game home)."""
import streamlit as st

import config
from core import game, logger, participant_report, storage
from ui import components as ui
from ui import learn_panel


def _team_options() -> list[str]:
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

_SECTION_BLURBS = {
    "join": "Enter the host's PIN and pick your team to jump into a live battle.",
    "bots": "Practice solo against bots — pick a quiz and difficulty.",
    "learn": "Explore banking paths, glossary terms, and track your mastery.",
    "history": "Review past quizzes, see how you scored, and download study guides.",
    "profile": "Update your avatar, name, and nickname for the arena.",
    "feedback": "Tell us what to improve — content, UX, animations, and more.",
}


def render() -> None:
    nick = st.session_state.get("nick", "")
    full_name = st.session_state.get("full_name", nick)
    avatar = st.session_state.get("avatar", "🦊")
    if st.session_state.get("role") != "participant" or not nick:
        st.session_state.page = "login"
        st.rerun()
        return

    g = game.load()
    if g and nick in g.get("players", {}):
        if g["status"] == "LOBBY":
            st.session_state.page = "lobby"
            st.rerun()
        elif g["status"] not in ("FINISHED",):
            st.session_state.page = "quiz"
            st.rerun()

    st.markdown('<span class="qt-hub-scope"></span>', unsafe_allow_html=True)
    ui.sound_effects()

    if ui.page_header(
        ui.pill(f"{avatar} {nick}"),
        ui.pill("Your profile", live_dot=True),
        logout_label="Logout",
        logout_key="hub_logout",
    ):
        ui.begin_exit_transition("logout")
        st.rerun()

    section = st.session_state.get("hub_section", "join")
    if section not in _SECTION_BLURBS:
        section = st.session_state["hub_section"] = "join"
    collapsed = st.session_state.get("hub_nav_collapsed", True)
    ratio = [0.4, 4.0] if collapsed else [1.55, 2.45]
    nav_l, main = st.columns(ratio, gap="medium")

    with nav_l:
        picked = ui.participant_hub_nav(section, avatar, nick, collapsed=collapsed)
        if picked == ui.HUB_NAV_TOGGLE:
            st.session_state.hub_nav_collapsed = not collapsed
            st.rerun()
        elif picked and picked != section:
            st.session_state.hub_section = picked
            st.rerun()

    with main:
        st.markdown('<span class="qt-hub-main-col"></span>', unsafe_allow_html=True)
        welcome = nick if nick != full_name else nick.split()[0]
        name_note = (
            f'<span style="color:#7a94b0;font-size:13px"> ({full_name})</span>'
            if nick != full_name else ""
        )
        st.markdown(
            f'<div class="qt-h1" style="font-size:28px;margin-bottom:4px">Welcome, {welcome}!{name_note}</div>'
            f'<div class="qt-sub" style="margin-bottom:18px">{_SECTION_BLURBS.get(section, "")}</div>',
            unsafe_allow_html=True,
        )

        if section == "join":
            _render_join(nick, avatar)
        elif section == "bots":
            _render_bots(nick, avatar)
        elif section == "learn":
            learn_panel.domain_academy_learn(nick, page="hub")
        elif section == "history":
            _render_history(nick)
        elif section == "profile":
            _profile_strip(nick, avatar, full_name)
        elif section == "feedback":
            learn_panel.render_feedback_panel(nick, page="hub")


def _render_join(nick: str, avatar: str) -> None:
    st.markdown('<span class="qt-hub-join-active"></span>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-card qt-rise qt-hub-join-card">'
        '<div class="qt-h3" style="margin-bottom:6px">🎮 Join live game</div>'
        '<div class="qt-sub" style="margin-bottom:4px">Enter the game PIN from your host, select your team, '
        'and tap join when you are ready.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.form("hub_join", border=False):
        pin = st.text_input("GAME PIN", max_chars=6, placeholder="••••••", key="pinbox")
        team_opts = _team_options()
        p_team = st.selectbox("SELECT TEAM", team_opts, key="hub_team")
        join = st.form_submit_button("Join the Fun 🚀", use_container_width=True)
    if join:
        if len(pin.strip()) < 4:
            st.error("Enter the game PIN from your host.")
        else:
            team = "" if p_team == "Solo" else p_team
            ok, result = game.join(pin, nick, avatar, team, "")
            if ok:
                st.session_state.update(nick=result, team=team, page="lobby")
                st.rerun()
            else:
                st.error(result)


def _render_bots(nick: str, avatar: str) -> None:
    st.markdown('<div class="qt-h3">🤖 Play vs bots</div>', unsafe_allow_html=True)
    cat = st.selectbox("QUIZ TYPE", _quiz_categories(), key="hub_quiz_cat")
    filtered = _quiz_options(cat)
    quiz_opts = _quiz_options()
    with st.form("hub_solo", border=False):
        if not filtered:
            st.warning("No quizzes in this category yet.")
            quiz_labels, quiz_ids = ["—"], [""]
        else:
            quiz_labels = [label for label, _ in filtered]
            quiz_ids = [qid for _, qid in filtered]
        quiz_pick = st.selectbox("CHOOSE QUIZ", quiz_labels, key="hub_quiz_pick")
        bot_preset = st.selectbox(
            "BOT DIFFICULTY", list(_BOT_PRESETS.keys()), key="hub_bot_preset")
        solo_go = st.form_submit_button("Start Solo Battle 🤖", use_container_width=True)
    if solo_go:
        if not quiz_opts:
            st.error("No quizzes available yet — ask your admin to create one.")
        elif not filtered:
            st.error("Pick a quiz type that has at least one quiz.")
        else:
            quiz_id = quiz_ids[quiz_labels.index(quiz_pick)]
            bot_count = _BOT_PRESETS[bot_preset]
            ok, result = game.start_solo_demo(nick, avatar, quiz_id, bot_count=bot_count)
            if ok:
                st.session_state.update(nick=result, page="quiz")
                st.rerun()
            else:
                st.error(result)


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(None, 1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _profile_names(full_name: str, nick: str) -> tuple[str, str, str]:
    first = st.session_state.get("first_name", "")
    last = st.session_state.get("last_name", "")
    if not first and not last:
        first, last = _split_full_name(full_name or nick)
    funky = nick if full_name and nick != full_name else ""
    return first, last, funky


def _render_history(nick: str) -> None:
    st.markdown('<div class="qt-h3">📚 My quiz history</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-sub" style="margin-bottom:14px">Revisit past games, see how you did on each '
        'question, and download a study guide to learn offline.</div>',
        unsafe_allow_html=True,
    )

    dismissed = st.session_state.get("dismissed_live_games", set())
    live_report = None

    # If a finished game is still in memory, offer immediate review first
    g = game.load()
    show_live = (
        g and g.get("status") == "FINISHED" and nick in g.get("players", {})
        and g.get("game_id") not in dismissed
    )
    if show_live:
        live_report = participant_report.build_report_from_game(g, nick)
        if live_report:
            st.info(f'🆕 Just finished: **{g.get("quiz_title", "Quiz")}** — review below or in your history.')
            with st.expander("Latest game — question review & download", expanded=False):
                ui.performance_review_panel(live_report, key_prefix="hub_live_perf")
                if st.button("Remove from history", key="hist_dismiss_live", use_container_width=True):
                    gid = g.get("game_id")
                    if gid:
                        storage.clear_player_history(nick, str(gid))
                        dismissed = set(dismissed) | {gid}
                        st.session_state["dismissed_live_games"] = dismissed
                        logger.log(nick, "participant", "history_cleared", f"game={gid}")
                    st.toast("Latest game removed from your history.")
                    st.rerun()

    history = participant_report.player_game_history(nick)
    has_saved = bool(history)
    has_live = live_report is not None

    if has_saved:
        head_l, head_r = st.columns([2.2, 1])
        head_l.markdown(f'<div class="qt-cat">{len(history)} PAST GAME(S)</div>',
                        unsafe_allow_html=True)
        with head_r:
            if st.button("🗑️ Clear all history", key="hist_clear_all_btn", use_container_width=True):
                st.session_state["confirm_clear_history"] = True

        if st.session_state.get("confirm_clear_history"):
            st.markdown(
                '<div class="qt-card" style="padding:14px 16px;margin:10px 0;border-color:rgba(226,24,54,.35)">'
                '<div class="qt-sub" style="margin-bottom:10px">This permanently deletes <b>your</b> saved '
                'scores and question reviews from Excel. Other players and admin reports are not affected.</div></div>',
                unsafe_allow_html=True,
            )
            sure = st.checkbox("I understand — clear my entire quiz history", key="hist_clear_sure")
            c1, c2 = st.columns(2)
            if c1.button("Yes, clear everything", key="hist_clear_yes", disabled=not sure,
                         use_container_width=True):
                n_s, n_a = storage.clear_player_history(nick)
                st.session_state.pop("confirm_clear_history", None)
                st.session_state.pop("hist_clear_sure", None)
                if g and g.get("game_id"):
                    st.session_state["dismissed_live_games"] = set(dismissed) | {g["game_id"]}
                logger.log(nick, "participant", "history_cleared_all", f"scores={n_s} answers={n_a}")
                st.success("Your quiz history has been cleared.")
                st.rerun()
            if c2.button("Cancel", key="hist_clear_no", use_container_width=True):
                st.session_state.pop("confirm_clear_history", None)
                st.rerun()

        for i, row in enumerate(history):
            team = f' · {row["team"]}' if row.get("team") else ""
            label = (f'{row["quiz_title"]} · {row["played_at"]} · '
                     f'#{row["rank"]} · {row["score"]:,} pts{team}')
            with st.expander(label, expanded=(i == 0 and not show_live)):
                report = participant_report.build_report_from_history(row["game_id"], nick)
                if report:
                    ui.performance_review_panel(report, key_prefix=f"hub_hist_{i}")
                else:
                    st.warning("Could not load details for this game.")
                if st.button("Remove this game", key=f"hist_del_{row['game_id']}", use_container_width=True):
                    storage.clear_player_history(nick, row["game_id"])
                    logger.log(nick, "participant", "history_cleared", f"game={row['game_id']}")
                    st.toast("Game removed from your history.")
                    st.rerun()
    elif not has_live:
        st.info("No completed games yet — join a live quiz or play vs bots to build your history.")


def _profile_strip(nick: str, avatar: str, full_name: str = "") -> None:
    st.markdown('<div class="qt-h3">🎭 Your profile</div>', unsafe_allow_html=True)
    grid = st.columns(6)
    for i, av in enumerate(config.AVATARS):
        sel = "✓" if avatar == av else ""
        if grid[i % 6].button(f"{av}{sel}", key=f"hub_avat{i}", use_container_width=True):
            st.session_state.avatar = av
            st.rerun()

    first, last, funky = _profile_names(full_name, nick)
    st.markdown('<div class="qt-h3" style="margin-top:18px;font-size:17px">✏️ Your name</div>',
                unsafe_allow_html=True)
    with st.form("hub_profile", border=False):
        n1, n2 = st.columns(2)
        p_first = n1.text_input("FIRST NAME", value=first, max_chars=20, placeholder="e.g. Rahul")
        p_last = n2.text_input("LAST NAME", value=last, max_chars=20, placeholder="e.g. Sharma")
        p_nick = st.text_input(
            "NICKNAME (optional)",
            value=funky,
            max_chars=24,
            placeholder="e.g. QuizZapper, Ops Ninja…",
        )
        save = st.form_submit_button("Save profile ✓", use_container_width=True)
    if save:
        if not p_first.strip() or not p_last.strip():
            st.error("First and last name are required.")
        else:
            formatted_name = f"{p_first.strip().title()} {p_last.strip().title()}"
            display = p_nick.strip() if p_nick.strip() else formatted_name
            st.session_state.update(
                first_name=p_first.strip().title(),
                last_name=p_last.strip().title(),
                full_name=formatted_name,
                nick=display,
            )
            st.success("Profile updated!")
            st.rerun()

    tag = f'Playing as <b style="color:#4db4ff">{nick}</b>'
    if full_name and full_name != nick:
        tag += f' · {full_name}'
    st.markdown(
        f'<div class="qt-mestrip">'
        f'<span class="av">{avatar}</span>'
        f'<span><span class="name">{nick}</span><br>'
        f'<span class="tag">{tag}</span></span>'
        f'<span class="ready">{ui.pill("PROFILE", live_dot=True)}</span></div>',
        unsafe_allow_html=True,
    )
