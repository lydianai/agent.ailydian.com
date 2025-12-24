"""
Application Configuration Management

HIPAA-compliant configuration with environment variable validation.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All PHI-related configurations are validated for HIPAA compliance.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========================================================================
    # APPLICATION
    # ========================================================================
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_name: str = Field(default="HealthCare-AI-Quantum-System")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ========================================================================
    # API
    # ========================================================================
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080)
    api_workers: int = Field(default=4)
    api_reload: bool = Field(default=False)

    # ========================================================================
    # DATABASE - PostgreSQL
    # ========================================================================
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="healthcare_ai")
    postgres_user: str = Field(default="healthcare_admin")
    postgres_password: str = Field(default="")
    postgres_schema: str = Field(default="public")
    postgres_pool_size: int = Field(default=20)
    postgres_max_overflow: int = Field(default=10)

    @property
    def postgres_url(self) -> str:
        """PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_url_sync(self) -> str:
        """Synchronous PostgreSQL URL for Alembic"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ========================================================================
    # DATABASE - MongoDB
    # ========================================================================
    mongodb_host: str = Field(default="localhost")
    mongodb_port: int = Field(default=27017)
    mongodb_db: str = Field(default="healthcare_ai_docs")
    mongodb_user: str = Field(default="healthcare_admin")
    mongodb_password: str = Field(default="")

    @property
    def mongodb_url(self) -> str:
        """MongoDB connection URL"""
        if self.mongodb_user and self.mongodb_password:
            return (
                f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
                f"@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
            )
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"

    # ========================================================================
    # CACHE - Redis
    # ========================================================================
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)
    redis_cache_ttl: int = Field(default=300, description="Cache TTL in seconds")

    # ========================================================================
    # MESSAGE QUEUE - Kafka
    # ========================================================================
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_patient_events: str = Field(default="patient-events")
    kafka_topic_agent_comm: str = Field(default="agent-communications")
    kafka_topic_alerts: str = Field(default="patient-alerts")
    kafka_consumer_group: str = Field(default="healthcare-ai-agents")

    @property
    def kafka_servers_list(self) -> List[str]:
        """Kafka servers as list"""
        return self.kafka_bootstrap_servers.split(",")

    # ========================================================================
    # AI/ML - OpenAI
    # ========================================================================
    openai_api_key: str = Field(default="")
    openai_model_gpt4: str = Field(default="gpt-4-turbo-preview")
    openai_model_gpt4o: str = Field(default="gpt-4o")
    openai_max_tokens: int = Field(default=4000)
    openai_temperature: float = Field(default=0.3)

    # ========================================================================
    # AI/ML - Anthropic (Claude)
    # ========================================================================
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-3-opus-20240229")
    anthropic_max_tokens: int = Field(default=4000)
    anthropic_temperature: float = Field(default=0.3)

    # ========================================================================
    # AI/ML - Google (Gemini)
    # ========================================================================
    google_api_key: str = Field(default="")
    google_model: str = Field(default="gemini-pro")

    # ========================================================================
    # QUANTUM COMPUTING - IBM Quantum
    # ========================================================================
    ibm_quantum_token: str = Field(default="")
    ibm_quantum_backend: str = Field(default="ibm_brisbane")
    ibm_quantum_hub: str = Field(default="ibm-q")
    ibm_quantum_group: str = Field(default="open")
    ibm_quantum_project: str = Field(default="main")

    # ========================================================================
    # CLOUD - AWS
    # ========================================================================
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_region: str = Field(default="us-east-1")
    aws_s3_bucket_medical_images: str = Field(default="healthcare-ai-medical-images")
    aws_s3_bucket_phi_encrypted: str = Field(default="healthcare-ai-phi-encrypted")

    # ========================================================================
    # SECURITY
    # ========================================================================
    secret_key: str = Field(default="change-this-secret-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    phi_encryption_key: str = Field(default="")
    encryption_key_version: int = Field(default=1)

    # ========================================================================
    # COMPLIANCE
    # ========================================================================
    hipaa_mode: bool = Field(default=True, description="HIPAA compliance enforcement")
    kvkk_mode: bool = Field(default=True, description="KVKK compliance enforcement")
    audit_logging_enabled: bool = Field(default=True)
    phi_encryption_required: bool = Field(default=True)
    min_password_length: int = Field(default=12)
    mfa_required: bool = Field(default=True)
    data_retention_days: int = Field(default=2555, description="7 years for HIPAA")

    # ========================================================================
    # MONITORING
    # ========================================================================
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="development")
    sentry_traces_sample_rate: float = Field(default=0.1)

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    enable_quantum_optimization: bool = Field(default=False)
    enable_clinical_decision_agent: bool = Field(default=True)
    enable_resource_optimization_agent: bool = Field(default=True)
    enable_patient_monitoring_agent: bool = Field(default=True)
    enable_emergency_response_agent: bool = Field(default=False)
    enable_diagnosis_agent: bool = Field(default=False)
    enable_treatment_planning_agent: bool = Field(default=False)
    enable_pharmacy_management_agent: bool = Field(default=False)

    # ========================================================================
    # AGENT CONFIGURATION
    # ========================================================================
    agent_decision_timeout_seconds: int = Field(default=30)
    agent_confidence_threshold: float = Field(default=0.8)
    agent_human_review_threshold: float = Field(default=0.7)
    agent_max_retries: int = Field(default=3)

    # ========================================================================
    # HEALTHCARE INTEGRATION
    # ========================================================================
    hl7_fhir_base_url: str = Field(default="http://localhost:8081/fhir")
    hl7_version: str = Field(default="2.5")
    dicom_ae_title: str = Field(default="HEALTHCARE_AI")
    dicom_port: int = Field(default=11112)

    # ========================================================================
    # TESTING
    # ========================================================================
    test_mode: bool = Field(default=False)
    mock_llm_responses: bool = Field(default=False)
    synthetic_patient_data: bool = Field(default=True)

    # ========================================================================
    # VALIDATORS
    # ========================================================================

    @validator("app_env")
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v

    @validator("agent_confidence_threshold", "agent_human_review_threshold")
    def validate_threshold(cls, v: float) -> float:
        """Validate thresholds are between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        """Ensure secret key is changed in production"""
        if values.get("app_env") == "production" and v == "change-this-secret-key":
            raise ValueError("SECRET_KEY must be changed in production!")
        return v

    @validator("phi_encryption_key")
    def validate_phi_encryption(cls, v: str, values: dict) -> str:
        """Ensure PHI encryption is configured if required"""
        if values.get("phi_encryption_required") and not v:
            raise ValueError("PHI_ENCRYPTION_KEY is required when phi_encryption_required=true")
        return v

    # ========================================================================
    # HELPERS
    # ========================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.app_env == "development"

    @property
    def has_openai(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.openai_api_key)

    @property
    def has_anthropic(self) -> bool:
        """Check if Anthropic is configured"""
        return bool(self.anthropic_api_key)

    @property
    def has_quantum(self) -> bool:
        """Check if IBM Quantum is configured"""
        return bool(self.ibm_quantum_token) and self.enable_quantum_optimization


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()


# Convenience export
settings = get_settings()
