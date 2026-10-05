from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    salary: float


class UserCreate(BaseModel):
    username: str
    password: str