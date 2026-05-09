from __future__ import annotations

import json
import time
from pathlib import Path
from .models import SyncEvent


class SyncManager:
    def __init__(self, event_log_path: Path, source: str = "desktop") -> None:
        self.event_log_path = event_log_path
        self.source = source
        self.version = 0

    def emit(self, event_type: str, payload: dict) -> SyncEvent:
        self.version += 1
        evt = SyncEvent(
            event_id=f"evt_{int(time.time() * 1000)}_{self.version}",
            event_type=event_type,
            source=self.source,
            ts=time.time(),
            version=self.version,
            payload=payload,
        )
        self.event_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.event_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evt.__dict__) + "\n")
        return evt

    def resolve_conflict_lww(self, local: dict, remote: dict) -> dict:
        return local if local["ts"] >= remote["ts"] else remote
