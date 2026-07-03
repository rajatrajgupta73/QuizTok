"""QuizTok — Citi-branded team quiz platform.

Run with:  streamlit run app.py
Everything is local: Excel data files in ./data, no internet required.
"""
import streamlit as st

from core import seed, question_bank
from ui import theme
from ui import login_page, lobby_page, quiz_page, results_page, admin_page, host_page

st.set_page_config(page_title="QuizTok · Citi Team Fun", page_icon="🎮",
                   layout="wide", initial_sidebar_state="collapsed")


@st.cache_resource
def _bootstrap() -> bool:
    """One-time setup: data folder, default admin, sample quizzes, 2000-question bank."""
    seed.run()
    question_bank.ensure_bank()
    return True


_bootstrap()
theme.inject()

PAGES = {
    "login": login_page.render,
    "lobby": lobby_page.render,
    "quiz": quiz_page.render,
    "results": results_page.render,
    "admin": admin_page.render,
    "host": host_page.render,
}

page = st.session_state.setdefault("page", "login")

# admin/host pages need an admin session
if page in ("admin", "host") and st.session_state.get("role") != "admin":
    page = st.session_state["page"] = "login"

PAGES.get(page, login_page.render)()
