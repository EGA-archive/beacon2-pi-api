import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args, level, LOG
from typing import Optional
from beacon.request.parameters import RequestParams
from beacon.connections.mongo.datasets import get_full_datasets, get_dataset_with_id
from beacon.connections.mongo.cohorts import get_cohorts, get_cohort_with_id
from beacon.conf import analysis, biosample, cohort, dataset as dtaset, genomicVariant, individual, run
from beacon.connections.mongo.resultSets import get_resultSet, get_resultSet_with_id, get_variants_of_resultSet, get_resultSet_of_variants, get_analyses_of_resultSet, get_biosamples_of_resultSet, get_resultSet_of_dataset, get_variants_of_dataset, get_resultSet_of_cohort, get_variants_of_cohort, get_runs_of_resultSet, get_individuals_of_resultSet
from beacon.conf import individual, genomicVariant, biosample, run, dataset as dtaset
from beacon.connections.mongo.__init__ import biosamples, genomicVariations, individuals, analyses, runs, datasets, cohorts
from beacon.response.schemas import DefaultSchemas
from beacon.request.classes import ErrorClass, RequestAttributes
from aiohttp import web

@log_with_args(level)
async def execute_function(self, datasets: list, qparams: RequestParams):
    include = qparams.query.includeResultsetResponses
    limit = qparams.query.pagination.limit
    datasets_docs={}
    datasets_count={}
    new_count=0
    try:
        entry_type_splitted = RequestAttributes.entry_type.split('.')
        RequestAttributes.entry_type = entry_type_splitted[1]
        RequestAttributes.pre_entry_type = entry_type_splitted[0]
    except Exception:
        pass
    if RequestAttributes.entry_type==genomicVariant.endpoint_name:
        try:
            if genomicVariant.allow_queries_without_filters == False and qparams.query.filters == [] and qparams.query.requestParameters == []:
                ErrorClass.error_code=400
                ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(genomicVariant.endpoint_name)
                raise web.HTTPBadRequest
        except Exception:
            ErrorClass.error_code=400
            ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(genomicVariant.endpoint_name)
            raise web.HTTPBadRequest
        collection=genomicVariant.endpoint_name
        mongo_collection=genomicVariations
        schema=DefaultSchemas.GENOMICVARIATIONS
        idq="caseLevelData.biosampleId"
    elif RequestAttributes.entry_type==analysis.endpoint_name:
        try:
            if analysis.allow_queries_without_filters == False and qparams.query.filters == [] and qparams.query.requestParameters == []:
                ErrorClass.error_code=400
                ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(analysis.endpoint_name)
                raise web.HTTPBadRequest
        except Exception:
            ErrorClass.error_code=400
            ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(analysis.endpoint_name)
            raise web.HTTPBadRequest
        collection=analysis.endpoint_name
        mongo_collection=analyses
        schema=DefaultSchemas.ANALYSES
        idq="biosampleId"
    elif RequestAttributes.entry_type==biosample.endpoint_name:
        try:
            if biosample.allow_queries_without_filters == False and qparams.query.filters == [] and qparams.query.requestParameters == []:
                ErrorClass.error_code=400
                ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(biosample.endpoint_name)
                raise web.HTTPBadRequest
        except Exception:
            ErrorClass.error_code=400
            ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(biosample.endpoint_name)
            raise web.HTTPBadRequest
        collection=biosample.endpoint_name
        mongo_collection=biosamples
        schema=DefaultSchemas.BIOSAMPLES
        idq="id"
    elif RequestAttributes.entry_type==individual.endpoint_name:
        try:
            if individual.allow_queries_without_filters == False and qparams.query.filters == [] and qparams.query.requestParameters == []:
                ErrorClass.error_code=400
                ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(individual.endpoint_name)
                raise web.HTTPBadRequest
        except Exception:
            ErrorClass.error_code=400
            ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(individual.endpoint_name)
            raise web.HTTPBadRequest
        collection=individual.endpoint_name
        mongo_collection=individuals
        schema=DefaultSchemas.INDIVIDUALS
        idq="id"
    elif RequestAttributes.entry_type==run.endpoint_name:
        try:
            if run.allow_queries_without_filters == False and qparams.query.filters == [] and qparams.query.requestParameters == []:
                ErrorClass.error_code=400
                ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(run.endpoint_name)
                raise web.HTTPBadRequest
        except Exception:
            ErrorClass.error_code=400
            ErrorClass.error_message="{} endpoint doesn't allow query without filters".format(run.endpoint_name)
            raise web.HTTPBadRequest
        collection=run.endpoint_name
        mongo_collection=runs
        schema=DefaultSchemas.RUNS
        idq="biosampleId"
    if RequestAttributes.pre_entry_type == None:
        if RequestAttributes.entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
    else:
        if RequestAttributes.pre_entry_type == dtaset.endpoint_name and RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_dataset
        elif RequestAttributes.pre_entry_type == dtaset.endpoint_name:
            function = get_resultSet_of_dataset
        elif RequestAttributes.pre_entry_type == cohort.endpoint_name and RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_cohort
        elif RequestAttributes.pre_entry_type == cohort.endpoint_name:
            function = get_resultSet_of_cohort
        elif RequestAttributes.pre_entry_type == genomicVariant.endpoint_name:
            function = get_resultSet_of_variants
        elif RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_resultSet
        elif RequestAttributes.entry_type == analysis.endpoint_name:
            function = get_analyses_of_resultSet
        elif RequestAttributes.entry_type == biosample.endpoint_name:
            function = get_biosamples_of_resultSet
        elif RequestAttributes.entry_type == run.endpoint_name:
            function = get_runs_of_resultSet
        elif RequestAttributes.entry_type == individual.endpoint_name:
            function = get_individuals_of_resultSet

    loop = asyncio.get_running_loop()

    if datasets != []:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, qparams, dataset.dataset, collection, mongo_collection, schema, idq) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
            if include == 'ALL':
                if dataset_count != -1:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] # pragma: no cover
            elif include == 'MISS':
                if dataset_count == 0:# pragma: no cover
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] # pragma: no cover
            else:
                if dataset_count != -1 and dataset_count != 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] # pragma: no cover
        count=new_count

    return datasets_docs, datasets_count, count, entity_schema, include, datasets

@log_with_args(level)
async def execute_collection_function(self, qparams: RequestParams):
    if RequestAttributes.entry_id == None:
        if RequestAttributes.entry_type == dtaset.endpoint_name:
            function=get_full_datasets
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            function=get_cohorts
    else:
        if RequestAttributes.entry_type == dtaset.endpoint_name:
            function=get_dataset_with_id
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            function=get_cohort_with_id
    response_converted, count, entity_schema = function(self, qparams)
    return response_converted, count, entity_schema