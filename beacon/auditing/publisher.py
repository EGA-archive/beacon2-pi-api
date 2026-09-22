import asyncio
import json
from typing import Any, Dict

import aio_pika
from aio_pika import Message, DeliveryMode

from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config

class AuditPublisher:
    def __init__(self, rabbitmq_url: str, exchange_name: str = "audit_logs"):
        # Initialize connection string to rabbitmq, connection with aio_pika and logger
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self._connection: aio_pika.Connection | None = None
        self._channel: aio_pika.Channel | None = None
        self._exchange: aio_pika.Exchange | None = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self.LOG = initialize_logger(config.level)

    async def connect(self):
        # Check if rabbit mq is already initialized
        if self._initialized:
            return
        # If it isn't, initialize connection to it with aio pika for more robust connection (and ensure nothing is lost in case of server down)
        async with self._lock:
            if self._initialized:
                return
            self._connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=100)
            self._exchange = await self._channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            queue = await self._channel.declare_queue("audit_queue", durable=True)
            await queue.bind(exchange=self._exchange, routing_key="audit.*")
            self._initialized = True
            self.LOG.info("Audit publisher connected to RabbitMQ")

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        """Fire-and-forget publish. Call via asyncio.create_task() from handlers."""
        if not self._initialized:
            await self.connect()

        message_body = json.dumps({
            "event_type": event_type,
            "payload": payload,
        }).encode("utf-8")

        message = Message(
            body=message_body,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        try:
            routing_key = f"audit.{event_type}"
            await self._exchange.publish(message=message, routing_key=routing_key)
        except Exception as e:
            self.LOG.error("Failed to publish audit event (non-blocking): %s", e)

    async def close(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()