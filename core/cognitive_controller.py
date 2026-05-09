from __future__ import annotations

from dataclasses import asdict
from .memory_manager import MemoryManager
from .motivation_engine import MotivationEngine
from .reflection_engine import ReflectionEngine
from .soul_manager import SoulManager
from .state_engine import StateEngine
from .sync_manager import SyncManager


class CognitiveController:
    def __init__(self, soul_manager: SoulManager, memory: MemoryManager, llm, sync: SyncManager) -> None:
        self.soul_manager = soul_manager
        self.memory = memory
        self.llm = llm
        self.sync = sync
        self.state_engine = StateEngine()
        self.motivation = MotivationEngine()
        self.reflection = ReflectionEngine()
        self.soul = self.soul_manager.load()

    async def bootstrap(self) -> None:
        self.sync.version = self.soul.sync_version

    async def process_interaction(self, user_text: str) -> str:
        context = await self.memory.retrieve(user_text, k=4)
        priorities = self.motivation.evaluate(self.soul.state, user_text)
        sampling = self.motivation.response_modifiers(priorities)
        messages = self._build_messages(user_text, context, priorities)
        response = await self.llm.generate(messages, **sampling)
        reflection = self.reflection.analyze(response, asdict(self.soul.state), user_text)
        self.state_engine.apply_deltas(self.soul.state, reflection["deltas"])
        await self.memory.add_turn(user_text, response, importance=reflection["importance"])
        if reflection["milestone"]:
            self.soul.milestones.append(reflection["milestone"])
            self.sync.emit("MILESTONE", reflection["milestone"])
        self.sync.emit("STATE_UPDATE", asdict(self.soul.state))
        self.soul.sync_version = self.sync.version
        return response

    async def shutdown(self) -> None:
        await self.memory.prune()
        self.soul_manager.save(self.soul)

    def _build_messages(self, user_text: str, context: list[str], priorities: dict[str, float]) -> list[dict[str, str]]:
        system = (
            f"You are {self.soul.name}, a {self.soul.species} Digimon companion. "
            f"Base traits: {', '.join(self.soul.base_traits)}. "
            f"Dynamic traits: {self.soul.dynamic_traits}. "
            f"State: {asdict(self.soul.state)}. Motivation priorities: {priorities}."
        )
        memory_block = "\n".join(f"- {c}" for c in context)
        return [
            {"role": "system", "content": system},
            {"role": "system", "content": f"Relevant memories:\n{memory_block}"},
            *self.memory.rolling_window(),
            {"role": "user", "content": user_text},
        ]
