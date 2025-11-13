from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView

class MapView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        meta_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.meta'
        map_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.map'
        import importlib
        module_meta = importlib.import_module(meta_module, package=None)
        module_map = importlib.import_module(map_module, package=None)
        try:
            map = module_map.MapSchema.populate_endpoints(module_map.MapSchema)
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = module_map.MapResponse(meta=meta.model_dump(exclude_none=True),response=map.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')