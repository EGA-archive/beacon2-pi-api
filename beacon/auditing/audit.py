import asyncio
import os
import time
from aiohttp import web
from beacon.utils.txid import generate_txid
import datetime

from beacon.auditing.publisher import AuditPublisher

audit_publisher = AuditPublisher(
    rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://audit_user:audit_password@rabbitmq:5672/")
)

@web.middleware
async def audit_middleware(request: web.Request, handler):
    # Attach a correlation ID
    # TODO: create middleware to generate only the transaction id
    txid = generate_txid(request)
    request["txid"] = txid
    start = time.perf_counter()
    error = None
    try:
        response = await handler(request)
        return response
    except Exception as e:
        error = e
        raise
    finally:
        # TODO: remove duration of the request in audit, keep it in the conventional logs
        duration_ms = (time.perf_counter() - start) * 1000

        event = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
            "action": "HTTP_REQUEST",
            "request": {
                "id": txid,
                "method": request.method,
                "path": request.path,
                "status": response.status if response else 500,
                "duration_ms": duration_ms,
            },
            "client": {
                "ip": request.remote,
                "user_agent": request.headers.get("User-Agent"),
            },
        }

        if error:
            event["error"] = {
                "type": type(error).__name__,
            }

        asyncio.create_task(
            audit_publisher.publish(event_type="HTTP_REQUEST",payload=event)
        )