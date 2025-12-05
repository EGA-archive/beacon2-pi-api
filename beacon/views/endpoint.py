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
        # Initialize dhe endpoint with some of the attributes that will need to be collected later on
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
        #try:
        # Decompound/validate the request and store the attributes needed in the class RequestAttributes
        await deconstruct_request(self, self.request)
        # Call the handler function for the view assigned to the queried endpoint
        return await self.handler()
        """
        except AppError as e:
            # In case a handled error occurs, return the error message and status for it
            response_obj = self.error_builder(e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            # In case an unhandled error occurs, return a 500 and the generic error message below
            response_obj = self.error_builder(500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')
        """

    async def post(self):
        #try:
        # Decompound/validate the request and store the attributes needed in the class RequestAttributes
        await deconstruct_request(self, self.request)
        # Call the handler function for the view assigned to the queried endpoint
        return await self.handler()
        """
        except AppError as e:
            # In case a handled error occurs, return the error message and status for it
            response_obj = self.error_builder(e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            # In case an unhandled error occurs, return a 500 and the generic error message below
            response_obj = self.error_builder(500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')
        """

    def create_response(self):
        # Convert the previously created class of the response to JSON:
        classtoJSON = self.classResponse.model_dump(exclude_none=True, by_alias=True)
        return classtoJSON
    
    def error_builder(self, status, message):
        # Load the modules that have the classes that will serve as the meta and error part of the response
        module_meta = load_framework_module(self, "meta")
        module_error = load_framework_module(self, "error")
        try:
            # Instantiate the error class with the status and the message collected during the error handling
            error = module_error.BeaconError(errorCode=status,errorMessage=message)
            # Instantiat the meta class with the attributes collected in the request
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=[{"schema": "error-v2.2.0"}],testMode=RequestAttributes.qparams.query.testMode)
            # Create the response class that will allocate the Meta and error parts of the response
            self.classResponse = module_error.ErrorResponse(meta=meta.model_dump(exclude_none=True),error=error.model_dump(exclude_none=True))
            # Convert the class to JSON to return it in the final stream response
            response_obj = self.create_response()
            return response_obj
        except ValidationError as v:
            raise InvalidData('error templates or data are not correct')