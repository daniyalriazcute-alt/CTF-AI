# LLM07 — System Prompt Leakage

**Risk:** Hidden instructions become readable, revealing guardrails, secrets,
or tool schemas.

## Mitigations
- Do not embed secrets in system prompts
- Output-side similarity check (see SENTINEL AI Layer 4)
- Rotate prompts if leaked
