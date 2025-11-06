from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.validator.framework.common import ResponseSummary
from beacon.validator.framework.meta import Meta
from beacon.validator.framework.collection import CollectionResponse, Collections
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import collectionsTemplate
from beacon.views.endpoint import EndpointView

class CollectionView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        collectionsResponseClass = await module.execute_collection_function(self)
        self.define_final_path(collectionsTemplate)
        try:
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = ResponseSummary(exists=collectionsResponseClass.count>0,numTotalResults=collectionsResponseClass.count)
            collections = Collections(collections=collectionsResponseClass.docs)
            self.classResponse = CollectionResponse(meta=meta,response=collections,responseSummary=responseSummary)
            response_obj = self.create_response()
        except ValidationError as v:
            LOG.error(str(v))
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')