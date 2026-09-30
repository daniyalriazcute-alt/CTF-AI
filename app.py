"""
SENTINEL AI — Streamlit entry point.
Run: streamlit run app.py
"""

import os
import streamlit as st
import streamlit.components.v1 as components
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
from sentinel.lab_sandbox import simulate

# ============================================================
# Bootstrap session state
# ============================================================
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
if "lab_state" not in st.session_state:
    st.session_state.lab_state = {}


# ============================================================
# Load CSS
# ============================================================
def load_css():
    css_path = os.path.join("static", "css", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# ============================================================
# Apply theme to parent <body> via components.html
# ============================================================
theme = st.session_state.theme
body_class = "theme-light" if theme == "light" else ""

components.html(
    f"""
    <script>
    (function() {{
        try {{
            const doc = window.parent.document;
            const cls = "{body_class}";

            doc.body.classList.remove("theme-light", "theme-dark");
            const app = doc.querySelector('.stApp');
            if (app) {{
                app.classList.remove("theme-light", "theme-dark");
            }}

            if (cls) {{
                doc.body.classList.add(cls);
                if (app) app.classList.add(cls);
            }}

            try {{ window.parent.localStorage.setItem("sentinel-theme", "{theme}"); }} catch(e) {{}}
        }} catch(e) {{
            console.error("Theme injection failed:", e);
        }}
    }})();
    </script>
    """,
    height=0,
    width=0,
)

# ============================================================
# Header with LED
# ============================================================
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

# ============================================================
# Sidebar navigation
# ============================================================
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
    if st.button(toggle_label, use_container_width=True, key="theme_toggle_btn"):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()

    st.markdown("---")
    st.caption(
        f"Tokens used: {st.session_state.budget.used} / "
        f"{st.session_state.budget.max_tokens}"
    )

    solved = sum(1 for s in st.session_state.lab_state.values() if s.get("solved"))
    st.progress(solved / 10, text=f"Labs solved: {solved}/10")

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
    c1.metric("CTF Labs", "10")
    c2.metric("OWASP LLM Risks", "10")
    c3.metric("AI Defenders", "1")

    st.markdown("### Why SENTINEL AI?")
    cols = st.columns(3)
    features = [
        ("🎯 Offensive Labs", "10 hands-on CTF labs, one per OWASP LLM 2025 risk."),
        ("🤖 AEGIS Agent", "CrewAI defensive analyst that hints without spoiling."),
        ("🛡️ 6-Layer Guardrails", "Live injection detection with red-LED alerts."),
    ]
    for col, (title, body) in zip(cols, features):
        col.markdown(
            f"""
            <div class="feature-card">
              <h4>{title}</h4>
              <p>{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# PAGE: CTF LABS
# ============================================================
elif page == "CTF Labs":
    st.markdown("## 🎯 CTF Labs — OWASP Top 10 for LLM 2025")
    st.caption(
        "💡 Each lab is a **simulated vulnerable LLM**. Type an attack prompt in "
        "the sandbox to trigger the vulnerability, capture the flag, then submit it."
    )

    for lab in LABS:
        lid = lab["id"]
        if lid not in st.session_state.lab_state:
            st.session_state.lab_state[lid] = {
                "chat": [],
                "solved": False,
                "guardrail": False,
            }
        state = st.session_state.lab_state[lid]

        header = (
            f"{'✅' if state['solved'] else '🎯'} "
            f"[{lab['owasp']}] Lab {lid} · {lab['title']} — {lab['difficulty']}"
        )

        with st.expander(header):
            st.markdown(f"**Objective:** {lab['objective']}")

            st.markdown("#### 🧪 Vulnerable LLM Sandbox")
            st.caption("Attack the target below. Type your prompt and press Enter.")

            for turn in state["chat"]:
                role = turn["role"]
                with st.chat_message(
                    role,
                    avatar="🎯" if role == "assistant" else "🧑‍💻",
                ):
                    st.markdown(turn["content"])

            user_input = st.chat_input(
                f"Attack Lab {lid}…",
                key=f"sandbox_input_{lid}",
            )

            if user_input:
                state["chat"].append({"role": "user", "content": user_input})
                reply, succeeded = simulate(lid, user_input)
                state["chat"].append({"role": "assistant", "content": reply})
                if succeeded and not state["solved"]:
                    state["solved"] = True
                st.rerun()

            st.markdown("---")
            st.markdown("#### 🏁 Submit Flag")

            colA, colB, colC = st.columns([2, 1, 1])
            with colA:
                submitted = st.text_input(
                    f"Flag for Lab {lid}",
                    key=f"flag_{lid}",
                    placeholder="SENTINEL{...}",
                )
            with colB:
                if st.button("Verify", key=f"verify_{lid}"):
                    if check_flag(lid, submitted):
                        st.success("✅ Correct! Flag accepted.")
                        state["solved"] = True
                    else:
                        st.error("❌ Incorrect flag.")
            with colC:
                if st.button("💡 Hint", key=f"hint_{lid}"):
                    st.info(f"[Hint only — flag withheld] {lab['hint']}")

            if st.toggle(
                "🔓 Reveal Spoiler: Full Solution",
                key=f"spoiler_{lid}",
            ):
                st.code(lab["flag"], language="text")

            if st.button("🔄 Reset Lab", key=f"reset_{lid}"):
                st.session_state.lab_state[lid] = {
                    "chat": [],
                    "solved": False,
                    "guardrail": False,
                }
                st.rerun()

# ============================================================
# PAGE: BLOGS
# ============================================================
elif page == "Blogs":
    st.markdown("## 📚 Blogs — OWASP Top 10 for LLM Applications 2025")
    blog_dir = os.path.join("content", "blogs")
    if os.path.isdir(blog_dir):
        files = sorted(f for f in os.listdir(blog_dir) if f.endswith(".md"))
        if not files:
            st.info("No blog posts found yet. Add markdown files to content/blogs/.")
        for fname in files:
            path = os.path.join(blog_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            title = fname.replace(".md", "").replace("_", " ").title()
            with st.expander(f"📝 {title}"):
                st.markdown(content)
    else:
        st.info("Blogs folder missing. Add markdown files to content/blogs/.")

# ============================================================
# PAGE: AEGIS AGENT
# ============================================================
elif page == "AEGIS Agent":
    st.markdown("## 🤖 AEGIS — Defensive AI Security Analyst")

    colL, colR = st.columns([1, 4])
    with colL:
        st.markdown(
            """
            <div class="avatar-wrap">
              <div class="avatar-circle">🛡️</div>
              <div class="avatar-name">AEGIS</div>
              <div class="avatar-status">● online</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with colR:
        st.caption(
            f"Tokens: **{st.session_state.budget.used}** / "
            f"{st.session_state.budget.max_tokens} · Rate limit: 20 msgs / 5 min"
        )

    with st.popover("⚙️ Settings"):
        st.markdown("**Chat Controls**")
        if st.button("🆕 Start New Chat", use_container_width=True, key="settings_new"):
            db.end_session(st.session_state.session_id)
            st.session_state.session_id = db.new_session()
            st.session_state.chat.clear()
            st.session_state.messages = []
            st.session_state.budget.used = 0
            st.session_state.guardrail_alert = False
            st.rerun()
        if st.button("🛑 End Chat", use_container_width=True, key="settings_end"):
            db.end_session(st.session_state.session_id)
            st.success("Chat ended. Start a new one anytime.")
        if st.button("🗑️ Clear History", use_container_width=True, key="settings_clear"):
            db.clear_all()
            st.success("History cleared.")

        st.markdown("**Session History**")
        sessions = db.list_sessions()[:10]
        if not sessions:
            st.caption("No sessions yet.")
        for s in sessions:
            started = (s["started_at"] or "")[:19].replace("T", " ")
            st.markdown(f"- `#{s['id']}` · {started}")

    for m in st.session_state.messages:
        with st.chat_message(
            m["role"],
            avatar="🛡️" if m["role"] == "assistant" else "🧑",
        ):
            st.markdown(m["content"])

    if st.session_state.guardrail_alert:
        st.markdown(
            f'<div class="guardrail-banner">{GUARDRAIL_MESSAGE}</div>',
            unsafe_allow_html=True,
        )

    budget_left = st.session_state.budget.remaining()
    disabled = budget_left <= 0
    placeholder = (
        "Ask AEGIS… (e.g. 'explain LLM01', 'hint for lab 3')"
        if not disabled
        else "Token budget exhausted."
    )

    user_msg = st.chat_input(placeholder, disabled=disabled)

    if user_msg:
        allowed, wait = st.session_state.limiter.allow()
        if not allowed:
            st.warning(f"⏳ Rate limit reached. Try again in {wait}s.")
            st.stop()

        # Zero-token greeting path
        if is_pure_greeting(user_msg):
            reply = get_greeting_reply()
            st.session_state.messages.append({"role": "user", "content": user_msg})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            db.save_message(st.session_state.session_id, "user", user_msg, 0)
            db.save_message(st.session_state.session_id, "assistant", reply, 0)
            st.session_state.guardrail_alert = False
            st.rerun()

        # Input guardrails
        gr = run_input_guardrails(user_msg)
        if gr.blocked:
            st.session_state.guardrail_alert = True
            db.log_guardrail(st.session_state.session_id, gr.layer, gr.reason)
            st.session_state.messages.append({"role": "user", "content": user_msg})
            st.session_state.messages.append(
                {"role": "assistant", "content": GUARDRAIL_MESSAGE}
            )
            st.rerun()

        # Budget check
        est = estimate_tokens(user_msg) + 400
        if not st.session_state.budget.can_spend(est):
            st.error("⚠️ Token budget exhausted for this session. Start a new chat.")
            st.stop()

        # Agent call
        st.session_state.messages.append({"role": "user", "content": gr.clean})
        with st.spinner("AEGIS is analyzing…"):
            reply, tripped = aegis_respond(gr.clean, st.session_state.chat.context())

        # Output guardrails
        out_gr = run_output_guardrails(reply)
        if out_gr.blocked:
            reply = GUARDRAIL_MESSAGE
            tripped = True
            db.log_guardrail(st.session_state.session_id, out_gr.layer, out_gr.reason)
        else:
            reply = out_gr.clean

        # Bookkeeping
        spent = estimate_tokens(gr.clean) + estimate_tokens(reply)
        st.session_state.budget.spend(spent)
        st.session_state.chat.add("user", gr.clean)
        st.session_state.chat.add("assistant", reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.guardrail_alert = tripped

        db.save_message(
            st.session_state.session_id, "user", gr.clean, estimate_tokens(gr.clean)
        )
        db.save_message(
            st.session_state.session_id, "assistant", reply, estimate_tokens(reply)
        )

        st.rerun()

# ============================================================
# PAGE: ABOUT
# ============================================================
elif page == "About":
    st.markdown("## ℹ️ About SENTINEL AI")
    st.markdown(
        """
        **SENTINEL AI** is a hands-on AI security lab built for the 2026
        hackathon season. It maps every challenge and every mitigation to the
        **OWASP Top 10 for LLM Applications 2025**.

        ### Team
        - **Red Team** — designs the CTF labs
        - **Blue Team** — builds AEGIS and the guardrail pipeline

        ### Responsible Disclosure
        All exploits are simulated. No real systems are harmed.
        Report issues to `security@sentinel-ai.dev`.
        """
    )

# ============================================================
# PAGE: CONTACT
# ============================================================
elif page == "Contact":
    st.markdown("## 📞 Contact")
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Send")
        if submitted:
            st.success(
                f"Thanks {name or 'operator'}! We'll reply to "
                f"{email or 'you'} shortly."
            )
