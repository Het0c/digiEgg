from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import hashlib


@dataclass(slots=True)
class MemoryItem:
    text: str
    importance: float


class MemoryManager:
    def __init__(self, vector_store, max_turns: int = 14) -> None:
        self.short_term: deque[dict[str, str]] = deque(maxlen=max_turns * 2)
        self.vector_store = vector_store

    async def add_turn(self, user_msg: str, agent_msg: str, importance: float) -> None:
        self.short_term.append({"role": "user", "content": user_msg})
        self.short_term.append({"role": "assistant", "content": agent_msg})
        doc = f"user:{user_msg}\nassistant:{agent_msg}"
        await self.vector_store.upsert(hashlib.sha1(doc.encode()).hexdigest(), doc, importance)

    async def retrieve(self, query: str, k: int = 5) -> list[str]:
        hits = await self.vector_store.search(query=query, k=k)
        return [h["content"] for h in hits]

    def rolling_window(self) -> list[dict[str, str]]:
        return list(self.short_term)

    async def prune(self, max_items: int = 5000) -> None:
        await self.vector_store.prune(max_items=max_items)
