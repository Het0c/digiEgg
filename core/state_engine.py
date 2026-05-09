from __future__ import annotations

from .models import EmotionalState, InternalState


class StateEngine:
    def apply_decay(self, state: InternalState) -> None:
        state.energy -= 0.03
        state.stability -= 0.01
        state.coherence -= 0.01
        state.clamp()

    def apply_deltas(self, state: InternalState, deltas: dict[str, float]) -> None:
        for key, delta in deltas.items():
            if hasattr(state, key):
                setattr(state, key, float(getattr(state, key)) + delta)
        self._derive_emotion(state)
        state.clamp()

    def instability_score(self, state: InternalState) -> float:
        return round((1 - state.stability) * 0.5 + (1 - state.coherence) * 0.5, 3)

    def _derive_emotion(self, state: InternalState) -> None:
        if state.energy < 0.2:
            state.emotional_state = EmotionalState.TIRED
        elif state.curiosity > 0.75 and state.stability > 0.6:
            state.emotional_state = EmotionalState.INQUISITIVE
        elif state.stability < 0.4:
            state.emotional_state = EmotionalState.ERRATIC
        else:
            state.emotional_state = EmotionalState.FOCUSED
