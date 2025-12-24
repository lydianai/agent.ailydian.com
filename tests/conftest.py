"""
Pytest Configuration and Fixtures

Provides shared fixtures for all tests.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, timedelta
from uuid import uuid4

# FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Models
from core.database.models import Base, User, Hospital, UserRole, SubscriptionTier, ComplianceRegion

# App
# from main import app  # Will uncomment when ready


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """
    Create in-memory SQLite database for testing.

    Using SQLite instead of PostgreSQL for speed.
    Scope: session (created once for all tests)
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create a new database session for each test.

    Automatically rolls back after each test.
    Scope: function (new session per test)
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ============================================================================
# HOSPITAL & USER FIXTURES
# ============================================================================

@pytest.fixture
def test_hospital(db_session: Session) -> Hospital:
    """Create a test hospital"""
    hospital = Hospital(
        hospital_id=uuid4(),
        name="Test General Hospital",
        tenant_id="test-hospital-001",
        country="US",
        state="California",
        city="San Francisco",
        subscription_tier=SubscriptionTier.ENTERPRISE,
        compliance_region=ComplianceRegion.USA,
        hipaa_compliant=True,
        quantum_enabled=True,
        is_active=True,
        is_verified=True,
    )
    db_session.add(hospital)
    db_session.commit()
    db_session.refresh(hospital)
    return hospital


@pytest.fixture
def test_user_physician(db_session: Session, test_hospital: Hospital) -> User:
    """Create a test physician user"""
    from core.security.auth import get_password_hash

    user = User(
        user_id=uuid4(),
        hospital_id=test_hospital.hospital_id,
        email="dr.test@hospital.com",
        username="dr.test",
        hashed_password=get_password_hash("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        full_name="Dr. John Doe",
        role=UserRole.PHYSICIAN,
        medical_license_number="CA123456",
        medical_license_state="California",
        medical_specialties=["cardiology", "internal_medicine"],
        email_verified=True,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_nurse(db_session: Session, test_hospital: Hospital) -> User:
    """Create a test nurse user"""
    from core.security.auth import get_password_hash

    user = User(
        user_id=uuid4(),
        hospital_id=test_hospital.hospital_id,
        email="nurse.test@hospital.com",
        username="nurse.test",
        hashed_password=get_password_hash("TestPassword123!"),
        first_name="Jane",
        last_name="Smith",
        full_name="Jane Smith, RN",
        role=UserRole.NURSE,
        email_verified=True,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_admin(db_session: Session, test_hospital: Hospital) -> User:
    """Create a test admin user"""
    from core.security.auth import get_password_hash

    user = User(
        user_id=uuid4(),
        hospital_id=test_hospital.hospital_id,
        email="admin@hospital.com",
        username="admin",
        hashed_password=get_password_hash("AdminPassword123!"),
        first_name="Admin",
        last_name="User",
        full_name="Admin User",
        role=UserRole.ADMIN,
        email_verified=True,
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    FastAPI test client (synchronous)
    """
    # from main import app
    # with TestClient(app) as c:
    #     yield c
    pass  # Uncomment when app is ready


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI async test client
    """
    # from main import app
    # async with AsyncClient(app=app, base_url="http://test") as ac:
    #     yield ac
    pass  # Uncomment when app is ready


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def auth_headers_physician(test_user_physician: User) -> dict:
    """
    Get auth headers for physician user
    """
    from core.security.auth import create_access_token

    access_token = create_access_token(
        data={"sub": test_user_physician.username}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_nurse(test_user_nurse: User) -> dict:
    """
    Get auth headers for nurse user
    """
    from core.security.auth import create_access_token

    access_token = create_access_token(
        data={"sub": test_user_nurse.username}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_admin(test_user_admin: User) -> dict:
    """
    Get auth headers for admin user
    """
    from core.security.auth import create_access_token

    access_token = create_access_token(
        data={"sub": test_user_admin.username}
    )
    return {"Authorization": f"Bearer {access_token}"}


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_vital_signs() -> dict:
    """Sample vital signs data"""
    return {
        "heart_rate": 72,
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "temperature": 37.0,
        "respiratory_rate": 16,
        "spo2": 98,
    }


@pytest.fixture
def mock_patient_data() -> dict:
    """Sample patient data"""
    return {
        "mrn": "TEST-123456",
        "first_name": "Test",
        "last_name": "Patient",
        "dob": "1980-01-01",
        "gender": "male",
        "blood_type": "O+",
    }


@pytest.fixture
def mock_clinical_notes() -> str:
    """Sample clinical notes"""
    return """
    Patient presents with chest pain and shortness of breath.
    Onset: 2 hours ago
    Pain: 7/10, radiating to left arm
    History: Hypertension, controlled with medication
    Allergies: Penicillin
    """


# ============================================================================
# AI AGENT FIXTURES
# ============================================================================

@pytest.fixture
def mock_openai_api_key() -> str:
    """Mock OpenAI API key for testing"""
    return "sk-test-mock-key-for-testing"


@pytest.fixture
def mock_ibm_quantum_token() -> str:
    """Mock IBM Quantum token for testing"""
    return "test-quantum-token"


# ============================================================================
# TIME FIXTURES
# ============================================================================

@pytest.fixture
def freeze_time():
    """Freeze time for testing"""
    frozen_time = datetime(2025, 12, 24, 12, 0, 0)
    return frozen_time


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Auto-cleanup after each test.

    Runs after every test automatically.
    """
    yield
    # Cleanup code here if needed
    pass


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom markers
    """
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require external services)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full system)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (> 1 second)"
    )
    config.addinivalue_line(
        "markers", "ai: Tests requiring AI API keys"
    )
    config.addinivalue_line(
        "markers", "quantum: Tests requiring IBM Quantum"
    )


# ============================================================================
# ASYNC SUPPORT
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.

    Scope: session (one loop for all tests)
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
