from fastapi.testclient import TestClient
import uuid
import os

from app.main import app
from tests.conftest import (
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
)


client = TestClient(app)


# --------------------------------------------------
# Helper: Get normal user JWT token
# --------------------------------------------------

def get_user_token():
    response = client.post(
        "/login",
        data={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "user"
    assert "access_token" in data

    return data["access_token"]


# --------------------------------------------------
# Helper: Get admin JWT token
# --------------------------------------------------

def get_admin_token():
    response = client.post(
        "/login",
        data={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "admin"
    assert "access_token" in data

    return data["access_token"]


# --------------------------------------------------
# Test 1: Authenticated user can get employees
# --------------------------------------------------

def test_get_employees_authenticated():

    token = get_user_token()

    response = client.get(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "employees" in response.json()


# --------------------------------------------------
# Test 2: User without JWT cannot get employees
# --------------------------------------------------

def test_get_employees_without_token():

    response = client.get("/employees")

    assert response.status_code == 401


# --------------------------------------------------
# Test 3: User cannot create employee
# --------------------------------------------------

def test_user_cannot_create_employee():

    token = get_user_token()

    email = f"user_create_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Employee",
            "email": email,
            "department": "Testing",
            "salary": 30000
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


# --------------------------------------------------
# Test 4: Admin can create employee
# --------------------------------------------------

def test_admin_can_create_employee():

    token = get_admin_token()

    email = f"admin_create_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Automation Employee",
            "email": email,
            "department": "Testing",
            "salary": 40000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Employee created successfully"
    assert data["employee"]["name"] == "Automation Employee"
    assert data["employee"]["email"] == email
    assert data["employee"]["department"] == "Testing"
    assert data["employee"]["salary"] == 40000


# --------------------------------------------------
# Test 5: Admin can get single employee
# --------------------------------------------------

def test_admin_can_get_single_employee():

    token = get_admin_token()

    email = f"single_{uuid.uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Single Employee",
            "email": email,
            "department": "Testing",
            "salary": 35000
        }
    )

    assert create_response.status_code == 200

    employee_id = create_response.json()["employee"]["id"]

    response = client.get(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == employee_id
    assert data["email"] == email


# --------------------------------------------------
# Test 6: Employee not found
# --------------------------------------------------

def test_employee_not_found():

    token = get_user_token()

    response = client.get(
        "/employees/99999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


# --------------------------------------------------
# Test 7: Duplicate employee email
# --------------------------------------------------

def test_duplicate_employee_email():

    token = get_admin_token()

    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

    first_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "First Employee",
            "email": email,
            "department": "Testing",
            "salary": 30000
        }
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Second Employee",
            "email": email,
            "department": "Testing",
            "salary": 40000
        }
    )

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "An employee with this email already exists"
    )


# --------------------------------------------------
# Test 8: Admin can update employee
# --------------------------------------------------

def test_admin_can_update_employee():

    token = get_admin_token()

    # Generate unique email
    email = f"update_{uuid.uuid4().hex[:8]}@example.com"

    # Create employee
    create_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Update Test Employee",
            "email": email,
            "department": "Testing",
            "salary": 40000
        }
    )

    assert create_response.status_code == 200

    employee_id = create_response.json()["employee"]["id"]

    # Update employee
    update_response = client.put(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Updated Automation Employee",
            "email": email,
            "department": "Data Science",
            "salary": 50000
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["message"] == "Employee updated successfully"
    assert data["employee"]["name"] == "Updated Automation Employee"
    assert data["employee"]["email"] == email
    assert data["employee"]["department"] == "Data Science"
    assert data["employee"]["salary"] == 50000


# --------------------------------------------------
# Test 9: Normal user cannot update employee
# --------------------------------------------------

def test_user_cannot_update_employee():

    admin_token = get_admin_token()

    email = f"protected_update_{uuid.uuid4().hex[:8]}@example.com"

    # Admin creates employee
    create_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "Protected Employee",
            "email": email,
            "department": "Testing",
            "salary": 40000
        }
    )

    assert create_response.status_code == 200

    employee_id = create_response.json()["employee"]["id"]

    # Normal user gets token
    user_token = get_user_token()

    # Normal user tries to update
    response = client.put(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json={
            "name": "Unauthorized Update",
            "email": email,
            "department": "Testing",
            "salary": 1
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


# --------------------------------------------------
# Test 10: Admin can delete employee
# --------------------------------------------------

def test_admin_can_delete_employee():

    token = get_admin_token()

    email = f"delete_{uuid.uuid4().hex[:8]}@example.com"

    # Create employee
    create_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Delete Test Employee",
            "email": email,
            "department": "Testing",
            "salary": 30000
        }
    )

    assert create_response.status_code == 200

    employee_id = create_response.json()["employee"]["id"]

    # Delete employee
    delete_response = client.delete(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 200

    assert (
        delete_response.json()["message"]
        == "Employee deleted successfully"
    )

    # Verify employee no longer exists
    get_response = client.get(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code == 404


# --------------------------------------------------
# Test 11: Normal user cannot delete employee
# --------------------------------------------------

def test_user_cannot_delete_employee():

    admin_token = get_admin_token()

    email = f"protected_delete_{uuid.uuid4().hex[:8]}@example.com"

    # Admin creates employee
    create_response = client.post(
        "/employees",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "Protected Delete Employee",
            "email": email,
            "department": "Testing",
            "salary": 30000
        }
    )

    assert create_response.status_code == 200

    employee_id = create_response.json()["employee"]["id"]

    # Normal user
    user_token = get_user_token()

    # Try to delete
    response = client.delete(
        f"/employees/{employee_id}",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
