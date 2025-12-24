"""Add User, Hospital, UserSession, and AuditLog models

Revision ID: 001
Revises:
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    op.execute("""
        CREATE TYPE userrole AS ENUM (
            'admin', 'physician', 'nurse', 'radiologist',
            'pharmacist', 'researcher', 'viewer'
        );
    """)

    op.execute("""
        CREATE TYPE subscriptiontier AS ENUM (
            'community', 'professional', 'enterprise', 'quantum_plus'
        );
    """)

    op.execute("""
        CREATE TYPE complianceregion AS ENUM (
            'usa', 'eu', 'turkey', 'japan', 'middle_east'
        );
    """)

    # Create hospitals table
    op.create_table(
        'hospitals',
        sa.Column('hospital_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('tenant_id', sa.String(100), unique=True, nullable=False),

        # Location
        sa.Column('country', sa.String(2)),
        sa.Column('state', sa.String(100)),
        sa.Column('city', sa.String(100)),
        sa.Column('address', sa.Text()),
        sa.Column('timezone', sa.String(50), server_default='UTC'),

        # Contact
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(100)),
        sa.Column('website', sa.String(200)),

        # Integration
        sa.Column('fhir_endpoint', sa.String(500)),
        sa.Column('fhir_client_id', sa.String(200)),
        sa.Column('fhir_client_secret_encrypted', sa.LargeBinary()),
        sa.Column('ehr_system', sa.String(50)),

        # Subscription
        sa.Column('subscription_tier', sa.Enum('community', 'professional', 'enterprise', 'quantum_plus', name='subscriptiontier'), server_default='community'),
        sa.Column('subscription_start_date', sa.DateTime(timezone=True)),
        sa.Column('subscription_end_date', sa.DateTime(timezone=True)),
        sa.Column('monthly_fee', sa.Float(), server_default='0.0'),

        # Compliance
        sa.Column('compliance_region', sa.Enum('usa', 'eu', 'turkey', 'japan', 'middle_east', name='complianceregion'), nullable=False),
        sa.Column('hipaa_compliant', sa.Boolean(), server_default='false'),
        sa.Column('gdpr_compliant', sa.Boolean(), server_default='false'),
        sa.Column('kvkk_compliant', sa.Boolean(), server_default='false'),

        # Limits
        sa.Column('max_patients', sa.Integer()),
        sa.Column('max_users', sa.Integer()),
        sa.Column('max_ai_requests_per_day', sa.Integer()),
        sa.Column('quantum_enabled', sa.Boolean(), server_default='false'),

        # Settings
        sa.Column('settings', postgresql.JSONB(), server_default='{}'),

        # Status
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),

        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create indexes for hospitals
    op.create_index('idx_hospital_tenant', 'hospitals', ['tenant_id'])
    op.create_index('idx_hospital_active', 'hospitals', ['is_active'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('hospital_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hospitals.hospital_id'), nullable=False),

        # Authentication
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),

        # Personal Info
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(200)),

        # Role & Permissions
        sa.Column('role', sa.Enum('admin', 'physician', 'nurse', 'radiologist', 'pharmacist', 'researcher', 'viewer', name='userrole'), nullable=False),
        sa.Column('permissions', postgresql.JSONB(), server_default='{}'),

        # Medical License
        sa.Column('medical_license_number', sa.String(50)),
        sa.Column('medical_license_state', sa.String(50)),
        sa.Column('medical_specialties', postgresql.ARRAY(sa.String())),

        # Contact
        sa.Column('phone', sa.String(20)),
        sa.Column('phone_verified', sa.Boolean(), server_default='false'),

        # MFA
        sa.Column('mfa_enabled', sa.Boolean(), server_default='false'),
        sa.Column('mfa_secret', sa.String(32)),
        sa.Column('mfa_backup_codes', postgresql.ARRAY(sa.String())),

        # Security
        sa.Column('password_reset_token', sa.String(255)),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True)),
        sa.Column('email_verification_token', sa.String(255)),
        sa.Column('email_verified', sa.Boolean(), server_default='false'),

        # Session Management
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('last_login_ip', sa.String(45)),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True)),

        # Preferences
        sa.Column('preferred_language', sa.String(5), server_default='en'),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.Column('theme', sa.String(20), server_default='dark'),

        # Notifications
        sa.Column('email_notifications', sa.Boolean(), server_default='true'),
        sa.Column('sms_notifications', sa.Boolean(), server_default='false'),
        sa.Column('push_notifications', sa.Boolean(), server_default='true'),

        # Status
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_staff', sa.Boolean(), server_default='false'),
        sa.Column('is_superuser', sa.Boolean(), server_default='false'),

        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('last_password_change', sa.DateTime(timezone=True)),
    )

    # Create indexes for users
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_hospital', 'users', ['hospital_id'])
    op.create_index('idx_user_role', 'users', ['role'])
    op.create_index('idx_user_active', 'users', ['is_active'])

    # Add email validation constraint
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT valid_email
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$');
    """)

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=False),

        # JWT Token Info
        sa.Column('jti', sa.String(36), unique=True, nullable=False),
        sa.Column('access_token_hash', sa.String(64)),
        sa.Column('refresh_token_hash', sa.String(64)),

        # Session Metadata
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('device_type', sa.String(50)),
        sa.Column('device_name', sa.String(100)),

        # Timing
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        # Status
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('revoked_reason', sa.String(200)),
    )

    # Create indexes for user_sessions
    op.create_index('idx_session_user', 'user_sessions', ['user_id'])
    op.create_index('idx_session_jti', 'user_sessions', ['jti'])
    op.create_index('idx_session_expires', 'user_sessions', ['expires_at'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), primary_key=True),

        # Who
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('hospital_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hospitals.hospital_id')),

        # What
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', sa.String(100)),

        # Details
        sa.Column('description', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),

        # When & Where
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text()),

        # Outcome
        sa.Column('success', sa.Boolean(), server_default='true'),
        sa.Column('error_message', sa.Text()),

        # PHI Access
        sa.Column('accessed_phi', sa.Boolean(), server_default='false'),
        sa.Column('phi_fields', postgresql.ARRAY(sa.String())),
    )

    # Create indexes for audit_logs
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('user_sessions')
    op.drop_table('users')
    op.drop_table('hospitals')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole CASCADE;")
    op.execute("DROP TYPE IF EXISTS subscriptiontier CASCADE;")
    op.execute("DROP TYPE IF EXISTS complianceregion CASCADE;")
