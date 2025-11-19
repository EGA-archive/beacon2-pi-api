from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module, load_source_module

class CollectionEntryTypeView(EndpointView):
    @log_with_args(level)
    async def handler(self):
        module = load_source_module(self, 'executor')
        collectionsResponseClass = await module.execute_collection_function(self)
        module_meta = load_framework_module(self, "meta")
        module_common = load_framework_module(self, "common")
        module_collection = load_framework_module(self, "collection")
        try:
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = module_common.ResponseSummary(exists=collectionsResponseClass.count>0,numTotalResults=collectionsResponseClass.count)
            self.classResponse = module_collection.CollectionResponse(meta=meta.model_dump(exclude_none=True),response=module_collection.Collections(collections=collectionsResponseClass.docs).model_dump(exclude_none=True),responseSummary=responseSummary.model_dump(exclude_none=True))
            response_obj = self.create_response()
        except ValidationError as v:
            LOG.error(str(v))
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')