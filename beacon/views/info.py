from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from pydantic import ValidationError
from beacon.utils.modules import load_framework_module

class InfoView(EndpointView):        
    @log_with_args(config.level)
    async def handler(self):
        # Load the modules that will serve as the meta and the info part of the response
        module_meta = load_framework_module(self, "meta")
        module_info = load_framework_module(self, "info")
        try:
            # Generate the Info class for the info part of the response and populate it with data from the configuration
            info = module_info.InfoBody()
            # Generate the Meta class for the meta part of the response and populate it with data from the configuration
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            # Create the response class that will allocate both Meta and Info parts of the response
            self.classResponse = module_info.InfoResponse(meta=meta.model_dump(exclude_none=True),response=info.model_dump(exclude_none=True))
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')