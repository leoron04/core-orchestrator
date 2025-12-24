def pytest_addoption(parser):
    option_map = getattr(parser, "_option2dest", {})
    if "--cov" not in option_map:
        group = parser.getgroup("cov")
        group.addoption("--cov", action="store", default=None, help="dummy coverage option")
    if "--cov-report" not in option_map:
        group = parser.getgroup("cov")
        group.addoption("--cov-report", action="store", default=None, help="dummy coverage report option")


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark async tests")


def pytest_pyfunc_call(pyfuncitem):
    """
    Minimal asyncio support without external plugins.
    """
    import asyncio

    if asyncio.iscoroutinefunction(pyfuncitem.obj):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
        loop.close()
        return True
    return None
