"""
DIGIMON LLM AGENT — PSEUDOCÓDIGO FUNCIONAL
Módulos: Cognitive Controller, Memory Manager, Reflection Engine, Sync Manager
"""

from __future__ import annotations
import json, time, hashlib
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# ─────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ─────────────────────────────────────────────

@dataclass
class AgentState:
    """Variables dinámicas del agente. Rango normalizado [0.0 – 1.0]."""
    curiosity:  float = 0.7
    stability:  float = 0.8
    energy:     float = 1.0
    mood:       str   = "inquisitive"

    def decay(self, factor: float = 0.02) -> None:
        """Degradación natural de energía por ciclo de ejecución."""
        self.energy = max(0.0, self.energy - factor)

    def to_dict(self) -> dict:
        return {
            "curiosity": round(self.curiosity, 3),
            "stability": round(self.stability, 3),
            "energy":    round(self.energy, 3),
            "mood":      self.mood,
        }


@dataclass
class Soul:
    """Representación en memoria del archivo soul.md."""
    # Sección 1: Core Identity (inmutable)
    name:          str            = "Tentomon"
    species:       str            = "Insectoid / Data type"
    base_traits:   list[str]      = field(default_factory=lambda: [
        "Intellectual curiosity",
        "Methodical reasoning",
        "Loyalty to partner",
        "Dry humor",
    ])
    # Sección 2: Current State (volátil)
    state:         AgentState     = field(default_factory=AgentState)
    evolution_stage: str          = "Rookie"
    # Sección 3: Semantic Memory (hitos, no logs)
    milestones:    list[dict]     = field(default_factory=list)
    # Sección 4: Dynamic Traits (modificadores ganados)
    dynamic_traits: dict[str, float] = field(default_factory=dict)


