import aiohttp.web as web
from bson import json_util
from beacon.views.endpoint import EndpointView

@web.middleware
async def error_middleware(request, handler):
    try:
        # Aa generic handler manages the request before arriving to the app.
        response = await handler(request)
        # If the request is not pointing to an unknown endpoint, the response is managed accordingly.
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