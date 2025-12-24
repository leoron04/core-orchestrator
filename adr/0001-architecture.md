# ADR 0001: Core Orchestrator Architecture

## Status
Accepted

## Context
We need a modular orchestrator that can combine AI tools, networking, authentication, and hardware abstractions while remaining portable from PC to embedded targets. The system must be introspectable via manifests to drive both automation and operator interfaces.

## Decision
- Use a registry-first design: tool/action capabilities are declared as JSON manifests, validated via Pydantic, and loaded by a central `Registry` service.
- Keep network operations asynchronous with a small state machine (`NetworkManager`) to handle retries and expose hooks for UI updates.
- Model authentication with Pydantic/SQLAlchemy, leveraging OS keyring for token persistence where available.
- Provide a Textual TUI to surface status, controls, logs, and diagnostics in a multi-panel layout suitable for constrained environments.
- Maintain AI protocol artifacts (`ai/protocol`) aligned with registry manifests to document available tools.

## Consequences
- New capabilities are added declaratively via manifests, keeping code changes minimal.
- Async networking and clear states simplify resilience and observability but require event loop integration in clients.
- Using keyring introduces platform differences; fallbacks may be needed on environments without a keychain.
- Textual dependency requires a modern terminal; alternate UIs may be required for headless deployments.