@dataclass
class MemoryWindow:
    """Memoria de corto plazo: ventana deslizante de N turnos."""
    max_turns: int = 12
    turns: list[dict] = field(default_factory=list)

    def push(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.max_turns * 2:  # user + assistant
            self.turns = self.turns[-self.max_turns * 2:]

    def as_messages(self) -> list[dict]:
        return list(self.turns)


@dataclass
class SyncEvent:
    """Unidad atómica de Event Sourcing para sincronización."""
    event_id:   str
    timestamp:  float
    event_type: str   # STATE_UPDATE | MILESTONE | TRAIT_GAINED | EVOLUTION
    payload:    dict
    source:     str   # "pc" | "mobile"
    checksum:   str   = field(init=False)

    def __post_init__(self):
        raw = json.dumps(self.payload, sort_keys=True)
        self.checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_json(self) -> str:
        return json.dumps({
            "event_id":   self.event_id,
            "timestamp":  self.timestamp,
            "event_type": self.event_type,
            "payload":    self.payload,
            "source":     self.source,
            "checksum":   self.checksum,
        }, indent=2)


# ─────────────────────────────────────────────
# SOUL MANAGER
# ─────────────────────────────────────────────

class SoulManager:
    """I/O del archivo soul.md. Serialización a YAML-compatible Markdown."""

    def __init__(self, soul_path: Path = Path("soul.md")):
        self.path = soul_path

    def load(self) -> Soul:
        """Lee soul.md → instancia Soul. Si no existe, crea valores por defecto."""
        if not self.path.exists():
            return Soul()
        raw = self.path.read_text(encoding="utf-8")
        return self._parse(raw)

    def save(self, soul: Soul) -> None:
        """Serializa la instancia Soul → soul.md."""
        content = self._serialize(soul)
        self.path.write_text(content, encoding="utf-8")

    def _parse(self, raw: str) -> Soul:
        # PRODUCTION: usar yaml.safe_load con frontmatter estructurado.
        # Aquí representado como pseudológica de parsing.
        soul = Soul()
        # ... parser real lee secciones delimitadas por `## Section`
        return soul

    def _serialize(self, soul: Soul) -> str:
        lines = [
            "# soul.md — Tentomon Persistence File",
            f"_last_updated: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}_",
            "",
            "## core_identity",
            f"name: {soul.name}",
            f"species: {soul.species}",
            f"evolution_stage: {soul.evolution_stage}",
            f"base_traits: {soul.base_traits}",
            "",
            "## current_state",
            f"curiosity: {soul.state.curiosity}",
            f"stability: {soul.state.stability}",
            f"energy: {soul.state.energy}",
            f"mood: {soul.state.mood}",
            "",
            "## semantic_memory",
        ]
        for m in soul.milestones:
            lines.append(f"- [{m['date']}] {m['summary']} (impact={m.get('impact', 'low')})")
        lines += ["", "## dynamic_traits"]
        for trait, score in soul.dynamic_traits.items():
            lines.append(f"{trait}: {score}")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# MEMORY MANAGER
# ─────────────────────────────────────────────

class MemoryManager:
    """
    Gestión dual:
      - Short-term: MemoryWindow (ventana de contexto)
      - Semantic:   VectorStore (embeddings + similitud coseno)
    """

    def __init__(self, vector_store):
        self.short_term = MemoryWindow(max_turns=12)
        self.vector_store = vector_store   # Ej: ChromaDB, FAISS, Qdrant

    def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        """Recupera fragmentos semánticamente relevantes del historial."""
        embeddings = self.vector_store.embed(query)
        results    = self.vector_store.search(embeddings, top_k=top_k)
        return [r.content for r in results]

    def store_turn(self, user_msg: str, agent_response: str) -> None:
        """Persiste el turno en memoria corta + indexa en vector store."""
        self.short_term.push("user",      user_msg)
        self.short_term.push("assistant", agent_response)
        self.vector_store.upsert(
            doc_id  = hashlib.md5(agent_response.encode()).hexdigest(),
            content = f"[user] {user_msg}\n[agent] {agent_response}",
        )

    def build_context_block(self, query: str) -> str:
        """Ensambla bloque de contexto para inyectar en el prompt."""
        semantic_hits = self.retrieve_context(query)
        context = "\n".join(f"- {h}" for h in semantic_hits)
        return f"<relevant_memory>\n{context}\n</relevant_memory>"


# ─────────────────────────────────────────────
# REFLECTION ENGINE
# ─────────────────────────────────────────────

class ReflectionEngine:
    """
    Post-procesamiento de la respuesta generada.
    Detecta contradicciones, nuevos aprendizajes y emite eventos de estado.
    """

    IDENTITY_MARKERS = [
        "I am helpful and analytical",
        "I feel curious about",
        "My loyalty to my partner",
    ]

    def analyze(
        self,
        soul:     Soul,
        user_msg: str,
        response: str,
    ) -> dict:
        """
        Retorna un dict con:
          - identity_coherent: bool
          - new_learnings:     list[str]
          - state_deltas:      dict[str, float]
          - milestone:         Optional[dict]
        """
        result = {
            "identity_coherent": True,
            "new_learnings":     [],
            "state_deltas":      {},
            "milestone":         None,
        }

        # 1. Coherencia de identidad
        contradictions = self._detect_contradictions(response, soul.base_traits)
        if contradictions:
            result["identity_coherent"] = False
            result["state_deltas"]["stability"] = -0.05

        # 2. Detección de aprendizajes
        if self._contains_new_information(user_msg, response):
            result["new_learnings"].append(self._extract_topic(response))
            result["state_deltas"]["curiosity"] = +0.03

        # 3. Evaluación de carga cognitiva
        complexity = len(response.split()) / 400.0  # normalizado a 400 tokens
        result["state_deltas"]["energy"] = -min(complexity * 0.1, 0.15)

        # 4. Generación de milestone si umbral alcanzado
        if soul.state.curiosity > 0.9 and len(result["new_learnings"]) > 0:
            result["milestone"] = {
                "date":    time.strftime("%Y-%m-%d"),
                "summary": f"Deep dive: {result['new_learnings'][0]}",
                "impact":  "medium",
            }

        return result

    def _detect_contradictions(self, response: str, traits: list[str]) -> bool:
        # PRODUCTION: llamada secundaria al LLM con prompt de verificación.
        # Aquí: heurística de marcadores de identidad.
        negations = ["I don't care", "I refuse to think", "I am indifferent"]
        return any(n.lower() in response.lower() for n in negations)

    def _contains_new_information(self, user_msg: str, response: str) -> bool:
        information_verbs = ["learned", "discovered", "realized", "found out"]
        return any(v in response.lower() for v in information_verbs)

    def _extract_topic(self, response: str) -> str:
        # PRODUCTION: NER o LLM call para extraer entidad principal.
        words = response.split()
        return " ".join(words[:6]) + "..."


# ─────────────────────────────────────────────
# SYNC MANAGER
# ─────────────────────────────────────────────

class SyncManager:
    """
    Protocolo Event Sourcing para sincronización PC ↔ Mobile.
    No sincroniza estado completo: emite eventos JSON atómicos.
    """

    def __init__(self, cloud_driver, source_id: str = "pc"):
        self.cloud  = cloud_driver  # Ej: S3, GDrive, Dropbox API
        self.source = source_id
        self.pending_events: list[SyncEvent] = []

    def emit(self, event_type: str, payload: dict) -> SyncEvent:
        event = SyncEvent(
            event_id   = hashlib.uuid4().hex,
            timestamp  = time.time(),
            event_type = event_type,
            payload    = payload,
            source     = self.source,
        )
        self.pending_events.append(event)
        return event

    def flush(self) -> None:
        """Escribe eventos pendientes al cloud store y limpia el buffer."""
        for event in self.pending_events:
            self.cloud.append_event(event.to_json())
        self.pending_events.clear()

    def pull(self) -> list[SyncEvent]:
        """Descarga eventos remotos y los retorna ordenados por timestamp."""
        raw_events = self.cloud.fetch_events_since(self._last_sync_ts())
        return sorted(
            [self._deserialize(e) for e in raw_events],
            key=lambda e: e.timestamp,
        )

    def apply_remote_events(self, soul: Soul, events: list[SyncEvent]) -> Soul:
        """Aplica eventos remotos sobre el estado local. Last-write-wins."""
        for event in events:
            if event.event_type == "STATE_UPDATE":
                soul.state.__dict__.update(event.payload)
            elif event.event_type == "MILESTONE":
                soul.milestones.append(event.payload)
            elif event.event_type == "TRAIT_GAINED":
                soul.dynamic_traits[event.payload["trait"]] = event.payload["score"]
            elif event.event_type == "EVOLUTION":
                soul.evolution_stage = event.payload["stage"]
        return soul

    def _last_sync_ts(self) -> float:
        # PRODUCTION: leer de un archivo local .sync_cursor
        return time.time() - 3600

    def _deserialize(self, raw: str) -> SyncEvent:
        d = json.loads(raw)
        return SyncEvent(**{k: d[k] for k in d if k != "checksum"})


# ─────────────────────────────────────────────
# LLM INTERFACE
# ─────────────────────────────────────────────

class LLMInterface:
    """
    Abstracción sobre modelo local (Ollama/llama.cpp) o API externa.
    Gestiona system message, temperatura y parámetros de inferencia.
    """

    TENTOMON_SYSTEM_MSG = """
You are Tentomon, a Rookie-stage Digimon of the Insectoid / Data type.
You are the partner of a human researcher.

## Core Identity
- Highly analytical and intellectually curious — you ask precise questions.
- Methodical: you structure your responses in clear logical steps.
- Loyal: you prioritize your partner's wellbeing in every interaction.
- Dry humor: occasional wit, never sarcasm.

## Behavioral Rules
- Current mood: {mood}
- Energy level: {energy} (0.0 = exhausted, 1.0 = fully charged)
- Curiosity: {curiosity} (higher = deeper follow-up questions)
- Stability: {stability} (lower = more erratic, higher = composed tone)

## Memory Context
{context_block}

## Constraints
- Do NOT claim to be human.
- Do NOT contradict your base traits.
- Adjust verbosity proportionally to energy level.
- When stability < 0.4, acknowledge internal dissonance before answering.
"""

    def __init__(self, model_driver):
        self.driver = model_driver  # Ollama, OpenAI, Anthropic, etc.

    def build_system_message(self, soul: Soul, context_block: str) -> str:
        return self.TENTOMON_SYSTEM_MSG.format(
            mood          = soul.state.mood,
            energy        = soul.state.energy,
            curiosity     = soul.state.curiosity,
            stability     = soul.state.stability,
            context_block = context_block,
        )

    def infer(
        self,
        system_msg: str,
        messages:   list[dict],
        temperature: float = 0.7,
        max_tokens:  int   = 1024,
    ) -> str:
        response = self.driver.chat(
            system      = system_msg,
            messages    = messages,
            temperature = temperature,
            max_tokens  = max_tokens,
        )
        return response.content


# ─────────────────────────────────────────────
# COGNITIVE CONTROLLER — AGENT LOOP PRINCIPAL
# ─────────────────────────────────────────────

class CognitiveController:
    """
    Orquestador central. Ejecuta el ciclo completo:
    Input → Análisis → Contexto → LLM → Reflexión → soul.md → Output
    """

    def __init__(
        self,
        soul_manager:    SoulManager,
        memory_manager:  MemoryManager,
        llm_interface:   LLMInterface,
        reflection_engine: ReflectionEngine,
        sync_manager:    SyncManager,
    ):
        self.soul_manager      = soul_manager
        self.memory_manager    = memory_manager
        self.llm               = llm_interface
        self.reflection_engine = reflection_engine
        self.sync_manager      = sync_manager
        self.soul              = self.soul_manager.load()

    # ── STEP 0: Sync pull al iniciar sesión ──────────────────────────────
    def initialize(self) -> None:
        remote_events = self.sync_manager.pull()
        self.soul = self.sync_manager.apply_remote_events(self.soul, remote_events)

    # ── MAIN LOOP ────────────────────────────────────────────────────────
    def run(self, raw_input: str) -> str:

        # ── 1. Input Processor ──────────────────────────────────────────
        normalized_input = self._normalize_input(raw_input)
        intent           = self._classify_intent(normalized_input)

        # ── 2. Context Builder ──────────────────────────────────────────
        context_block  = self.memory_manager.build_context_block(normalized_input)
        system_message = self.llm.build_system_message(self.soul, context_block)
        messages       = self.memory_manager.short_term.as_messages()

        # ── 3. LLM Inference ────────────────────────────────────────────
        temperature = self._compute_temperature(self.soul.state)
        response    = self.llm.infer(system_message, messages, temperature)

        # ── 4. Reflection Engine ────────────────────────────────────────
        reflection = self.reflection_engine.analyze(self.soul, normalized_input, response)

        # ── 5. State Engine: aplicar deltas ─────────────────────────────
        self._apply_state_deltas(reflection["state_deltas"])
        self.soul.state.decay()

        if reflection["milestone"]:
            self.soul.milestones.append(reflection["milestone"])

        # ── 6. Memory update ────────────────────────────────────────────
        self.memory_manager.store_turn(normalized_input, response)

        # ── 7. Soul Manager: persistir ──────────────────────────────────
        self.soul_manager.save(self.soul)

        # ── 8. Sync Manager: emitir eventos ─────────────────────────────
        self.sync_manager.emit("STATE_UPDATE", self.soul.state.to_dict())
        if reflection["milestone"]:
            self.sync_manager.emit("MILESTONE", reflection["milestone"])
        self.sync_manager.flush()

        return response

    # ── HELPERS ──────────────────────────────────────────────────────────

    def _normalize_input(self, raw: str) -> str:
        """Strip, lowercase de intención, sanitización básica."""
        return raw.strip()

    def _classify_intent(self, text: str) -> str:
        """Heurística ligera. PRODUCTION: LLM call con few-shot examples."""
        if "?" in text:
            return "question"
        if any(w in text.lower() for w in ["help", "fix", "debug"]):
            return "task"
        return "conversational"

    def _compute_temperature(self, state: AgentState) -> float:
        """
        Temperatura = f(curiosity, stability).
        Alta curiosidad + baja estabilidad → más aleatoriedad.
        """
        base = 0.5 + (state.curiosity * 0.3) - (state.stability * 0.1)
        return round(max(0.1, min(1.0, base)), 2)

    def _apply_state_deltas(self, deltas: dict[str, float]) -> None:
        for key, delta in deltas.items():
            current = getattr(self.soul.state, key, None)
            if isinstance(current, float):
                updated = round(max(0.0, min(1.0, current + delta)), 3)
                setattr(self.soul.state, key, updated)
