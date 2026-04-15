from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.tenant import get_tenant_context
from app.db.session import Base, get_db
from app.main import app
from app.models.entities import Organization, OrganizationMembership, Role, User
from app.schemas.auth import TenantContext

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seeded(db: Session) -> dict[str, int]:
    org1 = Organization(name="Org One")
    org2 = Organization(name="Org Two")
    db.add_all([org1, org2])
    db.flush()

    user1 = User(auth0_sub="auth0|u1", email="u1@example.com", full_name="User One")
    user2 = User(auth0_sub="auth0|u2", email="u2@example.com", full_name="User Two")
    db.add_all([user1, user2])
    db.flush()

    db.add_all(
        [
            OrganizationMembership(org_id=org1.id, user_id=user1.id, role=Role.ADMIN),
            OrganizationMembership(org_id=org2.id, user_id=user2.id, role=Role.ANALYST),
        ]
    )
    db.commit()

    return {
        "org1": org1.id,
        "org2": org2.id,
        "user1": user1.id,
        "user2": user2.id,
    }


def _override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client_org1_admin() -> Generator[TestClient, None, None]:
    def tenant_override() -> TenantContext:
        return TenantContext(org_id=1, role=Role.ADMIN, user_id=1)

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_tenant_context] = tenant_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client_org2_analyst() -> Generator[TestClient, None, None]:
    def tenant_override() -> TenantContext:
        return TenantContext(org_id=2, role=Role.ANALYST, user_id=2)

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_tenant_context] = tenant_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
