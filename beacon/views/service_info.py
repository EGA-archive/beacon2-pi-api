from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module

class ServiceInfoView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        # Call the module that serves service info response
        module = load_framework_module(self, "service_info")
        try:
            # Create the class that will allocate the data for the service info response
            self.classResponse = module.ServiceInfoResponse()
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')