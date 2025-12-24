# core-orchestrator

Modular AI orchestrator with autonomous workflows, hardware abstraction, and a hacker-style TUI — designed for PC now, portable to embedded devices later.

## Architecture (v0.1)

```
                         +-------------------------+
                         |       CLI / TUI         |
                         +------------+------------+
                                      |
                           +----------v----------+
                           |     AI Engine       |
                           | (policy & perms)    |
                           +----------+----------+
                                      |
                 +--------------------+----------------------+
                 |                                           |
        +--------v--------+                        +---------v---------+
        |  Tool Dispatcher|                        |   AI Providers    |
        |  (validation)   |                        | OpenAI/Gemini/etc |
        +--------+--------+                        +---------+---------+
                 |                                           |
        +--------v--------+                        +---------v---------+
        |   Modules       |                        |  Memory Store     |
        | Notes/Routine/  |                        |  Events & Facts   |
        | Health/Security |                        +---------+---------+
        +-----------------+                                  |
                                      +-----------------------v------+
                                      |       NetworkManager         |
                                      |   Connectivity FSM & checks  |
                                      +------------------------------+
```

## Setup

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run tests**

   ```bash
   pytest
   ```

3. **Lint and format**

   ```bash
   ruff check .
   black --check .
   ```

4. **Environment variables (optional)**

   - `OPENAI_API_KEY` for OpenAIProvider online mode
   - `GEMINI_API_KEY` for GeminiProvider online mode
   - Custom providers accept an arbitrary HTTP endpoint URL.

## Roadmap

- **v0.2**
  - Expand module catalogue (automation, hardware abstraction)
  - Conversation-aware memory with embeddings
  - Plugin loader for external tools
- **v1.0**
  - Production-grade policy enforcement
  - TUI/GUI shell
  - Streaming AI responses and telemetry dashboard
