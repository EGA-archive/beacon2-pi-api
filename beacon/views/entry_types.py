from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.validator.framework.meta import InformationalMeta
from beacon.validator.framework.entry_types import EntryTypesSchema, EntryTypesResponse
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import entryTypesTemplate
from beacon.views.endpoint import EndpointView

class EntryTypesView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        self.define_final_path(entryTypesTemplate)
        try:
            entry_types = EntryTypesSchema.return_schema(EntryTypesSchema)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = EntryTypesResponse(meta=meta,response=entry_types)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')