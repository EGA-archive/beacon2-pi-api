from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
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
    @log_with_args(level)
    async def handler(self, datasets, username, time_now):
        module = load_source_module(self, "executor")
        initialMultipleDatasetsResponseClass = await module.execute_function(self, datasets)
        multipleDatasetsResponseClass = include_resultSet_responses(self, initialMultipleDatasetsResponseClass)
        module_meta = load_framework_module(self, "meta")
        module_resultSet = load_framework_module(self, "resultSet")
        module_common = load_framework_module(self, "common")
        module_count = load_framework_module(self, "count")
        module_boolean = load_framework_module(self, "boolean")
        try:
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.response_type == 'resultSet':
                list_of_resultSets=[]
                new_datasets=[]
                ResultsetInstance, Resultsets, ResultsetsResponse = module_resultSet.build_full_dynamic_response()
                for dataset in multipleDatasetsResponseClass.datasets_responses:
                    try:
                        resultSet = ResultsetInstance.build_response_by_dataset(dataset, RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                        list_of_resultSets.append(resultSet)
                        new_datasets.append(dataset)
                    except ValidationError as v:
                        LOG.error('{} dataset is invalid: {}'.format(dataset.dataset, str(v)))
                responseSummary = module_common.ResponseSummary.build_response_summary_by_dataset(module_common.ResponseSummary, new_datasets)
                resultSets = Resultsets.return_resultSets(list_of_resultSets)
                self.classResponse = ResultsetsResponse.return_response(meta, resultSets, responseSummary)
                response_obj = self.create_response()
            elif RequestAttributes.response_type == 'count':
                responseSummary = module_count.CountResponseSummary.build_count_response_summary(module_count.CountResponseSummary, multipleDatasetsResponseClass.total_count)
                self.classResponse = module_count.CountResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
            else:
                responseSummary = module_boolean.BooleanResponseSummary(exists=multipleDatasetsResponseClass.total_count>0)
                self.classResponse = module_boolean.BooleanResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        if time_now is not None:
            insert_budget(self, username, time_now)
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')