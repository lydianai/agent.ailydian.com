"""
Message Bus

Event-driven communication system for agents.
Lightweight in-memory implementation (production would use Kafka/RabbitMQ).
"""

import asyncio
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Event message"""
    message_id: str
    topic: str
    payload: Dict[str, Any]
    sender_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    In-memory message bus for agent communication

    Features:
    - Publish/subscribe pattern
    - Topic-based routing
    - Async message handling
    - Message history
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize message bus

        Args:
            max_history: Maximum messages to keep in history
        """
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Message] = []
        self.max_history = max_history
        self._message_counter = 0

        logger.info("Message Bus initialized")

    async def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        sender_id: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Publish message to topic

        Args:
            topic: Topic name
            payload: Message payload
            sender_id: Optional sender identifier
            **metadata: Additional metadata

        Returns:
            Message ID
        """
        self._message_counter += 1
        message_id = f"msg_{self._message_counter}"

        message = Message(
            message_id=message_id,
            topic=topic,
            payload=payload,
            sender_id=sender_id,
            metadata=metadata
        )

        # Store in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)

        # Notify subscribers
        subscribers = self.subscribers.get(topic, [])
        logger.debug(f"Publishing to {topic}: {len(subscribers)} subscribers")

        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Error in subscriber callback: {e}")

        logger.debug(f"Published message {message_id} to topic {topic}")
        return message_id

    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to a topic

        Args:
            topic: Topic name
            callback: Callback function (can be async)
        """
        self.subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from a topic

        Args:
            topic: Topic name
            callback: Callback function to remove
        """
        if topic in self.subscribers:
            try:
                self.subscribers[topic].remove(callback)
                logger.info(f"Unsubscribed from topic: {topic}")
            except ValueError:
                logger.warning(f"Callback not found for topic: {topic}")

    def get_message_history(
        self,
        topic: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Get message history

        Args:
            topic: Filter by topic (None = all topics)
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        messages = self.message_history

        if topic:
            messages = [m for m in messages if m.topic == topic]

        return messages[-limit:]

    def get_topics(self) -> List[str]:
        """Get list of all topics with subscribers"""
        return list(self.subscribers.keys())

    def clear_history(self):
        """Clear message history"""
        self.message_history.clear()
        logger.info("Message history cleared")
