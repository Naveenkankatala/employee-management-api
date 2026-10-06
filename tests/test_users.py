from fastapi.testclient import TestClient
import uuid
import os

from app.main import app


client = TestClient(app)


def get_admin_token():
    response = client.post(
        "/login",
        data={
            "username": "Naveen2",
            "password": "Naveen@1"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "admin"
    assert "access_token" in data

    return data["access_token"], data["user_id"]


def get_user_token():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "Test@12345"

    register_response = client.post(
        "/register",
        json={
            "username": username,
            "password": password
        }
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    return data["access_token"], data["user_id"]


def test_admin_can_get_users():
    token, _ = get_admin_token()

    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "users" in response.json()


def test_user_cannot_get_users():
    token, _ = get_user_token()

    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_cannot_change_own_role():
    token, user_id = get_admin_token()

    response = client.put(
        f"/users/{user_id}/role?role=user",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot change your own role"


def test_invalid_role():
    admin_token, _ = get_admin_token()

    user_token, user_id = get_user_token()

    response = client.put(
        f"/users/{user_id}/role?role=manager",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Role must be either 'admin' or 'user'"
    )


def test_admin_can_change_user_role():
    admin_token, _ = get_admin_token()

    user_token, user_id = get_user_token()

    response = client.put(
        f"/users/{user_id}/role?role=admin",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User role updated successfully"
    assert data["user"]["id"] == user_id
    assert data["user"]["role"] == "admin"


def test_user_cannot_change_role():
    user_token, user_id = get_user_token()

    response = client.put(
        f"/users/{user_id}/role?role=admin",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_cannot_delete_own_account():
    token, user_id = get_admin_token()

    response = client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "You cannot delete your own account"
    )


def test_admin_can_delete_user():
    admin_token, _ = get_admin_token()

    user_token, user_id = get_user_token()

    response = client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User deleted successfully"


def test_user_cannot_delete_user():
    user_token, _ = get_user_token()

    response = client.delete(
        "/users/1",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"