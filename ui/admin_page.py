"""Admin Command Center — dashboard, quiz library, 2000-question bank, builder, teams."""
import streamlit as st
import pandas as pd

import config
from core import bulk_import, domain_knowledge, feedback, game, logger, question_bank, storage
from ui import components as ui

_ADMIN_TABS = [
    "📊 Dashboard",
    "📚 Quiz Library",
    "🏦 Question Bank (2000)",
    "📖 Domain Academy",
    "💬 Feedback",
    "✏️ Media Question Builder",
    "📦 Excel + Image Import",
    "🏆 Teams",
]
_LIBRARY_TAB = 1


def _push_to_quiz_library(quiz_id: str, detail: str) -> None:
    """Mark quiz READY and jump to the Quiz Library tab."""
    storage.mark_quiz_ready(quiz_id)
    row = storage.get_quiz_row(quiz_id)
    n = storage.question_count(quiz_id)
    if row:
        title = f'{row["emoji"]} {row["title"]}'
        st.session_state["library_flash"] = (
            f'**{title}** is now in the Quiz Library — **{n}** question(s). {detail}')
    else:
        st.session_state["library_flash"] = detail
    st.session_state["library_highlight"] = str(quiz_id)
    st.session_state["admin_tab"] = _LIBRARY_TAB


def _admin_tab_nav() -> None:
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = 0
    cols = st.columns(len(_ADMIN_TABS))
    for i, label in enumerate(_ADMIN_TABS):
        if cols[i].button(
            label,
            key=f"adm_tab_{i}",
            use_container_width=True,
            type="primary" if i == st.session_state.admin_tab else "secondary",
        ):
            st.session_state.admin_tab = i
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)


def render() -> None:
    email = st.session_state.get("admin_email", "admin")
    role = st.session_state.get("role", "admin")
    role_pill = ui.pill("HOST", red=False) if role == "host" else ui.pill("ADMIN", red=True)
    if ui.page_header(role_pill, ui.pill(f'👩‍💼 {email}'), logout_key="admin_logout"):
        ui.begin_exit_transition("logout")
        st.rerun()

    st.markdown(f'<div class="qt-h1" style="font-family:\'Baloo 2\',cursive;font-size:30px;'
                f'font-weight:800">Command Center 🎛️</div>'
                f'<div class="qt-sub">Welcome back, {st.session_state.get("admin_name", "Admin")}! '
                f'Build quizzes from the bank, host live games, and export everything to Excel.</div>',
                unsafe_allow_html=True)

    live = game.load()
    if live and live["status"] not in ("FINISHED",):
        st.info(f'🔴 A game is LIVE right now — PIN **{live["pin"]}** · {live["quiz_title"]} · '
                f'{len(live["players"])} players')
        if st.button("Open Host Controls 🎛️", key="gold_host"):
            st.session_state.page = "host"
            st.rerun()

    _admin_tab_nav()
    tab = st.session_state.get("admin_tab", 0)
    if tab == 0:
        _dashboard()
    elif tab == 1:
        _quiz_library(email)
    elif tab == 2:
        _question_bank(email)
    elif tab == 3:
        _domain_academy(email)
    elif tab == 4:
        _feedback_inbox(email)
    elif tab == 5:
        _question_builder(email)
    elif tab == 6:
        _bulk_import(email)
    else:
        _teams(email)


# ---------------- Dashboard ----------------

def _dashboard() -> None:
    k = storage.get_kpis()
    bank = question_bank.load_bank()
    c1, c2, c3, c4 = st.columns(4)
    ui.kpi_card(c1, str(k["games_hosted"]), "GAMES HOSTED", spark="🎪")
    ui.kpi_card(c2, str(k["total_players"]), "HUMAN PLAYERS", spark="👥", tone="gold")
    ui.kpi_card(c3, k["avg_accuracy"], "AVG ACCURACY", spark="⚡", tone="teal")
    ui.kpi_card(c4, f"{len(bank):,}", "QUESTIONS IN BANK", spark="🎉", tone="pink")

    st.markdown('<div class="qt-cat" style="margin-top:18px">BANK COVERAGE BY CATEGORY</div>',
                unsafe_allow_html=True)
    counts = bank.groupby("category").size().sort_values(ascending=False)
    for cat, n in counts.items():
        st.markdown(
            f'<div class="qt-row"><span class="nm">{cat}</span>'
            f'<span class="bar" style="flex:2;height:10px;background:rgba(0,0,0,.35);border-radius:99px;overflow:hidden">'
            f'<i style="display:block;height:100%;width:{int(100 * n / counts.max())}%;'
            f'background:linear-gradient(90deg,#0088ce,#4db4ff);border-radius:99px"></i></span>'
            f'<span class="pt">{n}</span></div>', unsafe_allow_html=True)


