from fastapi.testclient import TestClient
from .discount import app


client = TestClient(app)


def test_generate():
    response = client.post("/generate/foo")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert len(data["result"]) == 10


def test_generate_with_number():
    for n in (1, 11, 125, 1000):
        response = client.post("/generate/foo?number=%d" % n)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert len(data["result"]) == n


def test_generate_over_limit():
    response = client.post("/generate/foo?number=150000")
    assert response.status_code == 400


def test_fetch():
    client.post("/generate/foo")
    response = client.post("/fetch/foo")
    assert response.status_code == 200
    assert "result" in response.json()

    response1 = client.post("/fetch/foo")
    assert response1.status_code == 200
    assert "result" in response1.json()
    assert response.json()["result"] != response1.json()["result"]


def test_fetch_empty():
    response = client.post("/fetch/bar")
    assert response.status_code == 404
