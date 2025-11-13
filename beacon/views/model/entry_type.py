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

class EntryTypeView(EndpointView):
    @query_permissions
    @log_with_args(level)
    async def handler(self, datasets, username, time_now):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'# TODO: Comentar.
        import importlib
        module = importlib.import_module(complete_module, package=None)
        initialMultipleDatasetsResponseClass = await module.execute_function(self, datasets)
        multipleDatasetsResponseClass = include_resultSet_responses(self, initialMultipleDatasetsResponseClass)
        meta_module='beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.meta'
        resultSet_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.resultSet'
        common_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.common'
        count_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.count'
        boolean_module = 'beacon.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.framework.boolean'
        import importlib
        module_meta = importlib.import_module(meta_module, package=None)
        module_resultSet = importlib.import_module(resultSet_module, package=None)
        module_common = importlib.import_module(common_module, package=None)
        module_count = importlib.import_module(count_module, package=None)
        module_boolean = importlib.import_module(boolean_module, package=None)
        try:
            meta = module_meta.Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.response_type == 'resultSet':
                list_of_resultSets=[]
                new_datasets=[]
                for dataset in multipleDatasetsResponseClass.datasets_responses:
                    try:
                        resultSet = module_resultSet.ResultsetInstance.build_response_by_dataset(module_resultSet.ResultsetInstance, dataset, RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                        list_of_resultSets.append(resultSet)
                        new_datasets.append(dataset)
                    except ValidationError as v:
                        LOG.error('{} dataset is invalid: {}'.format(dataset.dataset, str(v)))
                responseSummary = module_common.ResponseSummary.build_response_summary_by_dataset(module_common.ResponseSummary, new_datasets)
                resultSets = module_resultSet.Resultsets.return_resultSets(module_resultSet.Resultsets, list_of_resultSets)
                self.classResponse = module_resultSet.ResultsetsResponse.return_response(module_resultSet.ResultsetsResponse, meta, resultSets, responseSummary)
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