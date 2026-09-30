"""Short-term memory: keeps last N turns in LLM context; older turns summarized."""


class ShortTermMemory:
    def __init__(self, window: int = 8):
        self.window = window
        self.turns: list[dict] = []   # {"role": "user"|"assistant", "content": str}
        self.summary: str = ""

    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.window * 2:
            self._compress()

    def _compress(self) -> None:
        old = self.turns[: -self.window]
        # Cheap heuristic summary, NOT an LLM call
        topics = []
        for t in old:
            if t["role"] == "user":
                snippet = t["content"][:60].replace("\n", " ")
                topics.append(snippet)
        if topics:
            joined = " | ".join(topics[-5:])
            self.summary = (self.summary + " || " + joined)[-500:]
        self.turns = self.turns[-self.window :]

    def context(self) -> list[dict]:
        ctx = []
        if self.summary:
            ctx.append({"role": "system", "content": f"[Prior context: {self.summary}]"})
        ctx.extend(self.turns)
        return ctx

    def clear(self) -> None:
        self.turns = []
        self.summary = ""
