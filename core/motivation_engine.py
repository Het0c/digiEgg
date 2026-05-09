from __future__ import annotations

from .models import InternalState


class MotivationEngine:
    def evaluate(self, state: InternalState, user_text: str) -> dict[str, float]:
        novelty = 0.8 if any(x in user_text.lower() for x in ("new", "unknown", "learn")) else 0.3
        curiosity_drive = state.curiosity * novelty
        loyalty_drive = min(1.0, state.stability + 0.2)
        fatigue_drive = 1 - state.energy
        attachment_drive = 0.6 if "thank" in user_text.lower() else 0.35
        priorities = {
            "curiosity": round(curiosity_drive, 3),
            "loyalty": round(loyalty_drive, 3),
            "fatigue": round(fatigue_drive, 3),
            "novelty": round(novelty, 3),
            "attachment": round(attachment_drive, 3),
        }
        return priorities

    def response_modifiers(self, priorities: dict[str, float]) -> dict[str, float | int]:
        temperature = 0.45 + priorities["novelty"] * 0.25 - priorities["fatigue"] * 0.2
        max_tokens = 450 if priorities["fatigue"] < 0.6 else 260
        return {"temperature": max(0.2, min(0.9, temperature)), "max_tokens": max_tokens}
