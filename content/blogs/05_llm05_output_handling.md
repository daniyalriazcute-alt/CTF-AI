# LLM05 — Improper Output Handling

**Risk:** Downstream systems trust model output without validation.

## 2025 In Context
XSS-in-chat and SSRF-via-tool-call incidents traced to unescaped LLM output.

## Mitigations
- Escape all LLM output before rendering
- Treat model output as untrusted user input
- Allow-list tools and arguments
