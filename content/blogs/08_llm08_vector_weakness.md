# LLM08 — Vector & Embedding Weaknesses

**Risk:** Poisoned embeddings in RAG redirect the model to attacker content.

## Mitigations
- Sign and hash stored embeddings
- Validate retrieved chunks
- Cross-check similarity vs. relevance
