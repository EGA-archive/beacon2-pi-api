import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.utils.requests import deconstruct_request, RequestParams
from aiohttp_cors import CorsViewMixin
from beacon.exceptions.exceptions import AppError
from pydantic import create_model, ConfigDict
from typing import Optional
from beacon.conf.templates import path
import json
from beacon.logs.logs import LOG
from beacon.validator.framework.meta import Meta
from beacon.validator.framework.error import ErrorResponse, BeaconError
from pydantic import create_model, ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import errorTemplate

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
        RequestAttributes.returned_apiVersion="v2.0.0"
        RequestAttributes.qparams=RequestParams()
        RequestAttributes.returned_granularity="boolean"
        

    async def get(self):
        try:
            await deconstruct_request(self, self.request)
            self.define_root_path()
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
            self.define_root_path()
            return await self.handler()
        except AppError as e:
            response_obj =self.error_builder(e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = self.error_builder(500, "Unexpected system error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')

    def define_root_path(self):
        self.root_path = path + '/' + RequestAttributes.returned_apiVersion + '/'

    def define_final_path(self, template_name):
        self.template_path = self.root_path + template_name

    def create_response(self):
        # Save the template from path, e.g. response/templates/v2.0.0 as a JSON:
        with open(self.template_path, 'r') as template:
            templateJSON = json.load(template)
        # Convert the previously created class of the response to JSON:
        classtoJSON = self.classResponse.model_dump(exclude_none=True)
        # Create a class with the JSON of the template. The extra "ignore" will remove all extra properties when instatiating a new class from a JSON:
        modelFromTemplate = create_model('modelFromTemplate', **{k: (Optional[type(v)] if type(v) is not dict else create_model(str(k),**{k1: (Optional[type(v1)], None) for k1, v1 in v.items()}), None) for k, v in templateJSON.items()}, model_config=ConfigDict(extra='ignore'))
        # Instantiate a template class with the values from the JSON coming fro the initial response class:
        responseClass = modelFromTemplate.model_validate(classtoJSON)
        # Convert the template instance class created to JSON:
        JSONresponse = responseClass.model_dump(exclude_none=True)
        return JSONresponse
    
    def error_builder(self, status, message):
        try:
            self.define_root_path()
            self.define_final_path(errorTemplate)
            error = BeaconError(errorCode=status,errorMessage=message)
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=[{"schema": "error-v2.2.0"}],testMode=RequestAttributes.qparams.query.testMode)
            self.classResponse = ErrorResponse(meta=meta,error=error)
            response_obj = self.create_response()
            return response_obj
        except ValidationError as v:
            raise InvalidData('error templates or data are not correct')