# ---------------- Quiz Library ----------------

def _quiz_library(email: str) -> None:
    flash = st.session_state.pop("library_flash", None)
    highlight = st.session_state.pop("library_highlight", None)
    if flash:
        st.success(f"📚 {flash}")

    quizzes = storage.get_quizzes()
    if quizzes.empty:
        st.info("No quizzes yet — build one from the Question Bank tab!")
        return

    bots = st.toggle("Add demo bots 🤖 (fills the lobby for small groups)", value=False)
    live = game.load()
    thumbs = ["linear-gradient(135deg,#0088ce,#005a9e)", "linear-gradient(135deg,#e21836,#a80f26)",
              "linear-gradient(135deg,#00c9a7,#00806a)", "linear-gradient(135deg,#7c5cff,#4b32b4)"]
    qdf = storage.read_sheet(config.QUIZZES_XLSX, "questions")
    for i, (_, row) in enumerate(quizzes.iloc[::-1].iterrows()):
        n_q = int((qdf["quiz_id"].astype(str) == str(row["quiz_id"])).sum())
        is_live = bool(live and live["status"] != "FINISHED"
                       and str(live.get("quiz_id", "")) == str(row["quiz_id"]))
        status = '<span class="qt-status live">● LIVE NOW</span>' if is_live \
            else '<span class="qt-status ready">READY</span>' if n_q else \
            '<span class="qt-status draft">DRAFT</span>'
        hl = str(row["quiz_id"]) == str(highlight) if highlight else False
        if hl:
            st.markdown(
                f'<div class="qt-card" style="padding:10px 14px;margin:8px 0;border:2px solid #4db4ff;'
                f'background:rgba(0,136,206,.12)">✨ <b>Just added</b> — ready to host below</div>',
                unsafe_allow_html=True,
            )
        col1, col2, col3 = st.columns([4, 0.9, 0.9])
        col1.markdown(
            f'<div class="qt-quizrow">'
            f'<span class="thumb" style="background:{thumbs[i % 4]}">{row["emoji"]}</span>'
            f'<span><span class="ttl">{row["title"]}</span><br>'
            f'<span class="mt">{n_q} Qs · {row["category"]} · by {row["created_by"]}</span></span>'
            f'{status}</div>', unsafe_allow_html=True)
        if col2.button("Host 🎛️", key=f'host_{row["quiz_id"]}', use_container_width=True):
            try:
                game.create_game(str(row["quiz_id"]), email, with_bots=bots)
                st.session_state.page = "host"
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        if col3.button("🗑️ Delete", key=f'red_del_{row["quiz_id"]}',
                       use_container_width=True, disabled=is_live,
                       help="Can't delete while live" if is_live else "Remove quiz + its questions"):
            storage.delete_quiz(str(row["quiz_id"]))
            logger.log(email, "admin", "quiz_deleted", str(row["quiz_id"]))
            st.toast(f'Quiz "{row["title"]}" deleted 🗑️')
            st.rerun()

        with st.expander(f'👁️ View details — {row["title"]}'):
            sub = qdf[qdf["quiz_id"].astype(str) == str(row["quiz_id"])].sort_values("q_index")
            st.markdown(
                f'<div class="qt-sub" style="font-size:12.5px;margin-bottom:8px">'
                f'{row["emoji"]} <b style="color:#eef5ff">{row["title"]}</b> · {row["category"]} · '
                f'{len(sub)} questions · created by {row["created_by"]} on {row["created_at"]}</div>',
                unsafe_allow_html=True)
            for j, (_, q) in enumerate(sub.iterrows(), 1):
                tmr = int(q["timer_sec"]) if pd.notna(q["timer_sec"]) else config.DEFAULT_TIMER_SEC
                pts = int(q["points"]) if pd.notna(q["points"]) else config.BASE_POINTS
                if str(q["qtype"]).strip() == "subjective":
                    body = "🗳️ Subjective — answered in free text, scored by votes"
                else:
                    correct = str(q["correct"]).strip().upper()[:1]
                    body = " &nbsp;·&nbsp; ".join(
                        f'<b style="color:#00c9a7">{L}. {q["opt_" + L.lower()]} ✓</b>'
                        if L == correct else f'{L}. {q["opt_" + L.lower()]}'
                        for L in "ABCD")
                media_note = ""
                if "media_type" in q.index and pd.notna(q["media_type"]) and str(q["media_type"]).strip():
                    mt = str(q["media_type"]).strip().lower()
                    icon = {"image": "🖼️", "audio": "🎧", "video": "🎬"}.get(mt, "📎")
                    media_note = f' <span style="font-size:11px;color:#ffc233">{icon} {mt} round</span>'
                st.markdown(
                    f'<div class="qt-sub" style="font-size:12.5px;margin:6px 0 2px">'
                    f'<b style="color:#eef5ff">Q{j}.</b> {q["question"]}{media_note} '
                    f'<span style="font-size:11px">({tmr}s · {pts} pts)</span><br>'
                    f'<span style="font-size:11.5px">{body}</span></div>', unsafe_allow_html=True)


