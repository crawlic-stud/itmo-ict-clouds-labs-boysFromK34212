from fastapi.testclient import TestClient
import pytest

from labs.lab4.src.app import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def test_response_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
