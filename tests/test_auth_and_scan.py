import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.main import app
from app.db import Base, engine

@pytest.fixture(autouse=True, scope="function")
def _setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def _client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.anyio
async def test_signup_and_login_and_protected_routes():
    async with _client() as ac:
        r = await ac.post("/auth/signup", json={"email": "a@corp.com", "password": "secret123"})
        assert r.status_code == status.HTTP_201_CREATED
        r = await ac.post("/auth/login", data={"username": "a@corp.com", "password": "secret123"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        r = await ac.get("/scan/results", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json() == []

@pytest.mark.anyio
async def test_multitenant_isolation_and_scan_monkeypatch(monkeypatch):
    class FakePS:
        def scan(self, hosts, arguments="-F"):
            self._hosts = [hosts]
        def all_hosts(self):
            return ["127.0.0.1"]
        def __getitem__(self, host):
            return {"tcp": {22: {"state": "open", "name": "ssh", "product": "OpenSSH", "version": "8.9p1"}}}
    import app.main as mainmod
    monkeypatch.setattr(mainmod, "nmap", type("M", (), {"PortScanner": FakePS}))

    async with _client() as ac:
        await ac.post("/auth/signup", json={"email": "a2@corp.com", "password": "secret123"})
        r = await ac.post("/auth/login", data={"username": "a2@corp.com", "password": "secret123"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token_a = r.json()["access_token"]

        await ac.post("/auth/signup", json={"email": "b@corp.com", "password": "secret123"})
        r = await ac.post("/auth/login", data={"username": "b@corp.com", "password": "secret123"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token_b = r.json()["access_token"]

        r = await ac.post("/scan/network", json={"ip": "127.0.0.1"}, headers={"Authorization": f"Bearer {token_a}"})
        assert r.status_code == 200
        scan_a = r.json()
        assert scan_a["ip"] == "127.0.0.1"
        assert "scan_payload" in scan_a
        assert "127.0.0.1" in scan_a["scan_payload"]

        r = await ac.get("/scan/results", headers={"Authorization": f"Bearer {token_b}"})
        assert r.status_code == 200
        assert r.json() == []

        r = await ac.get("/scan/results", headers={"Authorization": f"Bearer {token_a}"})
        assert r.status_code == 200
        assert len(r.json()) == 1

@pytest.mark.anyio
async def test_input_validation_invalid_ip():
    async with _client() as ac:
        await ac.post("/auth/signup", json={"email": "c@corp.com", "password": "secret123"})
        r = await ac.post("/auth/login", data={"username": "c@corp.com", "password": "secret123"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = r.json()["access_token"]
        r = await ac.post("/scan/network", json={"ip": "not_an_ip"}, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 422
