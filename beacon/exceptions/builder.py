from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.request.classes import RequestAttributes
import json
from beacon.validator.framework.meta import Meta
from beacon.validator.framework.error import ErrorResponse, BeaconError
from pydantic import create_model, Field, ValidationError
from typing import Optional
from beacon.exceptions.exceptions import InvalidData

@log_with_args(level)
async def error_builder(self, status, message):
    try:
        with open('beacon/response/templates/{}/error.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        error = BeaconError(errorCode=status,errorMessage=message)
        meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=[{"schema": "error-v2.2.0"}],testMode=RequestAttributes.qparams.query.testMode)
        errorResponse = ErrorResponse(meta=meta,error=error)
        errorResponse = errorResponse.model_dump(exclude_none=True)
        ErrorFromTemplate = create_model('ErrorFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = ErrorFromTemplate.model_validate(errorResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except ValidationError as v:
        raise InvalidData('error templates or data are not correct')