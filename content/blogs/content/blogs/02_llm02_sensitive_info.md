# LLM02 — Sensitive Information Disclosure

**Risk:** The model leaks PII, credentials, or proprietary data.

## 2025 In Context
Multiple reports of Copilot-style assistants surfacing internal HR data
through "helpful" summarization.

## Mitigations
- PII scrubbers on input and output
- Data minimization in fine-tuning
- Red-team prompts before deployment
- Restrict retrieval scopes per user
