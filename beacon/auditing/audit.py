import asyncio
import os
import time
from aiohttp import web
import datetime
import json

from beacon.auditing.publisher import AuditPublisher

audit_publisher = AuditPublisher(
    rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://audit_user:audit_password@rabbitmq:5672/")
)

@web.middleware
async def auditing_middleware(request: web.Request, handler):
    # TODO: create middleware to generate only the transaction id
    # txid = generate_txid(request)
    # request["txid"] = txid
    error = None
    event = {}
    try:
        response = await handler(request)
        return response
    except Exception as e:
        error = e
        raise
    finally:
        event["timestamp"]=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        # TODO: event["actor"] -> from request.headers
        # TODO: event["auth"]["method"] -> from request.headers, if valid token -> oidc, otherwise None
        # TODO: event["auth"]["mfa"] -> 
        # TODO: event["source_ip"] -> get from request.ip
        # TODO: relevant change?
        # TODO: reason/context?
        entry_type=request.path.split('/')[-1]
        event["event"]='{}.view'.format(entry_type)
        event["request_id"]=request['txid']
        # TODO: event["target"] -> Get it from request.path, otherwise None?
        # TODO: event["outcome"] Success -> only status or responsedict = json.loads(responsetext) and get if the target was achieved?
        event = {
            "request": {
                "method": request.method,
                "path": request.path,
                "status": response.status if response else 500
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