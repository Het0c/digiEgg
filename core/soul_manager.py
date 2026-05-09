from __future__ import annotations

from pathlib import Path
import hashlib
import yaml
from .models import EmotionalState, InternalState, SoulSnapshot, utc_now_iso


class SoulManager:
    def __init__(self, soul_path: Path) -> None:
        self.soul_path = soul_path

    def load(self) -> SoulSnapshot:
        if not self.soul_path.exists():
            return SoulSnapshot(
                name="Tentomon",
                species="Insectoid / Data type",
                evolution_stage="Rookie",
                base_traits=["analytical", "curious", "loyal", "dry humor"],
                dynamic_traits={},
            )
        data = yaml.safe_load(self.soul_path.read_text(encoding="utf-8").split("---\n", 2)[1])
        state = InternalState(**data["dynamic_state"], emotional_state=EmotionalState(data["dynamic_state"]["emotional_state"]))
        return SoulSnapshot(
            name=data["core_identity"]["name"],
            species=data["core_identity"]["species"],
            evolution_stage=data["core_identity"]["evolution_stage"],
            base_traits=data["core_identity"]["base_traits"],
            dynamic_traits=data.get("dynamic_traits", {}),
            milestones=data.get("semantic_memory", {}).get("milestones", []),
            state=state,
            sync_version=data["metadata"]["sync_version"],
            updated_at=data["metadata"]["updated_at"],
        )

    def save(self, soul: SoulSnapshot) -> None:
        soul.updated_at = utc_now_iso()
        body = {
            "core_identity": {
                "name": soul.name,
                "species": soul.species,
                "evolution_stage": soul.evolution_stage,
                "base_traits": soul.base_traits,
            },
            "dynamic_state": {
                "curiosity": soul.state.curiosity,
                "stability": soul.state.stability,
                "energy": soul.state.energy,
                "coherence": soul.state.coherence,
                "emotional_state": soul.state.emotional_state.value,
            },
            "semantic_memory": {"milestones": soul.milestones[-50:]},
            "dynamic_traits": soul.dynamic_traits,
            "metadata": {
                "updated_at": soul.updated_at,
                "sync_version": soul.sync_version,
            },
        }
        serialized = yaml.safe_dump(body, sort_keys=False, allow_unicode=True)
        digest = hashlib.sha256(serialized.encode()).hexdigest()[:16]
        doc = f"---\n{serialized}integrity_hash: {digest}\n---\n"
        self.soul_path.write_text(doc, encoding="utf-8")

    def partial_snapshot(self, soul: SoulSnapshot) -> dict:
        return {
            "name": soul.name,
            "evolution_stage": soul.evolution_stage,
            "dynamic_state": soul.state.__dict__,
            "sync_version": soul.sync_version,
        }
