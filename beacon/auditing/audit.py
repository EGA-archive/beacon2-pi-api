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

def get_client_ip(request: web.Request) -> str | None:
    return request.remote


def get_outcome(status: int) -> str:
    if 200 <= status < 300:
        return "success"

    if 300 <= status < 400:
        return "redirect"

    if 400 <= status < 500:
        return "failure"

    if 500 <= status < 600:
        return "failure"

    return "unknown"


def get_event_name(request: web.Request) -> str:
    # TODO: get the route from the route function better than from the URL
    endpoint = request.match_info.route.name

    if endpoint:
        return f"{endpoint}.view"

    path_parts = [
        part for part in request.path.strip("/").split("/")
        if part
    ]

    resource = path_parts[0] if path_parts else "root"

    return f"{resource}.view"

@web.middleware
async def auditing_middleware(request: web.Request, handler):
    response = None
    error = None

    try:
        response = await handler(request)
        return response

    except Exception as exc:
        error = exc
        raise

    finally:
        auth = request.get("auth", {})

        status = response.status if response else 500

        event = {

            "request_id": request["txid"],

            "actor": auth.get("actor"),

            "auth": {
                "method": auth.get("method"),
                "acr": auth.get("acr"),
            },

            "source_ip": request.remote,

            "target": request.get("audit_target"),

            "request": {
                "method": request.method,
                "path": request.path,
                "status": status,
                "outcome": (
                    "success"
                    if 200 <= status < 300
                    else "failure"
                ),
            },

            "client": {
                "user_agent": request.headers.get("User-Agent"),
            },
        }

        if error:
            event["error"] = {
                "type": type(error).__name__,
            }

        context = request.get("audit_context")
        if context:
            event["context"] = context

        asyncio.create_task(
            audit_publisher.publish(
                event_type=get_event_name(request),
                payload=event,
            )
        )
