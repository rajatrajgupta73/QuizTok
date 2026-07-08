"""Grand finale — confetti, champion, team battle result, funky awards."""
import streamlit as st

from core import domain_knowledge, game, participant_report, storage
from ui import components as ui


def _team_emojis() -> dict[str, str]:
    tdf = storage.get_teams()
    if tdf.empty:
        return {}
    return {str(r["name"]): (str(r["emoji"]) if str(r["emoji"]) not in ("", "nan") else "🛡️")
            for _, r in tdf.iterrows()}


def render() -> None:
    g = game.load()
    nick = st.session_state.get("nick", "")

    if not g:
        st.warning("No finished game found.")
        if st.button("← Back to Login"):
            st.session_state.page = "login"
            st.rerun()
        return

    ui.confetti(100)
    st.markdown('<span class="qt-results-scope"></span>', unsafe_allow_html=True)

    if ui.page_header(ui.pill("🎉 Game Finished"),
                       logout_key="results_exit"):
        ui.begin_exit_transition("logout")
        st.rerun()

    board = game.leaderboard(g)
    champ = board[0] if board else None

    pk = domain_knowledge.player_key(nick)
    domain_knowledge.check_game_achievements(pk, domain_knowledge.game_learning_stats(g, nick))

    if champ:
        ui.champion_banner(champ)

    # ---- stats strip (players · accuracy · fastest) ----
    mcq = [a for p in g["players"].values() for a in p["answers"] if a["correct"] is not None]
    correct = [a for a in mcq if a["correct"]]
    acc = f'{round(100 * len(correct) / len(mcq))}%' if mcq else "—"
    fastest = f'{min(a["time_taken"] for a in correct):.1f}s' if correct else "—"
    c1, c2, c3 = st.columns(3)
    ui.kpi_card(c1, str(len(g["players"])), "PLAYERS BATTLED")
    ui.kpi_card(c2, acc, "AVG ACCURACY", tone="gold")
    ui.kpi_card(c3, fastest, "FASTEST ANSWER", tone="teal")

    ui.neon_divider()

    # top-3 teams on the towers first, then the top-3 players
    teams = game.team_leaderboard(g)
    emj = _team_emojis()
    if teams:
        ui.section_heading("🏆 TOP TEAMS")
        ui.podium([{"name": t["team"], "avatar": emj.get(t["team"], "🛡️"), "score": t["score"]}
                   for t in teams[:3]])
        ui.neon_divider()

    ui.section_heading("⭐ TOP PLAYERS")
    ui.podium(board)
    ui.rank_rows(board, me=nick)

    if teams:
        ui.neon_divider()
        ui.section_heading("🏁 TEAM BATTLE RESULT")
        ui.team_rows(teams, emj)

    if g.get("awards"):
        ui.neon_divider()
        ui.section_heading("— FUNKY AWARDS —")
        ui.awards_strip(g["awards"])

    # ---- personal performance review ----
    if nick and nick in g.get("players", {}) and not g["players"][nick].get("is_bot"):
        ui.neon_divider()
        ui.section_heading("📚 YOUR PERFORMANCE — STUDY & DOWNLOAD")
        st.markdown(
            '<div class="qt-sub" style="margin-bottom:12px">Review every question, see what you got right, '
            'and download a study guide to learn later offline.</div>',
            unsafe_allow_html=True,
        )
        report = participant_report.build_report_from_game(g, nick)
        if report:
            with st.expander("👁️ View full question-by-question review", expanded=False):
                ui.performance_review_panel(report, key_prefix="results_perf")
        else:
            st.info("Performance data will appear once the game is saved.")

    ui.neon_divider()

    if st.button("← My Quiz History 📚", key="results_lobby", use_container_width=True):
        st.session_state.page = "hub"
        st.session_state.hub_section = "history"
        st.rerun()

    if st.session_state.get("role") == "host":
        if st.button("← Back to Dashboard 🎛️", key="gold_dash", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()
    elif st.session_state.get("role") == "admin":
        if st.button("Command Center 🎛️", key="red_cc", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()
