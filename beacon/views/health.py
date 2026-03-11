from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import InvalidData
from exceptions.exceptions import DatabaseIsDown
from beacon.utils.modules import check_database_connections
from beacon.views.endpoint import EndpointView

class HealthView(EndpointView):        
    @log_with_args(config.level)
    async def handler(self):
        try:
            check_database_connections()
            response_obj = {"status": "ok"}
        except DatabaseIsDown as e:
            response_obj = {"status": "shutting down", "error": e}
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')