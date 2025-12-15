from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.permissions.__main__ import query_permissions
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.budget.__main__ import insert_budget
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.views.endpoint import EndpointView
from beacon.response.includeResultsetResponses import include_resultSet_responses
from beacon.utils.modules import load_framework_module, load_source_module

class EntryTypeView(EndpointView):
    @query_permissions
    @log_with_args(config.level)
    async def handler(self, datasets, username, time_now):
        # Load the executor from the module that owns the source of the entry type
        module = load_source_module(self, "executor")
        # Execute the function "execute_function" from the executor previously loaded. This will return a class with multiple nested classes, one per each dataset, with the docs retrieved from the source.
        initialMultipleDatasetsResponseClass = await module.execute_function(self, datasets)
        # Exclude the datasets not meant to be in the response depending on the resultSet response to return.
        multipleDatasetsResponseClass = include_resultSet_responses(self, initialMultipleDatasetsResponseClass)
        # Load the module that will serve as the meta part of the response
        module_meta = load_framework_module(self, "meta")
        try:
            # Instantiat the meta class with the attributes collected in the request
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.response_type == 'resultSet':
                # Load the modules that have the classes that will serve as the resultSet and responseSummary part of the response
                module_resultSet = load_framework_module(self, "resultSet")
                module_common = load_framework_module(self, "common")
                # Start the variables (arrays) to collect all the resultSets and datasets to respond with
                list_of_resultSets=[]
                new_datasets=[]
                # Generate the dynamic classes to be instantiated for the response that depend on the request and the entry types available
                ResultsetInstance, Resultsets, ResultsetsResponse = module_resultSet.build_full_dynamic_response()
                # Instantiate the different datasets found using the ResultSetInstance class created and store them in the arrays
                for dataset in multipleDatasetsResponseClass.datasets_responses:
                    try:
                        resultSet = ResultsetInstance.build_response_by_dataset(dataset, RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                        list_of_resultSets.append(resultSet)
                        new_datasets.append(dataset)
                    except ValidationError as v:
                        LOG.error('{} dataset is invalid: {}'.format(dataset.dataset, str(v)))
                # Instantiate the responseSummary and the resultSets with the datasets to be in the response
                responseSummary = module_common.ResponseSummary.build_response_summary_by_dataset(module_common.ResponseSummary, new_datasets)
                resultSets = Resultsets.return_resultSets(list_of_resultSets)
                # Create the response class that will allocate the Meta, responseSumary and resultSet parts of the response
                self.classResponse = ResultsetsResponse.return_response(meta, resultSets, responseSummary)
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
            elif RequestAttributes.response_type == 'count':
                # Load the module that have the class that will serve as the count part of the response
                module_count = load_framework_module(self, "count")
                # Instantiate the responseSummary with the class CountResponseSummary filled in with the counts found for the query
                responseSummary = module_count.CountResponseSummary.build_count_response_summary(module_count.CountResponseSummary, multipleDatasetsResponseClass.total_count)
                # Create the response class that will allocate both the Meta and responseSumary parts of the response
                self.classResponse = module_count.CountResponse(meta=meta, responseSummary=responseSummary)
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
            else:
                # Load the module that have the class that will serve as the boolean part of the response
                module_boolean = load_framework_module(self, "boolean")
                # Instantiate the responseSummary with the class BooleanResponseSummary with the yes/no response found for the query
                responseSummary = module_boolean.BooleanResponseSummary(exists=multipleDatasetsResponseClass.total_count>0)
                # Create the response class that will allocate both the Meta and responseSumary parts of the responses
                self.classResponse = module_boolean.BooleanResponse(meta=meta, responseSummary=responseSummary)
                # Convert the class to JSON to return it in the final stream response
                response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        # If a time could be obtained for the moment of the query, register it for the budget count
        if time_now is not None:
            insert_budget(self, username, time_now)
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')