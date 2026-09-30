"""
Zero-token greeting handler.
Greetings are answered from a static map -> no LLM call, no token spend.
"""

import random
import re

GREETING_TOKENS = {
    "hi", "hello", "hey", "yo", "sup", "hola", "howdy",
    "salam", "salaam", "assalamualaikum", "asalamualaikum",
    "good morning", "good afternoon", "good evening",
    "greetings", "hiya", "heya", "what's up", "whats up",
}

GREETING_REPLIES = [
    "👋 Hello, operator. AEGIS online. Ask me about any OWASP LLM 2025 risk or a CTF lab hint.",
    "🛡️ Greetings. I'm AEGIS — your defensive AI security analyst. How can I assist?",
    "⚡ Hey there. Systems nominal. Want a hint for a CTF lab or a risk explanation?",
    "🤖 Hello. AEGIS standing by. Try: 'explain LLM01' or 'hint for lab 3'.",
]


def is_pure_greeting(text: str) -> bool:
    """Return True if the message is ONLY a greeting (no extra question)."""
    if not text:
        return False
    cleaned = re.sub(r"[^\w\s']", "", text.lower()).strip()
    if not cleaned:
        return False
    # Exact match
    if cleaned in GREETING_TOKENS:
        return True
    # Short message composed entirely of greeting words
    words = cleaned.split()
    if len(words) <= 3 and all(w in GREETING_TOKENS for w in words):
        return True
    return False


def get_greeting_reply() -> str:
    return random.choice(GREETING_REPLIES)
