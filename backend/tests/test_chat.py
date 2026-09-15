def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_providers_include_mock(client):
    resp = client.get("/api/providers")
    assert resp.status_code == 200
    data = resp.json()
    names = [p["name"] for p in data["providers"]]
    assert "mock" in names
    mock = next(p for p in data["providers"] if p["name"] == "mock")
    assert mock["default_model"] == mock["models"][0]
    assert data["embedding_provider"] == "mock"


def test_chat_with_mock_logs_usage(client):
    resp = client.post(
        "/api/chat",
        json={
            "provider": "mock",
            "messages": [{"role": "user", "content": "Hello there, what can you do?"}],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Hello there" in data["text"]
    assert data["provider"] == "mock"
    assert data["input_tokens"] > 0
    assert data["output_tokens"] > 0

    usage = client.get("/api/usage", params={"provider": "mock", "feature": "chat"}).json()
    assert usage["totals"]["calls"] >= 1
    assert usage["by_provider"][0]["provider"] == "mock"
    assert len(usage["daily"]) >= 1


def test_chat_unknown_provider_is_400(client):
    resp = client.post(
        "/api/chat",
        json={
            "provider": "nope",
            "messages": [{"role": "user", "content": "hi"}],
        },
    )
    assert resp.status_code == 400
    assert "nope" in resp.json()["detail"]
