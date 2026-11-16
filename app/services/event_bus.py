import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

log = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.producer = None
        self.local_events = []

    async def connect(self):
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=500
            )
            await producer.start()
            self.producer = producer
        except Exception as exc:
            log.warning("Kafka unavailable; using local event log: %s", exc)
            self.producer = None

    async def publish(self, event: dict):
        self.local_events.append(event)
        if self.producer:
            try:
                await self.producer.send_and_wait(settings.kafka_topic, event)
            except Exception as exc:
                log.warning("Event publish failed: %s", exc)

    async def close(self):
        if self.producer:
            await self.producer.stop()
