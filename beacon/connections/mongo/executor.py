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
from beacon.request.classes import RequestAttributes
import aiohttp.web as web

@log_with_args(level)
async def execute_function(self, datasets: list):
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    datasets_docs={}
    datasets_count={}
    new_count=0
    if RequestAttributes.entry_type==genomicVariant.endpoint_name:
        collection=genomicVariant.endpoint_name
        mongo_collection=genomicVariations
        idq="caseLevelData.biosampleId"
    elif RequestAttributes.entry_type==analysis.endpoint_name:
        collection=analysis.endpoint_name
        mongo_collection=analyses
        idq="biosampleId"
    elif RequestAttributes.entry_type==biosample.endpoint_name:
        collection=biosample.endpoint_name
        mongo_collection=biosamples
        idq="id"
    elif RequestAttributes.entry_type==individual.endpoint_name:
        collection=individual.endpoint_name
        mongo_collection=individuals
        idq="id"
    elif RequestAttributes.entry_type==run.endpoint_name:
        collection=run.endpoint_name
        mongo_collection=runs
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
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, dataset.dataset, collection, mongo_collection, idq) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            count, dataset_count, records, dataset = task.result()
            if include == 'ALL':
                if dataset_count != -1:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
            elif include == 'MISS':
                if dataset_count == 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
            else:
                if dataset_count != -1 and dataset_count != 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
        count=new_count
    try:
        return datasets_docs, datasets_count, count, include, datasets
    except Exception:
        self._error.handle_exception(web.HTTPBadRequest, "No datasets found. Check out the permissions or the datsets requested if a response was expected.")
        raise

@log_with_args(level)
async def execute_collection_function(self):
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
    response_converted, count = function(self)
    return response_converted, count

# 1. Mirar si la configuració coincideix amb la request arribada. Si no, retornar un 400 Bad Request.
# 2. Mirar si s'ha trobat algun match de dataset amb permissions, si el dataset trobat no té permissions, retornar un 401 Unauthorized.
# 3. Resta d'errors llençar cap amunt.
