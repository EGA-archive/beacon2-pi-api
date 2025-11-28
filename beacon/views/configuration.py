from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module

class ConfigurationView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        # Load the modules that will serve as the meta and the configuration parts of the response
        module_meta = load_framework_module(self, "meta")
        module_configuration = load_framework_module(self, "configuration")
        try:
            # Generate the configuration class for the configuration part of the response and populate it with data from the configuration
            configuration = module_configuration.ConfigurationSchema.return_schema(module_configuration.ConfigurationSchema)
            # Generate the Meta class for the meta part of the response and populate it with data from the configuration
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            # Create the response class that will allocate both Meta and Configuration parts of the response
            self.classResponse = module_configuration.ConfigurationResponse(meta=meta.model_dump(exclude_none=True),response=configuration.model_dump(exclude_none=True))
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')