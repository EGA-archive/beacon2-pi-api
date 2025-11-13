from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView

class ServiceInfoView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.service_info'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        try:
            self.classResponse = module.ServiceInfoResponse()
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')