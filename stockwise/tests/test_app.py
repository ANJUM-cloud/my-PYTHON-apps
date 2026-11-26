import pytest
from app import create_app

@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(tmp_path / "test.db"), "SECRET_KEY": "test-secret"})
    with app.test_client() as client:
        yield client

def test_home_and_health(client):
    assert client.get("/").status_code == 200
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json["status"] == "ok"

def test_registration_and_dashboard(client):
    response = client.post("/register", data={"email":"learner@example.com","password":"correct-horse-battery"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"StockWise" in response.data

def test_short_password_rejected(client):
    response = client.post("/register", data={"email":"short@example.com","password":"tiny"}, follow_redirects=True)
    assert b"at least 10 characters" in response.data
