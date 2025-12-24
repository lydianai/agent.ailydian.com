"""
Unit Tests for User and Hospital Database Models

Tests user creation, authentication, RBAC, and multi-tenant isolation.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from core.database.models import User, Hospital, UserRole, SubscriptionTier, ComplianceRegion, UserSession
from core.security.auth import get_password_hash, verify_password


# ============================================================================
# HOSPITAL MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestHospitalModel:
    """Test Hospital model functionality"""

    def test_create_hospital(self, db_session):
        """Test creating a new hospital"""
        hospital = Hospital(
            hospital_id=uuid4(),
            name="Test Hospital",
            tenant_id="test-hospital-001",
            country="US",
            compliance_region=ComplianceRegion.USA,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
        )

        db_session.add(hospital)
        db_session.commit()

        assert hospital.hospital_id is not None
        assert hospital.name == "Test Hospital"
        assert hospital.is_active is True
        assert hospital.created_at is not None

    def test_hospital_tenant_id_unique(self, db_session, test_hospital):
        """Test that tenant_id must be unique"""
        duplicate_hospital = Hospital(
            hospital_id=uuid4(),
            name="Duplicate Hospital",
            tenant_id=test_hospital.tenant_id,  # Same tenant_id
            compliance_region=ComplianceRegion.USA,
        )

        db_session.add(duplicate_hospital)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_hospital_subscription_tiers(self, db_session):
        """Test different subscription tiers"""
        tiers = [
            SubscriptionTier.COMMUNITY,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.ENTERPRISE,
            SubscriptionTier.QUANTUM_PLUS,
        ]

        for tier in tiers:
            hospital = Hospital(
                hospital_id=uuid4(),
                name=f"Hospital {tier.value}",
                tenant_id=f"hospital-{tier.value}",
                compliance_region=ComplianceRegion.USA,
                subscription_tier=tier,
            )
            db_session.add(hospital)

        db_session.commit()

        # Verify all created
        assert db_session.query(Hospital).count() == len(tiers)

    def test_hospital_quantum_enabled(self, db_session):
        """Test quantum computing flag"""
        hospital_quantum = Hospital(
            hospital_id=uuid4(),
            name="Quantum Hospital",
            tenant_id="quantum-hospital",
            compliance_region=ComplianceRegion.USA,
            subscription_tier=SubscriptionTier.QUANTUM_PLUS,
            quantum_enabled=True,
        )

        db_session.add(hospital_quantum)
        db_session.commit()

        assert hospital_quantum.quantum_enabled is True


# ============================================================================
# USER MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestUserModel:
    """Test User model functionality"""

    def test_create_user(self, db_session, test_hospital):
        """Test creating a new user"""
        user = User(
            user_id=uuid4(),
            hospital_id=test_hospital.hospital_id,
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("TestPassword123!"),
            first_name="Test",
            last_name="User",
            role=UserRole.PHYSICIAN,
        )

        db_session.add(user)
        db_session.commit()

        assert user.user_id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_email_unique(self, db_session, test_user_physician):
        """Test that email must be unique"""
        duplicate_user = User(
            user_id=uuid4(),
            hospital_id=test_user_physician.hospital_id,
            email=test_user_physician.email,  # Same email
            username="different_username",
            hashed_password=get_password_hash("Password123!"),
            first_name="Another",
            last_name="User",
            role=UserRole.NURSE,
        )

        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_username_unique(self, db_session, test_user_physician):
        """Test that username must be unique"""
        duplicate_user = User(
            user_id=uuid4(),
            hospital_id=test_user_physician.hospital_id,
            email="different@example.com",
            username=test_user_physician.username,  # Same username
            hashed_password=get_password_hash("Password123!"),
            first_name="Another",
            last_name="User",
            role=UserRole.NURSE,
        )

        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_roles(self, db_session, test_hospital):
        """Test different user roles"""
        roles = [
            UserRole.ADMIN,
            UserRole.PHYSICIAN,
            UserRole.NURSE,
            UserRole.RADIOLOGIST,
            UserRole.PHARMACIST,
            UserRole.RESEARCHER,
            UserRole.VIEWER,
        ]

        for i, role in enumerate(roles):
            user = User(
                user_id=uuid4(),
                hospital_id=test_hospital.hospital_id,
                email=f"user{i}@hospital.com",
                username=f"user_{role.value}",
                hashed_password=get_password_hash("Password123!"),
                first_name="Test",
                last_name=f"User {i}",
                role=role,
            )
            db_session.add(user)

        db_session.commit()

        # Verify all roles created
        for role in roles:
            user = db_session.query(User).filter_by(role=role).first()
            assert user is not None
            assert user.role == role

    def test_user_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_user_mfa_fields(self, db_session, test_hospital):
        """Test MFA-related fields"""
        user = User(
            user_id=uuid4(),
            hospital_id=test_hospital.hospital_id,
            email="mfa@example.com",
            username="mfa_user",
            hashed_password=get_password_hash("Password123!"),
            first_name="MFA",
            last_name="User",
            role=UserRole.PHYSICIAN,
            mfa_enabled=True,
            mfa_secret="TESTSECRET123456",
            mfa_backup_codes=["CODE1", "CODE2", "CODE3"],
        )

        db_session.add(user)
        db_session.commit()

        assert user.mfa_enabled is True
        assert user.mfa_secret is not None
        assert len(user.mfa_backup_codes) == 3

    def test_user_medical_license(self, db_session, test_hospital):
        """Test medical license fields for clinical staff"""
        physician = User(
            user_id=uuid4(),
            hospital_id=test_hospital.hospital_id,
            email="doctor@hospital.com",
            username="dr_smith",
            hashed_password=get_password_hash("Password123!"),
            first_name="John",
            last_name="Smith",
            role=UserRole.PHYSICIAN,
            medical_license_number="CA123456",
            medical_license_state="California",
            medical_specialties=["cardiology", "internal_medicine"],
        )

        db_session.add(physician)
        db_session.commit()

        assert physician.medical_license_number == "CA123456"
        assert "cardiology" in physician.medical_specialties

    def test_user_account_lockout(self, db_session, test_hospital):
        """Test account lockout mechanism"""
        user = User(
            user_id=uuid4(),
            hospital_id=test_hospital.hospital_id,
            email="locked@example.com",
            username="locked_user",
            hashed_password=get_password_hash("Password123!"),
            first_name="Locked",
            last_name="User",
            role=UserRole.VIEWER,
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(hours=1),
        )

        db_session.add(user)
        db_session.commit()

        assert user.failed_login_attempts == 5
        assert user.locked_until > datetime.utcnow()


# ============================================================================
# MULTI-TENANT ISOLATION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestMultiTenantIsolation:
    """Test multi-tenant data isolation"""

    def test_users_belong_to_hospitals(self, db_session):
        """Test that users are associated with hospitals"""
        # Create two hospitals
        hospital1 = Hospital(
            hospital_id=uuid4(),
            name="Hospital 1",
            tenant_id="hospital-001",
            compliance_region=ComplianceRegion.USA,
        )
        hospital2 = Hospital(
            hospital_id=uuid4(),
            name="Hospital 2",
            tenant_id="hospital-002",
            compliance_region=ComplianceRegion.USA,
        )

        db_session.add_all([hospital1, hospital2])
        db_session.commit()

        # Create users for each hospital
        user1 = User(
            user_id=uuid4(),
            hospital_id=hospital1.hospital_id,
            email="user1@hospital1.com",
            username="user1",
            hashed_password=get_password_hash("Password123!"),
            first_name="User",
            last_name="One",
            role=UserRole.PHYSICIAN,
        )

        user2 = User(
            user_id=uuid4(),
            hospital_id=hospital2.hospital_id,
            email="user2@hospital2.com",
            username="user2",
            hashed_password=get_password_hash("Password123!"),
            first_name="User",
            last_name="Two",
            role=UserRole.NURSE,
        )

        db_session.add_all([user1, user2])
        db_session.commit()

        # Verify isolation
        hospital1_users = db_session.query(User).filter_by(hospital_id=hospital1.hospital_id).all()
        hospital2_users = db_session.query(User).filter_by(hospital_id=hospital2.hospital_id).all()

        assert len(hospital1_users) == 1
        assert len(hospital2_users) == 1
        assert hospital1_users[0].hospital_id != hospital2_users[0].hospital_id

    def test_user_cannot_exist_without_hospital(self, db_session):
        """Test that user must belong to a hospital (foreign key constraint)"""
        user = User(
            user_id=uuid4(),
            hospital_id=uuid4(),  # Non-existent hospital
            email="orphan@example.com",
            username="orphan_user",
            hashed_password=get_password_hash("Password123!"),
            first_name="Orphan",
            last_name="User",
            role=UserRole.VIEWER,
        )

        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()


# ============================================================================
# USER SESSION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestUserSession:
    """Test UserSession model for JWT token tracking"""

    def test_create_session(self, db_session, test_user_physician):
        """Test creating a user session"""
        session = UserSession(
            session_id=uuid4(),
            user_id=test_user_physician.user_id,
            jti=str(uuid4()),
            access_token_hash="abc123hash",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            device_type="desktop",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        db_session.add(session)
        db_session.commit()

        assert session.session_id is not None
        assert session.is_active is True
        assert session.created_at is not None

    def test_session_revocation(self, db_session, test_user_physician):
        """Test revoking a session"""
        session = UserSession(
            session_id=uuid4(),
            user_id=test_user_physician.user_id,
            jti=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=False,
            revoked_at=datetime.utcnow(),
            revoked_reason="User logged out",
        )

        db_session.add(session)
        db_session.commit()

        assert session.is_active is False
        assert session.revoked_at is not None


# ============================================================================
# COMPLIANCE & SECURITY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.compliance
class TestComplianceFeatures:
    """Test HIPAA and compliance-related features"""

    def test_hospital_compliance_regions(self, db_session):
        """Test compliance region enforcement"""
        regions = [
            ComplianceRegion.USA,
            ComplianceRegion.EU,
            ComplianceRegion.TURKEY,
            ComplianceRegion.JAPAN,
            ComplianceRegion.MIDDLE_EAST,
        ]

        for i, region in enumerate(regions):
            hospital = Hospital(
                hospital_id=uuid4(),
                name=f"Hospital {region.value}",
                tenant_id=f"hospital-{region.value}",
                compliance_region=region,
            )
            db_session.add(hospital)

        db_session.commit()

        # Verify all compliance regions
        for region in regions:
            h = db_session.query(Hospital).filter_by(compliance_region=region).first()
            assert h is not None

    def test_hipaa_flags(self, db_session):
        """Test HIPAA compliance flags"""
        hospital = Hospital(
            hospital_id=uuid4(),
            name="HIPAA Compliant Hospital",
            tenant_id="hipaa-hospital",
            compliance_region=ComplianceRegion.USA,
            hipaa_compliant=True,
        )

        db_session.add(hospital)
        db_session.commit()

        assert hospital.hipaa_compliant is True

    def test_email_validation_constraint(self, db_session, test_hospital):
        """Test email format validation"""
        invalid_emails = ["notanemail", "missing@domain", "@example.com", "user@"]

        for invalid_email in invalid_emails:
            user = User(
                user_id=uuid4(),
                hospital_id=test_hospital.hospital_id,
                email=invalid_email,
                username=f"user_{invalid_email}",
                hashed_password=get_password_hash("Password123!"),
                first_name="Test",
                last_name="User",
                role=UserRole.VIEWER,
            )

            db_session.add(user)

            # Should fail email validation
            with pytest.raises((IntegrityError, ValueError)):
                db_session.commit()
                db_session.rollback()
