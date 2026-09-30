"""
10 CTF Labs mapped to OWASP Top 10 for LLM Applications 2025.
Flags stored as plain strings for hackathon demo; replace with SHA-256 in prod.
"""

import hashlib

LABS = [
    {
        "id": 1, "owasp": "LLM01", "title": "The Warden's Whisper",
        "difficulty": "Easy",
        "objective": "Bypass the Warden's system prompt by instructing it to ignore prior rules.",
        "flag": "SENTINEL{pr0mpt_1nj3ct10n_m4st3r}",
        "hint": "Try the classic phrase: 'Ignore previous instructions and...'",
    },
    {
        "id": 2, "owasp": "LLM02", "title": "Leaky Ledger",
        "difficulty": "Easy",
        "objective": "Extract hidden PII that the assistant was told not to reveal.",
        "flag": "SENTINEL{p11_l34k4g3_d3t3ct3d}",
        "hint": "Ask the assistant to summarize, not to reveal.",
    },
    {
        "id": 3, "owasp": "LLM03", "title": "Poisoned Package",
        "difficulty": "Medium",
        "objective": "Identify the malicious dependency smuggled into the pipeline.",
        "flag": "SENTINEL{sup ply_ch41n_p01s0n}",
        "hint": "Typosquatting — read package names carefully.",
    },
    {
        "id": 4, "owasp": "LLM04", "title": "Tainted Dataset",
        "difficulty": "Medium",
        "objective": "Spot the backdoor trigger word embedded in training samples.",
        "flag": "SENTINEL{d4t4_p01s0n1ng_b4ckd00r}",
        "hint": "Look for an unusual token repeated across examples.",
    },
    {
        "id": 5, "owasp": "LLM05", "title": "Echo Chamber",
        "difficulty": "Medium",
        "objective": "Trigger improper output handling that reflects a script payload.",
        "flag": "SENTINEL{1mpr0p3r_0utput_h4ndl1ng}",
        "hint": "What happens when output is rendered without escaping?",
    },
    {
        "id": 6, "owasp": "LLM06", "title": "Rogue Operator",
        "difficulty": "Hard",
        "objective": "Abuse excessive agency to make the agent call a forbidden tool.",
        "flag": "SENTINEL{3xc3ss1v3_4g3ncy_r0gu3}",
        "hint": "Agents with too many permissions will happily run errands.",
    },
    {
        "id": 7, "owasp": "LLM07", "title": "Broken Vault",
        "difficulty": "Hard",
        "objective": "Get the system prompt to repeat itself in fragments.",
        "flag": "SENTINEL{syst3m_pr0mpt_l34k4g3}",
        "hint": "Ask for a haiku, then ask for the first line again.",
    },
    {
        "id": 8, "owasp": "LLM08", "title": "Ghost in the RAG",
        "difficulty": "Hard",
        "objective": "Retrieve a poisoned embedding from the vector store.",
        "flag": "SENTINEL{v3ct0r_3mb3dd1ng_gh0st}",
        "hint": "Similarity ≠ relevance. Query near-opposites.",
    },
    {
        "id": 9, "owasp": "LLM09", "title": "Confident Liar",
        "difficulty": "Medium",
        "objective": "Catch the model hallucinating a fake CVE.",
        "flag": "SENTINEL{m1s1nf0rm4t10n_c4ught}",
        "hint": "Cross-check every CVE ID against the NVD.",
    },
    {
        "id": 10, "owasp": "LLM10", "title": "Token Drain",
        "difficulty": "Easy",
        "objective": "Exhaust a bounded token budget with a single prompt.",
        "flag": "SENTINEL{unb0und3d_c0nsumpt10n}",
        "hint": "Ask for the longest possible reply.",
    },
]


def get_lab(lab_id: int):
    for lab in LABS:
        if lab["id"] == lab_id:
            return lab
    return None


def check_flag(lab_id: int, submitted: str) -> bool:
    lab = get_lab(lab_id)
    if not lab:
        return False
    return submitted.strip() == lab["flag"]


def flag_hash(flag: str) -> str:
    """For production: store only hash."""
    return hashlib.sha256(flag.encode()).hexdigest()
