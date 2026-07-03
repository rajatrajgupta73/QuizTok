"""Admin Command Center — dashboard, quiz library, 2000-question bank, builder, reports."""
import streamlit as st

import config
from core import game, logger, question_bank, storage
from ui import components as ui


def render() -> None:
    email = st.session_state.get("admin_email", "admin")
    ui.topbar(ui.pill("ADMIN", red=True), ui.pill(f'👩‍💼 {email}'))

    top_l, top_r = st.columns([3, 1])
    top_l.markdown(f'<div class="qt-h1" style="font-family:\'Baloo 2\',cursive;font-size:30px;'
                   f'font-weight:800">Command Center 🎛️</div>'
                   f'<div class="qt-sub">Welcome back, {st.session_state.get("admin_name", "Admin")}! '
                   f'Build quizzes from the bank, host live games, and export everything to Excel.</div>',
                   unsafe_allow_html=True)
    if top_r.button("Logout", type="secondary", use_container_width=True):
        st.session_state.page = "login"
        st.session_state.role = None
        st.rerun()

    live = game.load()
    if live and live["status"] not in ("FINISHED",):
        st.info(f'🔴 A game is LIVE right now — PIN **{live["pin"]}** · {live["quiz_title"]} · '
                f'{len(live["players"])} players')
        if st.button("Open Host Controls 🎛️", key="gold_host"):
            st.session_state.page = "host"
            st.rerun()

    tabs = st.tabs(["📊 Dashboard", "📚 Quiz Library", "🏦 Question Bank (2000)",
                    "✏️ Question Builder", "📈 Reports & Logs"])

    with tabs[0]:
        _dashboard()
    with tabs[1]:
        _quiz_library(email)
    with tabs[2]:
        _question_bank(email)
    with tabs[3]:
        _question_builder(email)
    with tabs[4]:
        _reports()


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
    quizzes = storage.get_quizzes()
    if quizzes.empty:
        st.info("No quizzes yet — build one from the Question Bank tab!")
        return

    bots = st.toggle("Add demo bots 🤖 (fills the lobby for small groups)", value=True)
    live = game.load()
    thumbs = ["linear-gradient(135deg,#0088ce,#005a9e)", "linear-gradient(135deg,#e21836,#a80f26)",
              "linear-gradient(135deg,#00c9a7,#00806a)", "linear-gradient(135deg,#7c5cff,#4b32b4)"]
    for i, (_, row) in enumerate(quizzes.iloc[::-1].iterrows()):
        n_q = storage.question_count(str(row["quiz_id"]))
        is_live = bool(live and live["status"] != "FINISHED"
                       and str(live.get("quiz_id", "")) == str(row["quiz_id"]))
        status = '<span class="qt-status live">● LIVE NOW</span>' if is_live \
            else '<span class="qt-status ready">READY</span>' if n_q else \
            '<span class="qt-status draft">DRAFT</span>'
        col1, col2 = st.columns([4, 1])
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
        n_subj = b4.number_input("Subjective (vote) rounds", 0, 5, 1)
        build = st.form_submit_button("Create Quiz from Bank ➕", use_container_width=True)
    if build:
        quiz_id = question_bank.build_quiz_from_bank(
            title, emoji, cats or question_bank.CATEGORIES, diffs, int(n_q), int(n_subj), email)
        logger.log(email, "admin", "quiz_built_from_bank", f'{quiz_id} n={n_q} subj={n_subj}')
        st.success(f'Quiz "{title}" created with {n_q} questions — find it in the Quiz Library! 🎉')


# ---------------- Question Builder ----------------

def _question_builder(email: str) -> None:
    quizzes = storage.get_quizzes()
    if quizzes.empty:
        st.info("Create a quiz first (Question Bank tab).")
        return
    labels = {f'{r["emoji"]} {r["title"]}': str(r["quiz_id"]) for _, r in quizzes.iterrows()}
    target = st.selectbox("Add to quiz", list(labels.keys()))
    qtype = st.radio("Question type", ["MCQ", "Subjective (voting round)"], horizontal=True)

    with st.form("builder", border=False):
        question = st.text_area("Question", height=80,
                                placeholder="e.g. Which metric measures wrap-up time after a call?")
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
        timer = t1.number_input("Timer (seconds)", 10, 120,
                                config.DEFAULT_TIMER_SEC if qtype == "MCQ" else config.SUBJECTIVE_TIMER_SEC)
        points = t2.number_input("Points", 100, 5000, config.BASE_POINTS, step=100)
        add = st.form_submit_button("Add to Quiz ➕", use_container_width=True)

    if add:
        if not question.strip() or (qtype == "MCQ" and not all(o.strip() for o in opts)):
            st.error("Fill the question and all four options.")
        else:
            storage.add_question(labels[target], question.strip(), opts, correct,
                                 int(timer), int(points),
                                 qtype="mcq" if qtype == "MCQ" else "subjective")
            logger.log(email, "admin", "question_added", f'quiz={labels[target]}')
            st.success("Question added! 🎯")


# ---------------- Reports ----------------

def _reports() -> None:
    st.markdown('<div class="qt-cat">🏁 GAMES PLAYED</div>', unsafe_allow_html=True)
    st.dataframe(storage.read_sheet(config.RESULTS_XLSX, "games").iloc[::-1],
                 use_container_width=True, height=180, hide_index=True)

    st.markdown('<div class="qt-cat">🏆 SCORES</div>', unsafe_allow_html=True)
    st.dataframe(storage.read_sheet(config.RESULTS_XLSX, "scores").iloc[::-1],
                 use_container_width=True, height=200, hide_index=True)

    st.markdown('<div class="qt-cat">📋 ACTIVITY LOG (latest 50)</div>', unsafe_allow_html=True)
    st.dataframe(logger.tail(50), use_container_width=True, height=220, hide_index=True)

    st.markdown(
        '<div class="qt-sub">All files live in the <b style="color:#4db4ff">data/</b> folder: '
        'results.xlsx (games · scores · answers), activity_log.xlsx, quizzes.xlsx, '
        'question_bank.xlsx, users.xlsx — open them in Excel anytime.</div>', unsafe_allow_html=True)
