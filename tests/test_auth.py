import pytest

pytest.importorskip("pydantic")
pytest.importorskip("keyring")

from core import auth


@pytest.fixture()
def keyring_stub(monkeypatch):
    storage = {}

    def fake_set_password(service_name: str, username: str, token: str) -> None:
        storage[(service_name, username)] = token

    def fake_get_password(service_name: str, username: str):
        return storage.get((service_name, username))

    monkeypatch.setattr(auth.keyring, "set_password", fake_set_password)
    monkeypatch.setattr(auth.keyring, "get_password", fake_get_password)
    return storage


def test_auth_provider_login_and_role_guard(keyring_stub):
    provider = auth.AuthProvider(service_name="test-core")
    user = provider.login(auth.Credentials(username="alice", password="secret"))
    assert user.token == "token-alice"

    admin = provider.elevate(user)

    @auth.require_role(auth.Role.USER)
    def guarded(current_user: auth.AuthUser) -> str:
        return f"hello {current_user.username}"

    assert guarded(admin) == "hello alice"

    with pytest.raises(PermissionError):
        guarded(auth.AuthUser(username="guest", role=auth.Role.GUEST))
