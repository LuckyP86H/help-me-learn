import pytest

SAMPLE_TEXT = """The Feynman Technique is a learning method named after physicist
Richard Feynman. It has four steps. First, choose a concept and study it.
Second, explain the concept in simple language as if teaching a child.
Third, identify gaps in your explanation and return to the source material.
Fourth, simplify further and use analogies until the explanation is clear.

Spaced repetition is a different memory technique. It schedules reviews of
material at increasing intervals: one day, three days, a week, and so on.
The spacing effect shows that information reviewed this way moves into
long-term memory far more reliably than cramming does.
""" * 3


@pytest.fixture(scope="module")
def uploaded_doc(client):
    resp = client.post(
        "/api/documents",
        files={"file": ("learning-techniques.txt", SAMPLE_TEXT, "text/plain")},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_upload_extracts_and_indexes(uploaded_doc):
    assert uploaded_doc["title"] == "learning-techniques"
    assert uploaded_doc["num_chars"] > 0
    assert uploaded_doc["num_chunks"] >= 1
    assert uploaded_doc["embedder"] == "mock"


def test_upload_rejects_unknown_extension(client):
    resp = client.post("/api/documents", files={"file": ("evil.exe", b"MZ", "application/octet-stream")})
    assert resp.status_code == 400


def test_list_documents(client, uploaded_doc):
    docs = client.get("/api/documents").json()
    assert any(d["id"] == uploaded_doc["id"] for d in docs)


def test_summarize_with_mock(client, uploaded_doc):
    resp = client.post(
        f"/api/documents/{uploaded_doc['id']}/summarize",
        json={"provider": "mock"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "summary" in data and data["summary"]
    assert data["llm_calls"] >= 1
    assert data["provider"] == "mock"


def test_ask_returns_citations(client, uploaded_doc):
    resp = client.post(
        f"/api/documents/{uploaded_doc['id']}/ask",
        json={"provider": "mock", "question": "What are the four steps of the Feynman Technique?"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["answer"]
    assert len(data["citations"]) >= 1
    top = data["citations"][0]
    assert {"n", "page", "score", "snippet"} <= set(top)
    # The lexical mock embedder should surface a Feynman-related chunk first.
    assert "feynman" in top["snippet"].lower()


def test_usage_features_recorded(client, uploaded_doc):
    usage = client.get("/api/usage").json()
    features = {row["feature"] for row in usage["by_feature"]}
    assert {"summarize", "qa"} <= features


def test_delete_document(client, uploaded_doc):
    resp = client.delete(f"/api/documents/{uploaded_doc['id']}")
    assert resp.status_code == 200
    docs = client.get("/api/documents").json()
    assert not any(d["id"] == uploaded_doc["id"] for d in docs)
