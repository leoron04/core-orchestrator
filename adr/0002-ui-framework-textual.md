# ADR 0002: UI Framework - Textual

## Status
Accepted

## Context
The orchestrator requires an operator-friendly console UI that can run in terminals, provide rich layouting (multiple panels), and integrate cleanly with async IO. The UI must be easy to script and test without heavyweight GUI stacks.

## Decision
- Adopt [Textual](https://textual.textualize.io/) as the primary TUI framework.
- Implement a six-panel layout (header, footer, controls, status, log, viewport/metrics) to reflect core telemetry and controls.
- Use Textual's async-friendly architecture to wire registry/network/auth events into the UI without blocking.

## Consequences
- Developers need familiarity with Textual conventions (compose, widgets, CSS-like styling).
- UI testing can leverage Textual's test pilot utilities for layout verification.
- Terminal compatibility is strong, but pure headless environments may require fallbacks or mocked UI interactions.
