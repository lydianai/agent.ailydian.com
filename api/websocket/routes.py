"""
WebSocket API Routes

Real-time WebSocket endpoints for live updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional

from api.websocket.manager import manager, MessageType
from core.logging import get_logger
from core.security import get_current_user  # WebSocket auth

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@router.websocket("/patient/{patient_id}")
async def patient_monitoring_websocket(
    websocket: WebSocket,
    patient_id: str,
    user_id: Optional[str] = Query(None),
):
    """
    WebSocket for real-time patient monitoring

    **Features:**
    - Live vital signs updates
    - NEWS2 score changes
    - Patient alerts
    - Treatment updates

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/patient/P-001?user_id=USER123');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    };
    ```
    """
    await manager.connect(
        websocket,
        connection_type="patient",
        user_id=user_id,
        room_id=f"patient_{patient_id}",
    )

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {
                "type": MessageType.CONNECTION_STATUS,
                "status": "connected",
                "patient_id": patient_id,
                "message": f"Connected to patient {patient_id} monitoring",
            },
            websocket,
        )

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()

            # Echo received message (in production, process the message)
            await manager.send_personal_message(
                {
                    "type": "echo",
                    "data": data,
                },
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Patient monitoring WebSocket disconnected: patient_id={patient_id}")

    except Exception as e:
        logger.error(f"WebSocket error for patient {patient_id}: {e}")
        manager.disconnect(websocket)


@router.websocket("/emergency")
async def emergency_department_websocket(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None),
):
    """
    WebSocket for emergency department updates

    **Features:**
    - Emergency alerts
    - Triage updates
    - Protocol activations
    - Critical patient notifications

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/emergency?user_id=USER123');
    ```
    """
    await manager.connect(
        websocket,
        connection_type="emergency",
        user_id=user_id,
    )

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {
                "type": MessageType.CONNECTION_STATUS,
                "status": "connected",
                "message": "Connected to emergency department",
            },
            websocket,
        )

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            # Process emergency messages
            await manager.send_personal_message(
                {
                    "type": "acknowledgment",
                    "message": "Message received",
                },
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Emergency WebSocket disconnected: user_id={user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for emergency: {e}")
        manager.disconnect(websocket)


@router.websocket("/pharmacy")
async def pharmacy_websocket(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None),
):
    """
    WebSocket for pharmacy updates

    **Features:**
    - Prescription verification results
    - Drug interaction alerts
    - Inventory notifications
    - Medication order status

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/pharmacy?user_id=USER123');
    ```
    """
    await manager.connect(
        websocket,
        connection_type="pharmacy",
        user_id=user_id,
    )

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {
                "type": MessageType.CONNECTION_STATUS,
                "status": "connected",
                "message": "Connected to pharmacy system",
            },
            websocket,
        )

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            await manager.send_personal_message(
                {
                    "type": "acknowledgment",
                    "message": "Message received",
                },
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Pharmacy WebSocket disconnected: user_id={user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for pharmacy: {e}")
        manager.disconnect(websocket)


@router.websocket("/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None),
):
    """
    WebSocket for general system notifications

    **Features:**
    - System announcements
    - User-specific notifications
    - Task assignments
    - Status updates

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/notifications?user_id=USER123');
    ```
    """
    await manager.connect(
        websocket,
        connection_type="notifications",
        user_id=user_id,
    )

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {
                "type": MessageType.CONNECTION_STATUS,
                "status": "connected",
                "message": "Connected to notifications",
            },
            websocket,
        )

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            await manager.send_personal_message(
                {
                    "type": "acknowledgment",
                    "message": "Message received",
                },
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Notifications WebSocket disconnected: user_id={user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for notifications: {e}")
        manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics

    **Returns:** Current WebSocket connection stats
    """
    return manager.get_connection_stats()
