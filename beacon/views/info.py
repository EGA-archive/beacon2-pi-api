from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.validator.framework.info import InfoBody, InfoResponse
from beacon.validator.framework.meta import InformationalMeta
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import infoTemplate
from beacon.views.endpoint import EndpointView
from pydantic import ValidationError

class InfoView(EndpointView):        
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + infoTemplate
        try:
            info = InfoBody()
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = InfoResponse(meta=meta,response=info)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')