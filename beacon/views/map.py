from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module

class MapView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        module_meta = load_framework_module(self, "meta")
        module_map = load_framework_module(self, "map")
        try:
            map = module_map.MapSchema.populate_endpoints(module_map.MapSchema)
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = module_map.MapResponse(meta=meta.model_dump(exclude_none=True),response=map.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')