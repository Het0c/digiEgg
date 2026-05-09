from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class EmotionalState(str, Enum):
    INQUISITIVE = "inquisitive"
    FOCUSED = "focused"
    PLAYFUL = "playful"
    TIRED = "tired"
    PROTECTIVE = "protective"
    ERRATIC = "erratic"


@dataclass(slots=True)
class InternalState:
    curiosity: float = 0.7
    stability: float = 0.8
    energy: float = 0.9
    coherence: float = 0.85
    emotional_state: EmotionalState = EmotionalState.INQUISITIVE

    def clamp(self) -> None:
        for key in ("curiosity", "stability", "energy", "coherence"):
            setattr(self, key, max(0.0, min(1.0, getattr(self, key))))


@dataclass(slots=True)
class SoulSnapshot:
    name: str
    species: str
    evolution_stage: str
    base_traits: list[str]
    dynamic_traits: dict[str, float]
    state: InternalState = field(default_factory=InternalState)
    milestones: list[dict[str, Any]] = field(default_factory=list)
    sync_version: int = 0
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class SyncEvent:
    event_id: str
    event_type: str
    source: str
    ts: float
    version: int
    payload: dict[str, Any]
