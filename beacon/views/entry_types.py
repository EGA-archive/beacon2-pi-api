from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module

class EntryTypesEndpointView(EndpointView):
    @log_with_args(config.level)
    async def handler(self):
        # Load the modules that will serve as the meta and the entry types part of the response
        module_meta = load_framework_module(self, "meta")
        module_entry_types = load_framework_module(self, "entry_types")
        try:
            # Generate the Entry Types class for the entry types part of the response and populate it with data from the configuration
            entry_types = module_entry_types.EntryTypesSchema.return_schema(module_entry_types.EntryTypesSchema)
            # Generate the Meta class for the meta part of the response and populate it with data from the configuration
            meta = module_meta.InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            # Create the response class that will allocate both Meta and Entry Types parts of the response
            self.classResponse = module_entry_types.EntryTypesResponse(meta=meta.model_dump(exclude_none=True),response=entry_types.model_dump(exclude_none=True))
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
        # Catch the cases where the Entry Types response is not valid against the reference schema
        except ValidationError as v:
            # Stdout the information about what entry type failed about it not being according to the spec
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        # Give a HTTP response with json data application and a 200 status, and the Entry Types object class collected
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')