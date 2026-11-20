# AI Decision Journal

- Chose Ollama to manage the local model runtime and avoid a manually bundled native server executable.
- Chose Qwen2.5 3B (about 1.9 GB) as a compact instruction model for CPU-first use.
- Kept deterministic Python validation and routing outside the model.
- Added a Python safety net that can promote urgency but never reduce it.
- Kept the warden as the human decision-maker for urgent tickets and ticket closure.