# ---------------- Question Bank ----------------

def _question_bank(email: str) -> None:
    bank = question_bank.load_bank()
    st.markdown(f'<div class="qt-sub">The full library lives in '
                f'<b style="color:#4db4ff">data/question_bank.xlsx</b> — {len(bank):,} questions, '
                f'editable directly in Excel.</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    cats = f1.multiselect("Categories", question_bank.CATEGORIES,
                          default=[question_bank.CAT_KPI, question_bank.CAT_IVR])
    diffs = f2.multiselect("Difficulty", ["easy", "medium", "hard"], default=[])
    search = f3.text_input("Search text", placeholder="e.g. FCR, chargeback, RAG…")

    view = bank
    if cats:
        view = view[view["category"].isin(cats + [question_bank.CAT_SUBJ])]
    if diffs:
        view = view[view["difficulty"].isin(diffs) | (view["qtype"] == "subjective")]
    if search.strip():
        view = view[view["question"].str.contains(search.strip(), case=False, na=False)]

    st.markdown(ui.pill(f"{len(view):,} matching questions") + " " +
                ui.pill(f'{(view["qtype"] == "subjective").sum()} subjective'), unsafe_allow_html=True)
    st.dataframe(view[["qid", "category", "difficulty", "qtype", "question", "correct"]],
                 use_container_width=True, height=280, hide_index=True)

    st.markdown('<div class="qt-cat" style="margin-top:10px">🎪 BUILD A QUIZ FROM THIS SELECTION</div>',
                unsafe_allow_html=True)
    with st.form("bank_quiz", border=False):
        b1, b2, b3, b4 = st.columns([2, 1, 1, 1])
        title = b1.text_input("Quiz title", value="Banking Ops Battle")
        emoji = b2.selectbox("Emoji", ["🏦", "🎬", "💼", "🧩", "🎵", "⚡", "🤖"])
        n_q = b3.number_input("Total questions", 3, 30, 10)
        mode = b4.selectbox("Game mode", list(config.QUIZ_MODE_PRESETS.keys()),
                            format_func=lambda k: config.QUIZ_MODE_PRESETS[k]["label"])
        if mode == "standard":
            n_subj = st.number_input("Subjective (vote) rounds", 0, 5, 2)
        else:
            n_subj = config.QUIZ_MODE_PRESETS[mode].get("subjective", 0)
            st.caption(f"{int(n_subj)} subjective rounds (preset)")
        build = st.form_submit_button("Create Quiz from Bank ➕", use_container_width=True)
    if build:
        if mode in ("acronym_blitz", "scenario_showdown", "mastery_match"):
            quiz_id = domain_knowledge.build_quiz_with_mode(
                title, emoji, cats or question_bank.CATEGORIES, diffs, int(n_q), mode, email)
        else:
            quiz_id = question_bank.build_quiz_from_bank(
                title, emoji, cats or question_bank.CATEGORIES, diffs, int(n_q), int(n_subj), email)
        logger.log(email, "admin", "quiz_built_from_bank", f'{quiz_id} mode={mode} n={n_q}')
        st.success(f'Quiz "{title}" created — find it in the Quiz Library! 🎉')


