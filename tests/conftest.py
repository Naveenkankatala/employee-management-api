import os

import pytest
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app import models
from app.auth import hash_password


TEST_USER_USERNAME = os.getenv("TEST_USER_USERNAME", "testuser_ci")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")

TEST_ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "admin_ci")
TEST_ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "AdminPassword123!")


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        test_user = db.query(models.User).filter(
            models.User.username == TEST_USER_USERNAME
        ).first()

        if not test_user:
            test_user = models.User(
                username=TEST_USER_USERNAME,
                password=hash_password(TEST_USER_PASSWORD),
                role="user"
            )
            db.add(test_user)

        test_admin = db.query(models.User).filter(
            models.User.username == TEST_ADMIN_USERNAME
        ).first()

        if not test_admin:
            test_admin = models.User(
                username=TEST_ADMIN_USERNAME,
                password=hash_password(TEST_ADMIN_PASSWORD),
                role="admin"
            )
            db.add(test_admin)

        db.commit()

        yield

    finally:
        db.close()