from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin
)
from app.schemas import EmployeeCreate, UserCreate
from app.logging_config import logger


# =========================
# FASTAPI APP
# =========================

app = FastAPI(title="Employee Management API")


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "Employee Management API is running"
    }


# =========================================================
# EMPLOYEE APIs
# =========================================================


# =========================
# CREATE EMPLOYEE
# ADMIN ONLY
# =========================

@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    # Check if email already exists
    existing_employee = db.query(models.Employee).filter(
        models.Employee.email == employee.email
    ).first()

    if existing_employee:

        logger.warning(
            f"Employee creation failed: "
            f"Email already exists - {employee.email}"
        )

        raise HTTPException(
            status_code=409,
            detail="An employee with this email already exists"
        )

    # Create employee
    new_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        salary=employee.salary
    )

    db.add(new_employee)

    try:
        db.commit()

    except IntegrityError:

        db.rollback()

        logger.warning(
            f"Employee creation failed: "
            f"Email already exists - {employee.email}"
        )

        raise HTTPException(
            status_code=409,
            detail="An employee with this email already exists"
        )

    db.refresh(new_employee)

    # Log employee creation
    logger.info(
        f"Employee created: ID={new_employee.id}, "
        f"Name={new_employee.name}, "
        f"Department={new_employee.department}, "
        f"By={current_user.username}"
    )

    return {
        "message": "Employee created successfully",
        "employee": new_employee
    }


# =========================
# GET ALL EMPLOYEES
# ADMIN + USER
# =========================

@app.get("/employees")
def get_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    employees = db.query(models.Employee).all()

    return {
        "employees": employees
    }


# =========================
# GET SINGLE EMPLOYEE
# ADMIN + USER
# =========================

@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:

        logger.warning(
            f"Employee not found: ID={employee_id}"
        )

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


# =========================
# UPDATE EMPLOYEE
# ADMIN ONLY
# =========================

@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    existing_employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not existing_employee:

        logger.warning(
            f"Employee update failed: "
            f"Employee ID={employee_id} not found"
        )

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Update employee
    existing_employee.name = employee.name
    existing_employee.email = employee.email
    existing_employee.department = employee.department
    existing_employee.salary = employee.salary

    try:
        db.commit()

    except IntegrityError:

        db.rollback()

        logger.warning(
            f"Employee update failed: "
            f"Email already exists - {employee.email}"
        )

        raise HTTPException(
            status_code=409,
            detail="An employee with this email already exists"
        )

    db.refresh(existing_employee)

    # Log employee update
    logger.info(
        f"Employee updated: ID={existing_employee.id}, "
        f"Name={existing_employee.name}, "
        f"Department={existing_employee.department}, "
        f"By={current_user.username}"
    )

    return {
        "message": "Employee updated successfully",
        "employee": existing_employee
    }


# =========================
# DELETE EMPLOYEE
# ADMIN ONLY
# =========================

@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:

        logger.warning(
            f"Employee deletion failed: "
            f"Employee ID={employee_id} not found"
        )

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Store information before deleting
    employee_id_value = employee.id
    employee_name = employee.name
    employee_department = employee.department

    # Delete employee
    db.delete(employee)
    db.commit()

    # Log employee deletion
    logger.info(
        f"Employee deleted: ID={employee_id_value}, "
        f"Name={employee_name}, "
        f"Department={employee_department}, "
        f"By={current_user.username}"
    )

    return {
        "message": "Employee deleted successfully"
    }


# =========================================================
# USER APIs
# =========================================================


# =========================
# REGISTER USER
# =========================

@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if username already exists
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:

        logger.warning(
            f"Registration failed: "
            f"Username already exists - {user.username}"
        )

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # New users are always normal users
    new_user = models.User(
        username=user.username,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    logger.info(
        f"User registered: ID={new_user.id}, "
        f"Username={new_user.username}"
    )

    return {
        "message": "User registered successfully",
        "username": new_user.username
    }


# =========================
# LOGIN
# =========================

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Find user
    existing_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    # Username doesn't exist
    if not existing_user:

        logger.warning(
            f"Failed login attempt: "
            f"Username={form_data.username}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    password_correct = verify_password(
        form_data.password,
        existing_user.password
    )

    # Wrong password
    if not password_correct:

        logger.warning(
            f"Failed login attempt: "
            f"Username={form_data.username}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create JWT token
    access_token = create_access_token(
        existing_user.username
    )

    # Log successful login
    logger.info(
        f"User logged in: "
        f"Username={existing_user.username}, "
        f"Role={existing_user.role}"
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "role": existing_user.role,
    "user_id": existing_user.id
}


# =========================
# GET ALL USERS
# ADMIN ONLY
# =========================

@app.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    users = db.query(models.User).all()

    logger.info(
        f"Users fetched by admin: "
        f"Admin={current_user.username}, "
        f"Count={len(users)}"
    )

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
            for user in users
        ]
    }


# =========================
# UPDATE USER ROLE
# ADMIN ONLY
# =========================

@app.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    # Find user
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Validate role
    if role not in ["admin", "user"]:

        raise HTTPException(
            status_code=400,
            detail="Role must be either 'admin' or 'user'"
        )

    # Prevent admin from changing their own role
    if user.id == current_user.id:

        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role"
        )

    old_role = user.role

    # Update role
    user.role = role

    db.commit()
    db.refresh(user)

    # Log role change
    logger.info(
        f"User role updated: "
        f"Username={user.username}, "
        f"OldRole={old_role}, "
        f"NewRole={user.role}, "
        f"By={current_user.username}"
    )

    return {
        "message": "User role updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }
# =========================
# DELETE USER
# ADMIN ONLY
# =========================

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    # Find the user
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    # User doesn't exist
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account"
        )

    username = user.username
    user_role = user.role

    # Delete user
    db.delete(user)
    db.commit()

    # Log deletion
    logger.info(
        f"User deleted: "
        f"Username={username}, "
        f"Role={user_role}, "
        f"By={current_user.username}"
    )

    return {
        "message": "User deleted successfully",
        "username": username
    }


# =========================================================
# LOGOUT
# =========================================================

@app.post("/logout")
def logout_user(
    current_user=Depends(get_current_user)
):

    logger.info(
        f"User logged out: "
        f"Username={current_user.username}"
    )

    return {
        "message": "Logout successful"
    }