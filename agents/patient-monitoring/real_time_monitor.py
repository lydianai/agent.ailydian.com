"""
Real-Time Patient Vital Signs Monitor

Kafka-based streaming for continuous patient monitoring.
Detects anomalies, predicts deterioration, and generates alerts.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sklearn.ensemble import IsolationForest

from core.config import settings
from core.logging import get_logger
from core.database import Alert, AlertSeverity

logger = get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class VitalSignsReading:
    """Single vital signs reading"""
    patient_id: str
    timestamp: datetime
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    temperature: Optional[float] = None
    device_id: Optional[str] = None


@dataclass
class PatientAlert:
    """Patient monitoring alert"""
    alert_id: str
    patient_id: str
    severity: str  # INFO, WARNING, URGENT, CRITICAL
    alert_type: str
    message: str
    details: Dict[str, Any]
    recommended_action: str
    timestamp: datetime


# ============================================================================
# REAL-TIME MONITOR
# ============================================================================

class RealTimeVitalSignsMonitor:
    """
    Real-time vital signs monitoring using Kafka streams

    Architecture:
    1. Consumes vital signs from Kafka topic
    2. Analyzes in 5-minute windows
    3. Detects anomalies and trends
    4. Generates alerts
    5. Publishes alerts to Kafka
    """

    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None

        # Patient baselines (in production: from database)
        self.baselines: Dict[str, Dict[str, float]] = {}

        # Recent readings (5-minute window)
        self.recent_readings: Dict[str, List[VitalSignsReading]] = {}

        # Anomaly detectors per patient
        self.anomaly_detectors: Dict[str, IsolationForest] = {}

        # Alert thresholds
        self.thresholds = {
            "heart_rate": {"low": 50, "high": 120, "critical_high": 150, "critical_low": 40},
            "blood_pressure_systolic": {"low": 90, "high": 160, "critical_high": 180, "critical_low": 70},
            "oxygen_saturation": {"low": 90, "critical_low": 85},
            "temperature": {"low": 36.0, "high": 38.0, "critical_high": 39.5, "critical_low": 35.0},
            "respiratory_rate": {"low": 12, "high": 20, "critical_high": 30, "critical_low": 8}
        }

        logger.info("Real-time vital signs monitor initialized")

    # ========================================================================
    # KAFKA CONNECTION
    # ========================================================================

    async def start(self):
        """Start Kafka consumer and producer"""

        # Consumer for vital signs
        self.consumer = AIOKafkaConsumer(
            settings.kafka_topic_patient_events,
            bootstrap_servers=settings.kafka_servers_list,
            group_id=f"{settings.kafka_consumer_group}-monitor",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest'
        )

        # Producer for alerts
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_servers_list,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        await self.consumer.start()
        await self.producer.start()

        logger.info(
            "Kafka connections established",
            consumer_topic=settings.kafka_topic_patient_events,
            producer_topic=settings.kafka_topic_alerts
        )

    async def stop(self):
        """Stop Kafka connections"""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

        logger.info("Kafka connections closed")

    # ========================================================================
    # MAIN MONITORING LOOP
    # ========================================================================

    async def monitor_stream(self):
        """
        Main monitoring loop

        Continuously processes vital signs from Kafka and generates alerts.
        """

        logger.info("Starting real-time monitoring stream...")

        try:
            async for message in self.consumer:
                try:
                    # Parse vital signs
                    data = message.value

                    if data.get("event_type") != "vital_signs":
                        continue

                    reading = VitalSignsReading(
                        patient_id=data["patient_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        heart_rate=data.get("heart_rate"),
                        blood_pressure_systolic=data.get("blood_pressure_systolic"),
                        blood_pressure_diastolic=data.get("blood_pressure_diastolic"),
                        respiratory_rate=data.get("respiratory_rate"),
                        oxygen_saturation=data.get("oxygen_saturation"),
                        temperature=data.get("temperature"),
                        device_id=data.get("device_id")
                    )

                    # Process reading
                    await self._process_reading(reading)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            logger.error(f"Monitoring stream error: {e}")
            raise

    async def _process_reading(self, reading: VitalSignsReading):
        """
        Process single vital signs reading

        Steps:
        1. Add to recent readings
        2. Rule-based alerts (immediate)
        3. Trend analysis
        4. Anomaly detection
        5. Sepsis risk assessment
        """

        patient_id = reading.patient_id

        # Initialize patient tracking
        if patient_id not in self.recent_readings:
            self.recent_readings[patient_id] = []
            self._initialize_anomaly_detector(patient_id)

        # Add reading
        self.recent_readings[patient_id].append(reading)

        # Keep only last 5 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        self.recent_readings[patient_id] = [
            r for r in self.recent_readings[patient_id]
            if r.timestamp > cutoff
        ]

        # 1. Rule-based alerts
        await self._check_threshold_alerts(reading)

        # 2. Trend analysis
        if len(self.recent_readings[patient_id]) >= 3:
            await self._check_trend_alerts(patient_id)

        # 3. Anomaly detection
        if len(self.recent_readings[patient_id]) >= 5:
            await self._check_anomaly_alerts(patient_id)

        # 4. Sepsis risk
        await self._assess_sepsis_risk(reading)

    # ========================================================================
    # ALERT GENERATION
    # ========================================================================

    async def _check_threshold_alerts(self, reading: VitalSignsReading):
        """Check for threshold-based alerts (immediate)"""

        alerts = []

        # Heart rate
        if reading.heart_rate:
            if reading.heart_rate > self.thresholds["heart_rate"]["critical_high"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "critical_tachycardia",
                    f"Critical tachycardia: HR={reading.heart_rate} bpm",
                    {"heart_rate": reading.heart_rate, "threshold": self.thresholds["heart_rate"]["critical_high"]},
                    "Immediate physician review and ECG"
                ))
            elif reading.heart_rate > self.thresholds["heart_rate"]["high"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.WARNING,
                    "tachycardia",
                    f"Tachycardia: HR={reading.heart_rate} bpm",
                    {"heart_rate": reading.heart_rate},
                    "Monitor closely, assess patient"
                ))
            elif reading.heart_rate < self.thresholds["heart_rate"]["critical_low"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "critical_bradycardia",
                    f"Critical bradycardia: HR={reading.heart_rate} bpm",
                    {"heart_rate": reading.heart_rate},
                    "Immediate intervention, prepare atropine"
                ))

        # Oxygen saturation
        if reading.oxygen_saturation:
            if reading.oxygen_saturation < self.thresholds["oxygen_saturation"]["critical_low"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "critical_hypoxia",
                    f"Critical hypoxia: SpO2={reading.oxygen_saturation}%",
                    {"oxygen_saturation": reading.oxygen_saturation},
                    "Immediate oxygen therapy, assess airway"
                ))
            elif reading.oxygen_saturation < self.thresholds["oxygen_saturation"]["low"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.URGENT,
                    "hypoxia",
                    f"Hypoxia: SpO2={reading.oxygen_saturation}%",
                    {"oxygen_saturation": reading.oxygen_saturation},
                    "Supplemental oxygen, assess respiratory status"
                ))

        # Temperature
        if reading.temperature:
            if reading.temperature >= self.thresholds["temperature"]["critical_high"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "high_fever",
                    f"High fever: Temp={reading.temperature}°C",
                    {"temperature": reading.temperature},
                    "Sepsis workup, antipyretics, blood cultures"
                ))

        # Blood pressure
        if reading.blood_pressure_systolic:
            if reading.blood_pressure_systolic > self.thresholds["blood_pressure_systolic"]["critical_high"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "hypertensive_crisis",
                    f"Hypertensive crisis: BP={reading.blood_pressure_systolic}/{reading.blood_pressure_diastolic}",
                    {"bp_systolic": reading.blood_pressure_systolic},
                    "Immediate antihypertensive therapy"
                ))
            elif reading.blood_pressure_systolic < self.thresholds["blood_pressure_systolic"]["critical_low"]:
                alerts.append(self._create_alert(
                    reading.patient_id,
                    AlertSeverity.CRITICAL,
                    "hypotension",
                    f"Severe hypotension: BP={reading.blood_pressure_systolic}/{reading.blood_pressure_diastolic}",
                    {"bp_systolic": reading.blood_pressure_systolic},
                    "IV fluids, assess for shock, consider pressors"
                ))

        # Publish alerts
        for alert in alerts:
            await self._publish_alert(alert)

    async def _check_trend_alerts(self, patient_id: str):
        """Analyze trends over recent readings"""

        readings = self.recent_readings[patient_id]
        if len(readings) < 3:
            return

        # Get HR trend
        hr_values = [r.heart_rate for r in readings if r.heart_rate]
        if len(hr_values) >= 3:
            # Calculate slope (simple linear regression)
            x = np.arange(len(hr_values))
            y = np.array(hr_values)
            slope = np.polyfit(x, y, 1)[0]  # bpm per reading

            # Alert if rapidly increasing
            if slope > 10:  # >10 bpm per minute
                alert = self._create_alert(
                    patient_id,
                    AlertSeverity.WARNING,
                    "rapid_hr_increase",
                    f"Rapid heart rate increase: {slope:.1f} bpm/min",
                    {"slope": slope, "current_hr": hr_values[-1]},
                    "Monitor closely, assess for deterioration"
                )
                await self._publish_alert(alert)

        # Similar for other vitals...

    async def _check_anomaly_alerts(self, patient_id: str):
        """Multi-variate anomaly detection"""

        readings = self.recent_readings[patient_id]
        if len(readings) < 5:
            return

        # Extract features
        features = []
        for r in readings:
            features.append([
                r.heart_rate or 80,
                r.blood_pressure_systolic or 120,
                r.oxygen_saturation or 98,
                r.temperature or 37.0
            ])

        features = np.array(features)

        # Detect anomalies
        detector = self.anomaly_detectors.get(patient_id)
        if detector:
            predictions = detector.predict(features)

            # If latest reading is anomalous
            if predictions[-1] == -1:
                alert = self._create_alert(
                    patient_id,
                    AlertSeverity.INFO,
                    "vital_signs_anomaly",
                    "Unusual vital signs pattern detected",
                    {"latest_vitals": features[-1].tolist()},
                    "Clinical assessment recommended"
                )
                await self._publish_alert(alert)

    async def _assess_sepsis_risk(self, reading: VitalSignsReading):
        """
        Assess sepsis risk using SIRS criteria + ML

        SIRS: 2+ of:
        - Temp >38°C or <36°C
        - HR >90
        - RR >20
        - WBC >12k or <4k (not available from vitals)
        """

        sirs_score = 0

        if reading.temperature:
            if reading.temperature > 38.0 or reading.temperature < 36.0:
                sirs_score += 1

        if reading.heart_rate and reading.heart_rate > 90:
            sirs_score += 1

        if reading.respiratory_rate and reading.respiratory_rate > 20:
            sirs_score += 1

        # If SIRS criteria met (2+), flag for sepsis evaluation
        if sirs_score >= 2:
            alert = self._create_alert(
                reading.patient_id,
                AlertSeverity.URGENT,
                "possible_sepsis",
                f"SIRS criteria met (score: {sirs_score}/4)",
                {"sirs_score": sirs_score, "vitals": asdict(reading)},
                "Sepsis workup: lactate, blood cultures, consider antibiotics"
            )
            await self._publish_alert(alert)

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def _initialize_anomaly_detector(self, patient_id: str):
        """Initialize anomaly detector for patient"""
        self.anomaly_detectors[patient_id] = IsolationForest(
            contamination=0.05,  # 5% expected anomaly rate
            random_state=42
        )

    def _create_alert(
        self,
        patient_id: str,
        severity: AlertSeverity,
        alert_type: str,
        message: str,
        details: Dict[str, Any],
        recommended_action: str
    ) -> PatientAlert:
        """Create patient alert"""

        from uuid import uuid4

        return PatientAlert(
            alert_id=str(uuid4()),
            patient_id=patient_id,
            severity=severity.value,
            alert_type=alert_type,
            message=message,
            details=details,
            recommended_action=recommended_action,
            timestamp=datetime.utcnow()
        )

    async def _publish_alert(self, alert: PatientAlert):
        """Publish alert to Kafka"""

        try:
            await self.producer.send(
                settings.kafka_topic_alerts,
                value=asdict(alert)
            )

            logger.info(
                f"Alert published: {alert.alert_type}",
                patient_id=alert.patient_id,
                severity=alert.severity
            )

        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")


# ============================================================================
# FACTORY
# ============================================================================

def create_realtime_monitor() -> RealTimeVitalSignsMonitor:
    """Create real-time monitor"""
    return RealTimeVitalSignsMonitor()
