from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from pydantic import ValidationError

class InfoView(EndpointView):        
    @log_with_args(level)
    async def handler(self):
        meta_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.meta'
        info_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.info'
        import importlib
        module_meta = importlib.import_module(meta_module, package=None)
        module_info = importlib.import_module(info_module, package=None)
        try:
            info = module_info.InfoBody()
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = module_info.InfoResponse(meta=meta.model_dump(exclude_none=True),response=info.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')