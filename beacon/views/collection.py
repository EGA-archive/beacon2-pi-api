from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.utils.modules import load_framework_module, load_source_module
from beacon.utils.checks import state_check
import asyncio

class CollectionEntryTypeView(EndpointView):
    @state_check
    @log_with_args(config.level)
    async def handler(self):
        # Load the executor from the module that owns the source of the entry type
        module = load_source_module(self, 'executor')
        # Execute the function "execute_collection_function" from the executor previously loaded. This will return a class with the docs for the collections retrieved from the source.
        collectionsResponseClass = await module.execute_collection_function(self)
        # Load the modules that have the classes that will serve as the meta, collections and responseSummary part of the response
        module_meta = load_framework_module(self, "meta")
        module_common = load_framework_module(self, "common")
        module_collection = load_framework_module(self, "collection")
        # Generate the dynamic class to be instantiated for the response that depend on the request and the collection entry types available
        Collections = module_collection.make_Collections()
        CollectionResponse = module_collection.make_CollectionResponse(Collections)
        try:
            # Instantiate the meta class with the attributes collected in the request
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.qparams.query.requestedGranularity == 'record' and RequestAttributes.allowed_granularity == 'record':
                # Instantiate the responseSummary class with the counts and yes/no found to be in the response
                responseSummary = module_common.ResponseSummary(exists=collectionsResponseClass.count>0,numTotalResults=collectionsResponseClass.count)
                # Instantiate the final response class with the meta, responseSumary end collections classes generated previously
                self.classResponse = CollectionResponse(meta=meta.model_dump(exclude_none=True),response=Collections(collections=collectionsResponseClass.docs).model_dump(exclude_none=True),responseSummary=responseSummary.model_dump(exclude_none=True))
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
            elif RequestAttributes.qparams.query.requestedGranularity == 'count' and RequestAttributes.allowed_granularity in ['count', 'record']:
                # Load the module that have the class that will serve as the count part of the response
                module_count = load_framework_module(self, "count")
                # Instantiate the responseSummary with the class CountResponseSummary filled in with the counts found for the query
                responseSummary = module_count.CountResponseSummary.build_count_response_summary(module_count.CountResponseSummary, collectionsResponseClass.count)
                # Create the response class that will allocate both the Meta and responseSumary parts of the response
                self.classResponse = module_count.CountResponse(meta=meta, responseSummary=responseSummary)
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
            else:
                # Load the module that have the class that will serve as the boolean part of the response
                module_boolean = load_framework_module(self, "boolean")
                # Instantiate the responseSummary with the class BooleanResponseSummary with the yes/no response found for the query
                responseSummary = module_boolean.BooleanResponseSummary(exists=collectionsResponseClass.count>0)
                # Create the response class that will allocate both the Meta and responseSumary parts of the responses
                self.classResponse = module_boolean.BooleanResponse(meta=meta, responseSummary=responseSummary)
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
        except ValidationError as v:
            self.LOG.error(str(v))
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')