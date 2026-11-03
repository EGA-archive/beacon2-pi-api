import aiohttp.web as web
from bson import json_util
from beacon.views.endpoint import EndpointView
import asyncio
import uuid

@web.middleware
async def error_before_request_reaches_destination_middleware(request, handler):
    try:
        # Aa generic handler manages the request before arriving to the app.
        response = await handler(request)
        # If the request is pointing to a known endpoint, the response is managed accordingly.
        if response.status != 404:
            return response
    except web.HTTPException as ex:
        # If the request gave an error befor reaching a destination, we return a generic response for the error.
        if ex.status != 404:
            response_obj = EndpointView.error_builder(EndpointView(request), ex.status, "Unexpected system error: {}".format(ex))
            return web.Response(text=json_util.dumps(response_obj), status=ex.status, content_type='application/json')
        # Else, we return the not found for the not found requested endpoint.
        else:
            response_obj = EndpointView.error_builder(EndpointView(request), 404, "Not found")
            return web.Response(text=json_util.dumps(response_obj), status=404, content_type='application/json')
        
@web.middleware
async def track_pending_requests_middleware(request, handler):
    # The purpose of this middleware is to get a list of the pending tasks to process (1 task = 1 request), to have a registry for the ones that are still pending to finish,
    # this allows the app to know what requests need to be processed or gracefully finalized in case a shutdown happens so a response is always given back to the client
    app = request.app
    task = asyncio.current_task()

    app['pending_requests'].add(task)

    try:
        return await handler(request)

    finally:
        if not app.get('shutting_down'):
            app['pending_requests'].discard(task)

@web.middleware
async def generate_txid(request: web.Request, handler):
    # Generate a unique id and get the first 9 characters to show it in the logs as the transaction id.
    uniqueid = uuid.uuid4()
    uniqueid = str(uniqueid)[0:8]
    request['txid']=uniqueid
    return await handler(request)