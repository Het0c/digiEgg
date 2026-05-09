from __future__ import annotations


class ReflectionEngine:
    def analyze(self, response: str, state_before: dict, user_text: str) -> dict:
        contradictions = "I cannot" in response and "I already did" in response
        gratitude = "thank" in user_text.lower()
        learning_event = any(k in user_text.lower() for k in ("learn", "remember", "important"))
        deltas = {
            "stability": -0.05 if contradictions else 0.01,
            "coherence": -0.04 if contradictions else 0.01,
            "curiosity": 0.03 if learning_event else 0.0,
            "energy": -0.02,
        }
        milestone = None
        if learning_event or gratitude:
            milestone = {
                "summary": user_text[:180],
                "impact": "high" if learning_event else "medium",
                "tags": ["learning"] if learning_event else ["bond"],
            }
        return {
            "contradiction": contradictions,
            "deltas": deltas,
            "importance": 0.8 if learning_event else 0.45,
            "milestone": milestone,
        }
