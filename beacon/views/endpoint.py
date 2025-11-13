import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.utils.requests import deconstruct_request, RequestParams
from aiohttp_cors import CorsViewMixin
from beacon.exceptions.exceptions import AppError
from pydantic import create_model, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import Optional
import json
from beacon.logs.logs import LOG
from pydantic import create_model, ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.utils.modules import load_framework_module

class EndpointView(web.View, CorsViewMixin):
    def __init__(self, request: Request):
        self._request = request
        self._id = generate_txid(self)
        RequestAttributes.ip = None
        RequestAttributes.headers=None
        RequestAttributes.entry_type=None
        RequestAttributes.entry_id=None
        RequestAttributes.pre_entry_type=None
        RequestAttributes.returned_schema=None
        RequestAttributes.returned_apiVersion="v2.2.0"
        RequestAttributes.qparams=RequestParams()
        RequestAttributes.returned_granularity="boolean"
        

    async def get(self):
        try:
            await deconstruct_request(self, self.request)
            return await self.handler()
        except AppError as e:
            response_obj = self.error_builder(e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = self.error_builder(500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')

    async def post(self):
        try:
            await deconstruct_request(self, self.request)
            return await self.handler()
        except AppError as e:
            response_obj =self.error_builder(e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = self.error_builder(500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')

    def create_response(self):
        # Convert the previously created class of the response to JSON:
        classtoJSON = self.classResponse.model_dump(exclude_none=True, by_alias=True)
        return classtoJSON
    
    def error_builder(self, status, message):
        module_meta = load_framework_module(self, "meta")
        module_error = load_framework_module(self, "error")
        try:
            error = module_error.BeaconError(errorCode=status,errorMessage=message)
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=[{"schema": "error-v2.2.0"}],testMode=RequestAttributes.qparams.query.testMode)
            self.classResponse = module_error.ErrorResponse(meta=meta.model_dump(exclude_none=True),error=error.model_dump(exclude_none=True))
            response_obj = self.create_response()
            return response_obj
        except ValidationError as v:
            raise InvalidData('error templates or data are not correct')