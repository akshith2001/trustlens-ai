from fastapi.testclient import TestClient

from trustlens.api import create_app
from trustlens.registry import FileRegistry


def test_health_and_authentication(tmp_path) -> None:
    client = TestClient(
        create_app(api_key="secret", registry_path=tmp_path / "models.json")
    )
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/v1/models").status_code == 401
    assert client.get("/v1/models", headers={"x-api-key": "wrong"}).status_code == 401
    assert client.get("/v1/models", headers={"x-api-key": "secret"}).json() == []


def test_governance_and_monitoring_endpoints(tmp_path) -> None:
    registry_path = tmp_path / "models.json"
    FileRegistry(registry_path).register(name="governed", version="1", artifact=b"x")
    client = TestClient(create_app(api_key="secret", registry_path=registry_path))
    headers = {"x-api-key": "secret"}
    response = client.post(
        "/v1/governance/evaluate",
        headers=headers,
        json={"probability": 0.9, "drift_auc": 0.8, "is_out_of_distribution": False},
    )
    assert response.status_code == 200
    assert response.json()["action"] == "pause_and_investigate"
    assert client.get("/v1/monitoring", headers=headers).json()["records"] == 1
    assert client.get("/v1/models", headers=headers).json()[0]["name"] == "governed"
    assert (
        client.post(
            "/v1/governance/evaluate", headers=headers, json={"probability": 2}
        ).status_code
        == 422
    )


def test_unconfigured_api_is_fail_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TRUSTLENS_API_KEY", raising=False)
    client = TestClient(create_app(registry_path=tmp_path / "models.json"))
    assert client.get("/v1/models").status_code == 503