# ---------------- Question Builder ----------------

def _question_builder(email: str) -> None:
    st.markdown(
        '<div class="qt-sub">Attach an <b style="color:#ffc233">image</b>, '
        '<b style="color:#4db4ff">audio clip</b>, or <b style="color:#00c9a7">video</b> '
        'to any MCQ or subjective round — saved straight to the Quiz Library when you add.</div>',
        unsafe_allow_html=True,
    )
    quizzes = storage.get_quizzes()
    labels = {f'{r["emoji"]} {r["title"]}': str(r["quiz_id"]) for _, r in quizzes.iterrows()} if not quizzes.empty else {}
    live = game.load()
    if live and live["status"] == "LOBBY" and live["host"] == email:
        st.info(f'🔴 Live lobby PIN **{live["pin"]}** — new questions are saved to the quiz '
                f'and appended to this game instantly.')

    q = ui.media_question_builder(
        key_prefix="admin_mq",
        quiz_labels=labels or None,
        show_quiz_picker=bool(labels),
        allow_create_quiz=True,
        created_by=email,
    )
    if q:
        quiz_id = q.pop("quiz_id", "")
        if live and live["status"] == "LOBBY" and live["host"] == email \
                and str(live.get("quiz_id", "")) == str(quiz_id):
            game.append_question_in_lobby(email, q)
            logger.log(email, "admin", "question_added",
                       f'quiz={quiz_id} media={q.get("media_type", "")} live=1')
        else:
            logger.log(email, "admin", "question_added",
                       f'quiz={quiz_id} media={q.get("media_type", "")}')
        storage.mark_quiz_ready(quiz_id)
        n = storage.question_count(quiz_id)
        row = storage.get_quiz_row(quiz_id)
        title = f'{row["emoji"]} {row["title"]}' if row else "Quiz"
        st.success(f'✅ Question saved — **{title}** now has **{n}** question(s) in the Quiz Library.')
        if st.button("📚 Open Quiz Library →", key="mq_goto_library", use_container_width=True):
            detail = "Review and host when ready."
            if live and live["status"] == "LOBBY" and str(live.get("quiz_id", "")) == str(quiz_id):
                detail = "Also synced to your live lobby game."
            _push_to_quiz_library(quiz_id, detail)
            st.rerun()


# ---------------- Bulk Excel + Image Import ----------------

