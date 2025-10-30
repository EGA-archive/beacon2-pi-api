import aiohttp.web as web
from bson import json_util
from beacon.views.endpoint import EndpointView

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response
    except web.HTTPException as ex:
        if ex.status != 404:
            response_obj = EndpointView.error_builder(EndpointView(request), ex.status, "Unexpected system error: {}".format(ex))
            return web.Response(text=json_util.dumps(response_obj), status=ex.status, content_type='application/json')
        else:
            response_obj = EndpointView.error_builder(EndpointView(request), 404, "Not found")
            return web.Response(text=json_util.dumps(response_obj), status=404, content_type='application/json')