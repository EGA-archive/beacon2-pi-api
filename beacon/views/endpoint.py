import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from beacon.exceptions.builder import error_builder
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.utils.requests import deconstruct_request, RequestParams
from aiohttp_cors import CorsViewMixin
from beacon.exceptions.exceptions import AppError
from pydantic import create_model
from typing import Optional
from beacon.conf.templates import path
import json

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
            self.template_path = path + '/' + RequestAttributes.returned_apiVersion + '/' # TODO: definir variable de forma diferent a la variable de path final. Cridar això en una funció.
            return await self.handler()
        except AppError as e:
            response_obj = await error_builder(self, e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = await error_builder(self, 500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')

    async def post(self):
        try:
            await deconstruct_request(self, self.request)
            self.template_path = path + '/' + RequestAttributes.returned_apiVersion + '/' 
            return await self.handler()
        except AppError as e:
            response_obj = await error_builder(self, e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = await error_builder(self, 500, "Unexpected system error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')


    def create_response(self): # TODO: Comentar cada línia de codi amb el que fem aquí.
        with open(self.template_path, 'r') as template:
            templateJSON = json.load(template)
        classtoJSON = self.classResponse.model_dump(exclude_none=True)
        modelFromTemplate = create_model('modelFromTemplate', **{k: (Optional[type(v)], None) for k, v in templateJSON.items()})
        responseClass = modelFromTemplate.model_validate(classtoJSON)
        JSONresponse = responseClass.model_dump(exclude_none=True)
        return JSONresponse