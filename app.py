"""
SENTINEL AI — Streamlit entry point.
Run: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv()

st.set_page_config(
    page_title="SENTINEL AI — Offensive AI Security Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from sentinel import db
from sentinel.greetings import is_pure_greeting, get_greeting_reply
from sentinel.guardrails import (
    run_input_guardrails,
    run_output_guardrails,
    GUARDRAIL_MESSAGE,
)
from sentinel.rate_limit import RateLimiter, TokenBudget, estimate_tokens
from sentinel.memory import ShortTermMemory
from sentinel.aegis_crew import aegis_respond
from sentinel.ctf_labs import LABS, check_flag

# ---------- Bootstrap ----------
db.init_db()

if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "guardrail_alert" not in st.session_state:
    st.session_state.guardrail_alert = False
if "chat" not in st.session_state:
    st.session_state.chat = ShortTermMemory(window=8)
if "budget" not in st.session_state:
    st.session_state.budget = TokenBudget(
        int(os.getenv("MAX_TOKENS_PER_SESSION", "4000"))
    )
if "limiter" not in st.session_state:
    st.session_state.limiter = RateLimiter(
        int(os.getenv("RATE_LIMIT_MESSAGES", "20")),
        int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "300")),
    )
if "session_id" not in st.session_state:
    st.session_state.session_id = db.new_session()
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- Load CSS ----------
def load_css():
    css_path = os.path.join("static", "css", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

theme = st.session_state.theme
st.markdown(f'<div data-theme="{theme}"></div>', unsafe_allow_html=True)

# ---------- Header LED ----------
led_class = "led led-danger blink" if st.session_state.guardrail_alert else "led led-ok"
st.markdown(
    f"""
    <div class="sentinel-header">
      <span class="brand">🛡️ SENTINEL <span class="accent">AI</span></span>
      <span class="led-wrap">Guardrail <span class="{led_class}"></span></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Navigation")
    page = option_menu(
        menu_title=None,
        options=["Home", "CTF Labs", "Blogs", "AEGIS Agent", "About", "Contact"],
        icons=["house", "shield-lock", "journal-text", "robot", "info-circle", "envelope"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#00e5ff", "font-size": "16px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "4px 0"},
            "nav-link-selected": {"background-color": "#00e5ff22"},
        },
    )
    st.markdown("---")
    toggle_label = "🌞 Light Mode" if theme == "dark" else "🌙 Dark Mode"
    if st.button(toggle_label, use_container_width=True):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()

    st.markdown("---")
    st.caption(
        f"Tokens used: {st.session_state.budget.used} / "
        f"{st.session_state.budget.max_tokens}"
    )

# ============================================================
# PAGE: HOME
# ============================================================
if page == "Home":
    st.markdown(
        """
        <div class="hero">
          <video class="hero-video" autoplay muted loop playsinline>
            <source src="https://cdn.coverr.co/videos/coverr-a-hacker-in-a-dark-room-1574/1080p.mp4" type="video/mp4">
          </video>
          <div class="hero-overlay">
            <h1 class="hero-title">Master the Offensive. <span class="accent">Defend the Intelligent.</span></h1>
            <p class="hero-sub">SENTINEL AI is an OWASP Top 10 LLM 2025 CTF arena with an embedded defensive AI analyst.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
