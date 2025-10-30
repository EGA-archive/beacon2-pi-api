from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import aiohttp.web as web
from beacon.permissions.__main__ import query_permissions
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.budget.__main__ import insert_budget
from beacon.validator.framework.meta import Meta
from beacon.validator.framework.common import ResponseSummary
from beacon.validator.framework.resultSet import ResultsetInstance, ResultsetsResponse, Resultsets 
from beacon.validator.framework.count import CountResponseSummary, CountResponse
from beacon.validator.framework.boolean import BooleanResponseSummary, BooleanResponse
from pydantic import ValidationError
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import resultSetsTemplate, countTemplate, booleanTemplate
from beacon.views.endpoint import EndpointView

class PhenoGenoView(EndpointView):
    @query_permissions
    @log_with_args(level)
    async def handler(self, datasets, username, time_now):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'# TODO: Comentar.
        import importlib
        module = importlib.import_module(complete_module, package=None)
        datasets_docs, datasets_count, count, include, datasets = await module.execute_function(self, datasets) # TODO: Això s'ha de retornar en una classe.
        try:
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.response_type == 'resultSet':
                self.define_final_path(resultSetsTemplate)
                list_of_resultSets=[]
                new_datasets=[]
                for dataset in datasets:
                    try:
                        resultSet = ResultsetInstance.build_response_by_dataset(ResultsetInstance,dataset, datasets_docs, datasets_count,RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                        list_of_resultSets.append(resultSet)
                        new_datasets.append(dataset)
                    except ValidationError as v:
                        LOG.error('{} dataset is invalid: {}'.format(dataset.dataset, str(v)))
                responseSummary = ResponseSummary.build_response_summary_by_dataset(ResponseSummary, new_datasets, datasets_count)
                resultSets = Resultsets.return_resultSets(Resultsets, list_of_resultSets)
                self.classResponse = ResultsetsResponse.return_response(ResultsetsResponse, meta, resultSets, responseSummary)
                response_obj = self.create_response()
            elif RequestAttributes.response_type == 'count':
                self.define_final_path(countTemplate)
                responseSummary = CountResponseSummary.build_count_response_summary(CountResponseSummary, count)
                self.classResponse = CountResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
            else:
                self.define_final_path(booleanTemplate)
                responseSummary = BooleanResponseSummary(exists=count>0)
                self.classResponse = BooleanResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        if time_now is not None:
            insert_budget(self, username, time_now)
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')