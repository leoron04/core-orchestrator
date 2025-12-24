import pytest

pytest.importorskip("textual")

from core.tui.app import OrchestratorApp


@pytest.mark.asyncio
async def test_tui_composes_required_panels():
    async with OrchestratorApp().run_test() as pilot:
        await pilot.pause()
        app = pilot.app
        for panel_id in [
            "header",
            "footer",
            "controls",
            "status",
            "log",
            "viewport",
            "notifications",
            "metrics",
        ]:
            assert app.query_one(f"#{panel_id}")
