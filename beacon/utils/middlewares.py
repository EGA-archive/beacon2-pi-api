import aiohttp.web as web
from bson import json_util
from beacon.views.endpoint import EndpointView
import asyncio
import asyncio

from datetime import datetime, timezone


#from beacon.logs.audit.audit_context import AuditContext

@web.middleware
async def error_middleware(request, handler):

    try:

        response = await handler(request)

        if response.status != 404:
            return response

        response_obj = EndpointView.error_builder(
            EndpointView(request),
            404,
            "Not found"
        )

        return web.Response(
            text=json_util.dumps(response_obj),
            status=404,
            content_type="application/json"
        )

    except web.HTTPException as ex:

        response_obj = EndpointView.error_builder(
            EndpointView(request),
            ex.status,
            str(ex)
        )

        return web.Response(
            text=json_util.dumps(response_obj),
            status=ex.status,
            content_type="application/json"
        )
        
@web.middleware
async def track_requests_middleware(request, handler):
    app = request.app
    task = asyncio.current_task()

    app['pending_requests'].add(task)

    try:
        return await handler(request)

    finally:
        if not app.get('shutting_down'):
            app['pending_requests'].discard(task)

"""
@web.middleware
async def audit_middleware(request, handler):

    app = request.app
    logger = app["logger"]

    # Generate the Beacon transaction ID
    request_id = generate_txid(request)

    audit = AuditContext(request_id=request_id)

    # Make the audit context accessible to all downstream components
    request["audit"] = audit
    request["request_id"] = request_id

    start_time = time.perf_counter()

    try:

        # 2. Collect the initial HTTP request information
        audit.collect_http_request(request)

        # 3. Execute the remaining middleware and endpoint
        response = await handler(request)

        # 4. Collect the final HTTP response information
        audit.collect_http_response(response)

        return response

    except asyncio.CancelledError:

        audit.finalize(status="cancelled")

        raise

    except web.HTTPException as exc:

        audit.set_error(
            type=type(exc).__name__,
            stage="request_processing",
            http_status=exc.status,
            expected=exc.status < 500
        )

        raise

    except Exception as exc:

        audit.set_error(
            type=type(exc).__name__,
            stage="request_processing",
            http_status=500,
            expected=False
        )

        logger.exception(
            "Unexpected exception during request processing"
        )

        raise

    finally:

        # 5. Calculate the total request duration
        audit.data.duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        audit.data.completed_at = datetime.now(
            timezone.utc
        )

        # 6. Determine the final audit status
        if audit.data.status == "in_progress":
            audit.finalize_from_http_status()

        # 7. Persist the audit record
        try:

            await audit.persist()

        except Exception:

            logger.exception(
                "Failed to persist audit record: %s",
                request_id
            )
"""