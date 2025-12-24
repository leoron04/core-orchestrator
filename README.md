# core-orchestrator
Modular AI orchestrator with autonomous workflows, hardware abstraction, and a hacker-style TUI — designed for PC now, portable to embedded devices later.

## TUI (Textual)

Avvia l'interfaccia a schede basata su [Textual](https://www.textualize.io/) con:

```bash
python -m core.tui.app
```

Hotkey principali:

- `Ctrl+D/M/E/A/N/U`: passa rapidamente tra Dashboard, Moduli, Dispositivi, AI, Rete e Auth.
- `R`: ricarica lo snapshot dall'orchestratore (o dai dati demo).
- `1`–`6`: selezione diretta dei pannelli.
- `Q`: esci.

Per collegarlo a un orchestratore reale, inizializza l'app passando un loader personalizzato che restituisca un `OrchestratorSnapshot`:

```python
from core.tui.app import OrchestratorApp
from core.tui.state import OrchestratorSnapshot


def load_snapshot() -> OrchestratorSnapshot:
    # TODO: integra le API del tuo orchestratore
    ...

OrchestratorApp(data_loader=load_snapshot).run()
```
