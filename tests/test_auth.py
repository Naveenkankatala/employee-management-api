from fastapi.testclient import TestClient
import uuid
import os

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Employee Management API is running"


def test_register_user():
    username = f"testuser_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/register",
        json={
            "username": username,
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


def test_login_user():
    response = client.post(
        "/login",
        data={
            "username": "testuser_automation2",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "user"
    assert "user_id" in data


def test_invalid_login():
    response = client.post(
        "/login",
        data={
            "username": "testuser_automation2",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"