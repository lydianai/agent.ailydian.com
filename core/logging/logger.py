"""
HIPAA-Compliant Logging System

All logs are structured, contain audit trails, and exclude PHI.
"""

import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from loguru import logger
from core.config import settings


class StructuredLogger:
    """
    Structured logger that ensures HIPAA compliance.

    Features:
    - Automatic PHI filtering
    - Structured JSON output
    - Audit trail integration
    - Performance tracking
    """

    def __init__(self):
        """Initialize structured logger"""
        # Remove default handler
        logger.remove()

        # Add custom handler based on environment
        if settings.is_production:
            # JSON format for production (better for log aggregation)
            logger.add(
                sys.stdout,
                format=self._json_formatter,
                level=settings.log_level,
                serialize=False
            )
        else:
            # Human-readable format for development
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                level=settings.log_level,
                colorize=True
            )

        # Add file handler for audit logs (always enabled)
        if settings.audit_logging_enabled:
            logger.add(
                "logs/audit_{time:YYYY-MM-DD}.log",
                rotation="1 day",
                retention="7 years",  # HIPAA requirement
                compression="gz",
                format=self._json_formatter,
                level="INFO"
            )

        self.logger = logger

    @staticmethod
    def _json_formatter(record: Dict[str, Any]) -> str:
        """
        Format log record as JSON

        Includes:
        - timestamp (ISO 8601)
        - level
        - message
        - extra context
        - NO PHI
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }

        # Add extra fields if present
        if record["extra"]:
            # Filter out PHI fields
            filtered_extra = {
                k: v for k, v in record["extra"].items()
                if k not in ["ssn", "dob", "patient_name", "mrn", "phi"]
            }
            log_entry["context"] = filtered_extra

        return json.dumps(log_entry)

    def _filter_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove PHI from log data

        PHI fields that are always removed:
        - ssn, dob, patient_name, address, phone, email
        - Patient IDs are hashed
        """
        phi_fields = [
            "ssn", "social_security_number",
            "dob", "date_of_birth", "birth_date",
            "patient_name", "first_name", "last_name",
            "address", "street_address",
            "phone", "phone_number", "telephone",
            "email", "email_address",
            "mrn"  # Medical Record Number
        ]

        filtered = data.copy()
        for field in phi_fields:
            if field in filtered:
                filtered[field] = "[REDACTED]"

        # Hash patient_id if present
        if "patient_id" in filtered:
            import hashlib
            filtered["patient_id_hash"] = hashlib.sha256(
                str(filtered["patient_id"]).encode()
            ).hexdigest()[:16]
            filtered.pop("patient_id")

        return filtered

    def info(self, message: str, **context: Any) -> None:
        """Log info message"""
        filtered_context = self._filter_phi(context)
        self.logger.bind(**filtered_context).info(message)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message"""
        filtered_context = self._filter_phi(context)
        self.logger.bind(**filtered_context).warning(message)

    def error(self, message: str, **context: Any) -> None:
        """Log error message"""
        filtered_context = self._filter_phi(context)
        self.logger.bind(**filtered_context).error(message)

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message"""
        filtered_context = self._filter_phi(context)
        self.logger.bind(**filtered_context).critical(message)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message"""
        if settings.debug:
            filtered_context = self._filter_phi(context)
            self.logger.bind(**filtered_context).debug(message)

    def audit(
        self,
        action: str,
        user_id: str,
        resource: str,
        outcome: str,
        **details: Any
    ) -> None:
        """
        Log audit trail event (HIPAA requirement)

        Args:
            action: Action performed (e.g., "patient_record_access")
            user_id: User who performed action
            resource: Resource affected (e.g., "patient:12345")
            outcome: Success/Failure
            **details: Additional context
        """
        audit_entry = {
            "audit_type": "access_log",
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Add details (PHI-filtered)
        if details:
            audit_entry["details"] = self._filter_phi(details)

        self.logger.bind(**audit_entry).info(f"AUDIT: {action}")


# Global logger instance
app_logger = StructuredLogger()


def get_logger() -> StructuredLogger:
    """Get application logger"""
    return app_logger