def _bulk_import(email: str) -> None:
    st.markdown(
        '<div class="qt-sub">Build a full quiz from Excel — upload <b>text questions</b> and '
        '<b>images</b> together in one ZIP, as two separate files, or text-only. '
        'Use <code>image_file</code> in Excel to link each row to a photo in your ZIP.</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Download Excel template",
        data=bulk_import.template_bytes(),
        file_name="QuizTok_question_import_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False,
        key="bulk_tpl_dl",
    )

    quizzes = storage.get_quizzes()
    mode = st.radio(
        "Import mode",
        [
            "Text only (Excel)",
            "Text + Images separately (Excel + ZIP)",
            "Combined package (single ZIP with Excel + images)",
            "Images only — attach to existing quiz (mapping Excel + ZIP)",
        ],
        key="bulk_mode",
    )

    target_mode = st.radio("Target quiz", ["Add to existing quiz", "Create new quiz"],
                           horizontal=True, key="bulk_target")
    quiz_id = ""
    if target_mode == "Add to existing quiz":
        if quizzes.empty:
            st.warning("No quizzes yet — choose **Create new quiz** or build one from the Question Bank.")
            return
        labels = {f'{r["emoji"]} {r["title"]}': str(r["quiz_id"]) for _, r in quizzes.iterrows()}
        quiz_id = labels[st.selectbox("Quiz", list(labels.keys()), key="bulk_quiz_pick")]
    else:
        if mode == "Images only — attach to existing quiz (mapping Excel + ZIP)":
            st.warning("Image-only attach requires an existing quiz with questions already imported.")
            if quizzes.empty:
                return
            labels = {f'{r["emoji"]} {r["title"]}': str(r["quiz_id"]) for _, r in quizzes.iterrows()}
            quiz_id = labels[st.selectbox("Quiz", list(labels.keys()), key="bulk_quiz_pick_img")]
        else:
            c1, c2 = st.columns([3, 1])
            new_title = c1.text_input("New quiz title", value="Imported Quiz Pack", key="bulk_new_title")
            new_emoji = c2.selectbox("Emoji", ["📦", "🏦", "🎬", "📚", "🖼️", "⚡"], key="bulk_new_emoji")

    excel_file = None
    zip_file = None
    combined_zip = None

    if mode == "Combined package (single ZIP with Excel + images)":
        combined_zip = st.file_uploader("Upload ZIP (Excel + images inside)", type=["zip"], key="bulk_combined")
    elif mode == "Images only — attach to existing quiz (mapping Excel + ZIP)":
        excel_file = st.file_uploader("Mapping Excel (columns: q_index, image_file)", type=["xlsx", "xls"],
                                      key="bulk_map_xlsx")
        zip_file = st.file_uploader("Images ZIP", type=["zip"], key="bulk_img_only_zip")
    elif mode == "Text + Images separately (Excel + ZIP)":
        excel_file = st.file_uploader("Questions Excel", type=["xlsx", "xls"], key="bulk_sep_xlsx")
        zip_file = st.file_uploader("Images ZIP (optional — match image_file column)", type=["zip"],
                                    key="bulk_sep_zip")
    else:
        excel_file = st.file_uploader("Questions Excel", type=["xlsx", "xls"], key="bulk_text_xlsx")

    preview_rows: list[dict] = []
    parse_errors: list[str] = []

    if mode == "Combined package (single ZIP with Excel + images)":
        if combined_zip:
            xlsx_data, images, zerr = bulk_import.parse_combined_zip(combined_zip.getvalue())
            parse_errors.extend(zerr)
            if xlsx_data:
                preview_rows, parse_errors = bulk_import.parse_questions_excel(xlsx_data)
                st.caption(f"Found **{len(preview_rows)}** question(s) and **{len(images)}** image(s) in ZIP.")
    elif excel_file:
        if mode.startswith("Images only"):
            preview_rows, parse_errors = bulk_import.parse_image_mapping_excel(excel_file.getvalue())
            st.caption(f"**{len(preview_rows)}** image mapping row(s).")
        else:
            preview_rows, parse_errors = bulk_import.parse_questions_excel(excel_file.getvalue())
            st.caption(f"**{len(preview_rows)}** question row(s) ready.")

    if parse_errors:
        for err in parse_errors:
            st.error(err)

    if preview_rows and not mode.startswith("Images only"):
        show = pd.DataFrame(preview_rows)[
            ["row_num", "qtype", "question", "correct", "timer_sec", "points", "image_file"]
        ]
        st.dataframe(show, use_container_width=True, height=min(120 + 35 * len(show), 320), hide_index=True)
    elif preview_rows and mode.startswith("Images only"):
        st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, height=160, hide_index=True)

    live = game.load()
    if live and live["status"] == "LOBBY" and live["host"] == email:
        st.info(f'🔴 Live lobby PIN **{live["pin"]}** — imported questions can be appended after import.')

    if st.button("🚀 Run import", key="bulk_run", type="primary", use_container_width=True,
                 disabled=not preview_rows and mode != "Combined package (single ZIP with Excel + images)"):
        if target_mode == "Create new quiz" and not mode.startswith("Images only"):
            quiz_id = bulk_import.create_import_quiz(new_title, new_emoji, email)

        if not quiz_id:
            st.error("Select or create a target quiz.")
            st.stop()

        images: dict[str, bytes] = {}
        rows = preview_rows

        if mode == "Combined package (single ZIP with Excel + images)":
            if not combined_zip:
                st.error("Upload a combined ZIP first.")
                st.stop()
            xlsx_data, images, zerr = bulk_import.parse_combined_zip(combined_zip.getvalue())
            if zerr:
                for e in zerr:
                    st.error(e)
                st.stop()
            rows, parse_errors = bulk_import.parse_questions_excel(xlsx_data or b"")
            if parse_errors:
                for e in parse_errors:
                    st.error(e)
                st.stop()
            result = bulk_import.import_questions(quiz_id, rows, images)
        elif mode.startswith("Images only"):
            if not excel_file or not zip_file:
                st.error("Upload both mapping Excel and images ZIP.")
                st.stop()
            images, iw = bulk_import.extract_images_from_zip(zip_file.getvalue())
            rows, _ = bulk_import.parse_image_mapping_excel(excel_file.getvalue())
            result = bulk_import.attach_images_to_quiz(quiz_id, rows, images)
            result.warnings.extend(iw)
        else:
            if not excel_file:
                st.error("Upload a questions Excel file.")
                st.stop()
            rows, errs = bulk_import.parse_questions_excel(excel_file.getvalue())
            if errs:
                for e in errs:
                    st.error(e)
                st.stop()
            if zip_file:
                images, iw = bulk_import.extract_images_from_zip(zip_file.getvalue())
            else:
                iw = []
            result = bulk_import.import_questions(quiz_id, rows, images)
            result.warnings.extend(iw)

        for w in result.warnings:
            st.warning(w)
        for e in result.errors:
            st.error(e)

        if result.added:
            action = "attached" if mode.startswith("Images only") else "imported"
            logger.log(email, "admin", "bulk_import",
                       f'quiz={quiz_id} {action}={result.added} mode={mode[:20]}')
            storage.mark_quiz_ready(quiz_id)

            if live and live["status"] == "LOBBY" and live["host"] == email \
                    and str(live.get("quiz_id", "")) == str(quiz_id) and not mode.startswith("Images only"):
                fresh = storage.get_questions(quiz_id)
                existing = len(live.get("questions", []))
                appended = 0
                for q in fresh[existing:]:
                    ok, _ = game.append_question_in_lobby(email, q)
                    if ok:
                        appended += 1
                extra = f" {appended} added to live lobby." if appended else ""
            else:
                extra = ""
            _push_to_quiz_library(
                quiz_id,
                f'{result.added} question(s) {action}.{extra}',
            )
            st.rerun()
        elif not result.errors:
            st.warning("Nothing was imported — check your files and try again.")


