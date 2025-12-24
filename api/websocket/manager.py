"""
WebSocket Connection Manager

Manages real-time WebSocket connections for:
- Patient vital signs monitoring
- Emergency alerts
- Treatment updates
- Pharmacy notifications
- System notifications
"""

import asyncio
import json
from typing import Dict, List, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

from core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    WebSocket Connection Manager

    Manages active WebSocket connections with support for:
    - Multiple connection types (patient, emergency, pharmacy)
    - Room-based broadcasting
    - User-specific messaging
    - Automatic reconnection handling
    """

    def __init__(self):
        # Active connections by type
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

        # User-specific connections
        self.user_connections: Dict[str, List[WebSocket]] = defaultdict(list)

        # Room-based connections (e.g., patient rooms, departments)
        self.room_connections: Dict[str, List[WebSocket]] = defaultdict(list)

        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(
        self,
        websocket: WebSocket,
        connection_type: str = "general",
        user_id: Optional[str] = None,
        room_id: Optional[str] = None,
    ):
        """
        Accept and register new WebSocket connection

        Args:
            websocket: WebSocket connection
            connection_type: Type of connection (patient, emergency, pharmacy, etc.)
            user_id: User identifier
            room_id: Room identifier
        """
        await websocket.accept()

        # Add to active connections
        self.active_connections[connection_type].append(websocket)

        # Add to user connections
        if user_id:
            self.user_connections[user_id].append(websocket)

        # Add to room connections
        if room_id:
            self.room_connections[room_id].append(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "type": connection_type,
            "user_id": user_id,
            "room_id": room_id,
            "connected_at": datetime.utcnow(),
        }

        logger.info(
            f"WebSocket connected: type={connection_type}, user={user_id}, room={room_id}, "
            f"total_connections={self._get_total_connections()}"
        )

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect and cleanup WebSocket connection

        Args:
            websocket: WebSocket connection to disconnect
        """
        metadata = self.connection_metadata.get(websocket, {})
        connection_type = metadata.get("type", "general")
        user_id = metadata.get("user_id")
        room_id = metadata.get("room_id")

        # Remove from active connections
        if websocket in self.active_connections[connection_type]:
            self.active_connections[connection_type].remove(websocket)

        # Remove from user connections
        if user_id and websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)

        # Remove from room connections
        if room_id and websocket in self.room_connections[room_id]:
            self.room_connections[room_id].remove(websocket)

        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

        logger.info(
            f"WebSocket disconnected: type={connection_type}, user={user_id}, room={room_id}, "
            f"remaining_connections={self._get_total_connections()}"
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific WebSocket connection

        Args:
            message: Message data (dict)
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_type(self, message: dict, connection_type: str):
        """
        Broadcast message to all connections of specific type

        Args:
            message: Message data (dict)
            connection_type: Connection type (patient, emergency, pharmacy, etc.)
        """
        disconnected = []

        for connection in self.active_connections[connection_type]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to type {connection_type}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_to_user(self, message: dict, user_id: str):
        """
        Broadcast message to all connections of specific user

        Args:
            message: Message data (dict)
            user_id: User identifier
        """
        disconnected = []

        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_to_room(self, message: dict, room_id: str):
        """
        Broadcast message to all connections in specific room

        Args:
            message: Message data (dict)
            room_id: Room identifier
        """
        disconnected = []

        for connection in self.room_connections[room_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to room {room_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast message to all active connections

        Args:
            message: Message data (dict)
        """
        disconnected = []

        for connection_type, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to all: {e}")
                    disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    def _get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self.active_connections.values())

    def get_connection_stats(self) -> Dict:
        """
        Get connection statistics

        Returns:
            Dict with connection statistics
        """
        return {
            "total_connections": self._get_total_connections(),
            "connections_by_type": {
                conn_type: len(conns)
                for conn_type, conns in self.active_connections.items()
            },
            "active_users": len(self.user_connections),
            "active_rooms": len(self.room_connections),
        }


# Global connection manager instance
manager = ConnectionManager()


# ============================================================================
# MESSAGE TYPES
# ============================================================================

class MessageType:
    """WebSocket message types"""

    # Patient monitoring
    VITAL_SIGNS_UPDATE = "vital_signs_update"
    PATIENT_ALERT = "patient_alert"
    NEWS2_SCORE_UPDATE = "news2_score_update"

    # Emergency
    EMERGENCY_ALERT = "emergency_alert"
    TRIAGE_UPDATE = "triage_update"
    PROTOCOL_ACTIVATION = "protocol_activation"

    # Treatment
    TREATMENT_PLAN_UPDATE = "treatment_plan_update"
    MEDICATION_ORDER = "medication_order"

    # Pharmacy
    PRESCRIPTION_VERIFICATION = "prescription_verification"
    DRUG_INTERACTION_ALERT = "drug_interaction_alert"

    # System
    SYSTEM_NOTIFICATION = "system_notification"
    CONNECTION_STATUS = "connection_status"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def send_vital_signs_update(patient_id: str, vital_signs: dict):
    """
    Send vital signs update to monitoring room

    Args:
        patient_id: Patient identifier
        vital_signs: Vital signs data
    """
    message = {
        "type": MessageType.VITAL_SIGNS_UPDATE,
        "patient_id": patient_id,
        "data": vital_signs,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_room(message, f"patient_{patient_id}")


async def send_emergency_alert(alert_data: dict, severity: str = "high"):
    """
    Send emergency alert to emergency department

    Args:
        alert_data: Alert data
        severity: Alert severity (critical, high, medium, low)
    """
    message = {
        "type": MessageType.EMERGENCY_ALERT,
        "severity": severity,
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_type(message, "emergency")


async def send_protocol_activation(protocol_name: str, patient_id: str):
    """
    Send protocol activation notification

    Args:
        protocol_name: Name of activated protocol
        patient_id: Patient identifier
    """
    message = {
        "type": MessageType.PROTOCOL_ACTIVATION,
        "protocol": protocol_name,
        "patient_id": patient_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_type(message, "emergency")


async def send_drug_interaction_alert(user_id: str, interaction_data: dict):
    """
    Send drug interaction alert to pharmacist

    Args:
        user_id: Pharmacist user ID
        interaction_data: Interaction details
    """
    message = {
        "type": MessageType.DRUG_INTERACTION_ALERT,
        "data": interaction_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_user(message, user_id)


async def send_system_notification(notification: str, users: Optional[List[str]] = None):
    """
    Send system notification

    Args:
        notification: Notification message
        users: List of user IDs (None = broadcast to all)
    """
    message = {
        "type": MessageType.SYSTEM_NOTIFICATION,
        "message": notification,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if users:
        for user_id in users:
            await manager.broadcast_to_user(message, user_id)
    else:
        await manager.broadcast_to_all(message)
