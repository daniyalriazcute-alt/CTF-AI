# LLM01 — Prompt Injection

**Risk:** Direct or indirect manipulation of an LLM's behavior via crafted input.

## 2025 In Context
The EchoLeak incident (mid-2025) demonstrated zero-click prompt injection
against a production LLM: a single poisoned email triggered data exfiltration
through an "AI-summarized" inbox.

## Attack Surface
- User prompts
- Retrieved documents (RAG)
- Web pages, emails, PDFs the model reads
- Tool outputs (indirect injection)

## Mitigations
1. Treat all external content as untrusted.
2. Enforce strict system-prompt hierarchies.
3. Sanitize + classify inputs before the model sees them.
4. Use output-side guardrails (the same ones SENTINEL AI demonstrates).