# ---------------- Teams ----------------

def _teams(email: str) -> None:
    teams_df = storage.get_teams()
    scores_df = storage.read_sheet(config.RESULTS_XLSX, "scores")

    # ── quick stats bar ──────────────────────────────────────────────────────
    humans = scores_df[scores_df["is_bot"] == False] if not scores_df.empty else scores_df  # noqa: E712
    has_team = humans[humans["team"].notna() & (humans["team"].astype(str).str.strip() != "")] if not humans.empty else humans
    solo_players = humans[(humans["team"].isna()) | (humans["team"].astype(str).str.strip() == "")] if not humans.empty else humans

    c1, c2, c3, c4 = st.columns(4)
    ui.kpi_card(c1, str(len(teams_df)), "ACTIVE TEAMS", spark="🏆")
    ui.kpi_card(c2, str(has_team["player"].nunique()) if not has_team.empty else "0",
                "TEAM PLAYERS", spark="👥", tone="teal")
    ui.kpi_card(c3, str(solo_players["player"].nunique()) if not solo_players.empty else "0",
                "SOLO PLAYERS", spark="🎯", tone="gold")
    ui.kpi_card(c4, str(scores_df["game_id"].nunique()) if not scores_df.empty else "0",
                "TOTAL GAMES", spark="🎪", tone="pink")

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ── team cards ───────────────────────────────────────────────────────────
    if not teams_df.empty:
        st.markdown('<div class="qt-cat">REGISTERED TEAMS</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(teams_df), 4))
        for i, (_, row) in enumerate(teams_df.iterrows()):
            team_name = str(row["name"])
            team_emoji = str(row["emoji"]) if pd.notna(row["emoji"]) else "🏆"
            team_color = str(row["color"]) if pd.notna(row["color"]) else "#0088ce"
            # count players in this team from results
            t_players = int(has_team[has_team["team"] == team_name]["player"].nunique()) \
                if not has_team.empty else 0
            t_score = int(has_team[has_team["team"] == team_name]["score"].sum()) \
                if not has_team.empty else 0
            with cols[i % 4]:
                st.markdown(
                    f'<div class="qt-card" style="border-top:3px solid {team_color};padding:14px 16px;margin-bottom:8px">'
                    f'<div style="font-size:28px;line-height:1">{team_emoji}</div>'
                    f'<div style="font-weight:700;font-size:15px;color:#eef5ff;margin:6px 0 2px">{team_name}</div>'
                    f'<div style="font-size:12px;color:rgba(255,255,255,.45)">{t_players} players · {t_score:,} pts</div>'
                    f'</div>', unsafe_allow_html=True)
                if st.button("🗑️ Remove", key=f"del_team_{i}", use_container_width=True):
                    storage.delete_team(team_name)
                    logger.log(email, "admin", "team_deleted", team_name)
                    st.rerun()

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # ── create / manage teams ────────────────────────────────────────────────
    with st.expander("➕ Create New Team", expanded=teams_df.empty):
        with st.form("new_team_form", border=False):
            nc1, nc2, nc3 = st.columns([3, 1, 2])
            t_name  = nc1.text_input("Team Name", placeholder="e.g. Quantum Hustlers")
            t_emoji = nc2.selectbox("Icon", ["⚡", "🔥", "🏆", "🌊", "💜", "🎯",
                                              "🦁", "🚀", "🐉", "🌟", "🎪", "💎"])
            t_color = nc3.selectbox("Colour", [
                "#0088ce — ABC Blue", "#e21836 — ABC Red", "#ffc233 — Gold",
                "#00c9a7 — Teal", "#7c5cff — Purple", "#ff6b35 — Orange",
            ])
            create_btn = st.form_submit_button("Create Team 🏆", use_container_width=True)
        if create_btn:
            if not t_name.strip():
                st.error("Team name cannot be empty.")
            else:
                hex_color = t_color.split(" ")[0]
                ok = storage.upsert_team(t_name.strip(), t_emoji, hex_color, email)
                if ok:
                    logger.log(email, "admin", "team_created", t_name.strip())
                    st.success(f'Team "{t_name.strip()}" created! 🎉')
                    st.rerun()
                else:
                    st.warning("A team with that name already exists.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # ── team battle scoreboard ───────────────────────────────────────────────
    st.markdown('<div class="qt-cat">🏆 TEAM BATTLE SCOREBOARD</div>', unsafe_allow_html=True)
    board = storage.get_team_scoreboard()
    if board.empty:
        st.info("No team games played yet — host a game with team players to see results here.")
    else:
        medals = ["🥇", "🥈", "🥉"]
        for idx, row in board.iterrows():
            medal = medals[idx] if idx < 3 else f"#{idx + 1}"
            bar_w = int(100 * row["Total Score"] / board["Total Score"].max())
            st.markdown(
                f'<div class="qt-row" style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,.06)">'
                f'<span style="font-size:20px;width:36px">{medal}</span>'
                f'<span class="nm" style="flex:2;font-weight:600">{row["Team"]}</span>'
                f'<span class="bar" style="flex:3;height:8px;background:rgba(0,0,0,.35);border-radius:99px;overflow:hidden">'
                f'<i style="display:block;height:100%;width:{bar_w}%;background:linear-gradient(90deg,#0088ce,#4db4ff);border-radius:99px"></i></span>'
                f'<span class="pt" style="margin-left:12px;min-width:80px;text-align:right">{int(row["Total Score"]):,} pts</span>'
                f'<span class="pt" style="margin-left:8px;color:rgba(255,255,255,.4);min-width:60px">{row["Players"]}p / {row["Games"]}g</span>'
                f'</div>', unsafe_allow_html=True)

    # ── solo competitors ─────────────────────────────────────────────────────
    st.markdown('<div class="qt-cat" style="margin-top:20px">🎯 SOLO COMPETITORS</div>',
                unsafe_allow_html=True)
    if not solo_players.empty:
        solo_agg = solo_players.groupby("player").agg(
            Games=("game_id", "nunique"),
            Best=("score", "max"),
            Total=("score", "sum"),
        ).sort_values("Total", ascending=False).reset_index()
        solo_agg.columns = ["Player", "Games", "Best Score", "Total Score"]
        st.dataframe(solo_agg, use_container_width=True, height=180, hide_index=True)
    else:
        st.info("No solo players recorded yet.")

    # ── activity log & game history ──────────────────────────────────────────
    st.markdown('<div class="qt-cat" style="margin-top:20px">🏁 GAMES PLAYED</div>',
                unsafe_allow_html=True)
    st.dataframe(storage.read_sheet(config.RESULTS_XLSX, "games").iloc[::-1],
                 use_container_width=True, height=160, hide_index=True)

    st.markdown('<div class="qt-cat">📋 ACTIVITY LOG (latest 50)</div>', unsafe_allow_html=True)
    st.dataframe(logger.tail(50), use_container_width=True, height=200, hide_index=True)

    st.markdown(
        '<div class="qt-sub">All data files are in the <b style="color:#4db4ff">data/</b> folder '
        '— teams.xlsx, results.xlsx, activity_log.xlsx, quizzes.xlsx — open in Excel anytime.</div>',
        unsafe_allow_html=True)


# ---------------- Domain Academy (admin) ----------------

def _domain_academy(email: str) -> None:
    nodes = domain_knowledge.load_nodes()
    terms = domain_knowledge.load_terms()
    analytics = domain_knowledge.learning_analytics()

    c1, c2, c3 = st.columns(3)
    ui.kpi_card(c1, str(analytics["active_learners"]), "ACTIVE LEARNERS", tone="teal")
    ui.kpi_card(c2, str(analytics["total_mastered"]), "TERMS MASTERED", tone="gold")
    ui.kpi_card(c3, str(len(terms)), "GLOSSARY TERMS", tone="pink")

    st.markdown('<div class="qt-cat" style="margin-top:14px">DOMAIN TREE</div>', unsafe_allow_html=True)
    st.dataframe(nodes[["node_id", "parent_id", "label", "category", "node_type"]],
                 use_container_width=True, height=220, hide_index=True)

    st.markdown('<div class="qt-cat">GLOSSARY TERMS</div>', unsafe_allow_html=True)
    st.dataframe(terms[["term_id", "abbr", "expansion", "definition", "related_qids"]],
                 use_container_width=True, height=240, hide_index=True)

    if analytics["top_missed"]:
        st.markdown('<div class="qt-cat">MOST MISSED TERMS</div>', unsafe_allow_html=True)
        for item in analytics["top_missed"]:
            st.markdown(
                f'<div class="qt-row"><span class="nm">{item["term_id"]}</span>'
                f'<span class="pt">{item["count"]} reviews needed</span></div>',
                unsafe_allow_html=True)

    if analytics["by_domain"]:
        st.markdown('<div class="qt-cat">MASTERY BY DOMAIN</div>', unsafe_allow_html=True)
        for cat, count in analytics["by_domain"].items():
            st.markdown(f'<div class="qt-row"><span class="nm">{cat}</span><span class="pt">{count} mastered</span></div>',
                        unsafe_allow_html=True)

    if st.button("🔄 Sync question bank → related qids", key="sync_qids"):
        n = domain_knowledge.sync_related_qids()
        logger.log(email, "admin", "domain_sync", f"updated {n} terms")
        st.success(f"Updated related question links for {n} terms.")

    st.markdown(
        f'<div class="qt-sub">Edit tree & terms in <b style="color:#4db4ff">data/domain_tree.xlsx</b> '
        f'— changes appear here on refresh.</div>',
        unsafe_allow_html=True)


# ---------------- Feedback Inbox ----------------

def _feedback_inbox(email: str) -> None:
    st.markdown('<div class="qt-sub">Participant suggestions for animations, content, UX and operations.</div>',
                unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    status_f = f1.selectbox("Status filter", ["", *feedback.FEEDBACK_STATUSES],
                            format_func=lambda x: x or "All")
    cat_f = f2.selectbox("Category filter", ["", *feedback.FEEDBACK_CATEGORIES],
                         format_func=lambda x: x or "All")

    df = feedback.list_feedback(status=status_f, category=cat_f)
    if df.empty:
        st.info("No feedback yet — participants can submit from the Ops Academy panel.")
        return

    st.dataframe(df, use_container_width=True, height=280, hide_index=True)

    st.markdown('<div class="qt-cat">UPDATE STATUS</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    fid = c1.selectbox("Feedback ID", df["feedback_id"].tolist())
    new_status = c2.selectbox("New status", feedback.FEEDBACK_STATUSES)
    if c3.button("Save", key="fb_save"):
        feedback.update_status(fid, new_status)
        logger.log(email, "admin", "feedback_updated", f"{fid} → {new_status}")
        st.rerun()

