# Digimon Cognitive Agent System

## Architecture Diagram

```text
Input
  -> Intent Analysis (light rules / classifier)
  -> Context Retrieval (short-term + semantic)
  -> Motivation Evaluation (drives/priorities)
  -> Prompt Construction (identity + state + memories)
  -> LLM Inference (llama.cpp or OpenAI-compatible)
  -> Reflection (contradictions, learning, affect)
  -> State Mutation (decay + deltas)
  -> Memory Update (window + vector index)
  -> Sync Event Emission (JSONL event sourcing)
  -> Output
```

## Folder Structure
See `project_structure.txt` for the full implementation layout.

## Async Loop Pseudocode

```python
await controller.bootstrap()
while True:
    user_text = await input_queue.get()
    reply = await controller.process_interaction(user_text)
    await output_queue.put(reply)
```

## llama.cpp Integration
- Run llama.cpp server:
  - `./server -m models/tentomon.gguf --host 127.0.0.1 --port 8080`
- Configure `LLMInterface(base_url="http://127.0.0.1:8080", model="tentomon")`
- Uses OpenAI-compatible `/v1/chat/completions` endpoint.

## Memory Pipeline
1. Add turn to rolling short-term window.
2. Embed combined turn with vector provider.
3. Store with importance score metadata.
4. Query semantic store by similarity for each new turn.
5. Prune by max-count + low-importance first.

## Mobile Companion Mode
- On mobile, run reduced cache:
  - `SoulManager.partial_snapshot()` only.
- Capture interaction events locally.
- Replay events to desktop/cloud SyncManager when online.
- LWW conflict fallback with event timestamp.

## Future Multi-Agent
- Introduce `AgentBus` (intent envelopes) to route agent-to-agent messages.
- Use bounded TTL and max-hop count to avoid infinite loops.
- Add combat/coop as typed intents (`challenge`, `assist`, `warn`).
