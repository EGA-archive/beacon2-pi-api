from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView

class CollectionView(EndpointView): # TODO: nombrar-lo com collection_entry_types
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        collectionsResponseClass = await module.execute_collection_function(self)
        meta_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.meta'
        common_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.common'
        collection_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.collection'
        import importlib
        module_meta = importlib.import_module(meta_module, package=None)
        module_common = importlib.import_module(common_module, package=None)
        module_collection = importlib.import_module(collection_module, package=None)
        try:
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = module_common.ResponseSummary(exists=collectionsResponseClass.count>0,numTotalResults=collectionsResponseClass.count)
            self.classResponse = module_collection.CollectionResponse(meta=meta.model_dump(exclude_none=True),response=module_collection.Collections(collections=collectionsResponseClass.docs).model_dump(exclude_none=True),responseSummary=responseSummary.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            LOG.error(str(v))
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')