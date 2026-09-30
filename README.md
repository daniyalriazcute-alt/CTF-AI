# 🛡️ SENTINEL AI

**Master the Offensive. Defend the Intelligent.**

An OWASP Top 10 for LLM Applications 2025 CTF platform with an embedded
CrewAI-powered defensive analyst called **AEGIS**.

![banner](https://img.shields.io/badge/OWASP-LLM%20Top%2010%202025-00e5ff)
![python](https://img.shields.io/badge/python-3.12.0-blue)
![streamlit](https://img.shields.io/badge/streamlit-1.40-ff4b4b)

## ✨ Features

- 🎯 **10 CTF Labs** — one per OWASP LLM 2025 risk
- 📚 **10 Blogs** — educational write-ups for each risk
- 🤖 **AEGIS Agent** — CrewAI defensive analyst with state machine
  (`goal → decide → act → observe → continue → complete`, retry-once)
- 🛡️ **6-Layer Guardrail Pipeline** — injection detection with blinking red LED
- 💬 **Chat UI** — avatars, settings popover, session history, new/end chat
- 💰 **Token budget** — 4000 tokens/session, rate-limited
- 👋 **Zero-token greetings** — "hi", "hello", "salam" answered free
- 🌗 **Dark / Light mode**

## 🚀 Quickstart

```bash
git clone https://github.com/<your-user>/sentinel-ai.git
cd sentinel-ai
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY
streamlit run app.py
