# LLM03 — Supply Chain

**Risk:** Compromised models, plugins, datasets, or Python packages.

## 2025 In Context
Typosquatted Hugging Face repos continued to ship malicious `pickle` files
that execute on model load.

## Mitigations
- Pin + hash dependencies
- Use `safetensors` over `pickle`
- SBOM for every model and plugin
