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

@log_with_args(level)
async def execute_function(self, entry_type: str, datasets: list, qparams: RequestParams, entry_id: Optional[str]):
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    datasets_docs={}
    datasets_count={}
    new_count=0
    if entry_type == genomicVariant.endpoint_name:
        if entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
        collection=genomicVariant.endpoint_name
        mongo_collection=genomicVariations
        schema=DefaultSchemas.GENOMICVARIATIONS
        idq="caseLevelData.biosampleId"
    elif entry_type == individual.endpoint_name:
        if entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
        collection=individual.endpoint_name
        mongo_collection=individuals
        schema=DefaultSchemas.INDIVIDUALS
        idq="id"
    elif entry_type == analysis.endpoint_name:
        if entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
        collection=analysis.endpoint_name
        mongo_collection=analyses
        schema=DefaultSchemas.ANALYSES
        idq="biosampleId"
    elif entry_type == biosample.endpoint_name:
        if entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
        collection=biosample.endpoint_name
        mongo_collection=biosamples
        schema=DefaultSchemas.BIOSAMPLES
        idq="id"
    elif entry_type == run.endpoint_name:
        if entry_id == None:
            function=get_resultSet
        else:
            function=get_resultSet_with_id
        collection=run.endpoint_name
        mongo_collection=runs
        schema=DefaultSchemas.RUNS
        idq="biosampleId"
    else:
        entry_type_splitted = entry_type.split('.')
        entry_type = entry_type_splitted[1]
        pre_entry_type = entry_type_splitted[0]
        if pre_entry_type == dtaset.endpoint_name and entry_type == analysis.endpoint_name:
            function = get_resultSet_of_dataset
            collection=analysis.endpoint_name
            mongo_collection=analyses
            schema=DefaultSchemas.ANALYSES
            idq="biosampleId"
        elif pre_entry_type == dtaset.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_resultSet_of_dataset
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="id"
        elif pre_entry_type == dtaset.endpoint_name and entry_type == individual.endpoint_name:
            function = get_resultSet_of_dataset
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="id"
        elif pre_entry_type == dtaset.endpoint_name and entry_type == run.endpoint_name:
            function = get_resultSet_of_dataset
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="biosampleId"
        elif pre_entry_type == dtaset.endpoint_name and entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_dataset
            collection=genomicVariant.endpoint_name
            mongo_collection=genomicVariations
            schema=DefaultSchemas.GENOMICVARIATIONS
            idq="caseLevelData.biosampleId"
        elif pre_entry_type == cohort.endpoint_name and entry_type == analysis.endpoint_name:
            function = get_resultSet_of_cohort
            collection=analysis.endpoint_name
            mongo_collection=analyses
            schema=DefaultSchemas.ANALYSES
            idq="biosampleId"
        elif pre_entry_type == cohort.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_resultSet_of_cohort
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="id"
        elif pre_entry_type == cohort.endpoint_name and entry_type == individual.endpoint_name:
            function = get_resultSet_of_cohort
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="id"
        elif pre_entry_type == cohort.endpoint_name and entry_type == run.endpoint_name:
            function = get_resultSet_of_cohort
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="biosampleId"
        elif pre_entry_type == cohort.endpoint_name and entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_cohort
            collection=genomicVariant.endpoint_name
            mongo_collection=genomicVariations
            schema=DefaultSchemas.GENOMICVARIATIONS
            idq="caseLevelData.biosampleId"
        elif pre_entry_type == genomicVariant.endpoint_name and entry_type == individual.endpoint_name:
            function = get_resultSet_of_variants
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="id"
        elif pre_entry_type == genomicVariant.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_resultSet_of_variants
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="id"
        elif pre_entry_type == genomicVariant.endpoint_name and entry_type == analysis.endpoint_name:
            function = get_resultSet_of_variants
            collection=analysis.endpoint_name
            mongo_collection=analyses
            schema=DefaultSchemas.ANALYSES
            idq="biosampleId"
        elif pre_entry_type == genomicVariant.endpoint_name and entry_type == run.endpoint_name:
            function = get_resultSet_of_variants
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="biosampleId"
        elif entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_resultSet
            collection=genomicVariant.endpoint_name
            mongo_collection=genomicVariations
            schema=DefaultSchemas.GENOMICVARIATIONS
            idq="caseLevelData.biosampleId"
        elif entry_type == analysis.endpoint_name:
            function = get_analyses_of_resultSet
            collection=analysis.endpoint_name
            mongo_collection=analyses
            schema=DefaultSchemas.ANALYSES
            idq="biosampleId"
        elif pre_entry_type == individual.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_biosamples_of_resultSet
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="individualId"
        elif pre_entry_type == analysis.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_biosamples_of_resultSet
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="analysisId"
        elif pre_entry_type == run.endpoint_name and entry_type == biosample.endpoint_name:
            function = get_biosamples_of_resultSet
            collection=biosample.endpoint_name
            mongo_collection=biosamples
            schema=DefaultSchemas.BIOSAMPLES
            idq="runId"
        elif pre_entry_type == individual.endpoint_name and entry_type == run.endpoint_name:
            function = get_runs_of_resultSet
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="individualId"
        elif pre_entry_type == biosample.endpoint_name and entry_type == run.endpoint_name:
            function = get_runs_of_resultSet
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="biosampleId"
        elif pre_entry_type == analysis.endpoint_name and entry_type == run.endpoint_name:
            function = get_runs_of_resultSet
            collection=run.endpoint_name
            mongo_collection=runs
            schema=DefaultSchemas.RUNS
            idq="analysisId"
        elif pre_entry_type == analysis.endpoint_name and entry_type == individual.endpoint_name:
            function = get_individuals_of_resultSet
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="analysisId"
        elif pre_entry_type == run.endpoint_name and entry_type == individual.endpoint_name:
            function = get_individuals_of_resultSet
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="runId"
        elif pre_entry_type == biosample.endpoint_name and entry_type == individual.endpoint_name:
            function = get_individuals_of_resultSet
            collection=individual.endpoint_name
            mongo_collection=individuals
            schema=DefaultSchemas.INDIVIDUALS
            idq="biosampleId"

    loop = asyncio.get_running_loop()

    if datasets != [] and include != 'NONE':
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, qparams, dataset, collection, mongo_collection, schema, idq, entry_type) for dataset in datasets],
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
                    datasets.remove(dataset)# pragma: no cover
            elif include == 'HIT':
                if dataset_count != -1 and dataset_count != 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets.remove(dataset) 
            else:
                if dataset_count == 0:# pragma: no cover
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets.remove(dataset)
        count=new_count
    
    else:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, qparams, dataset, collection, mongo_collection, schema, idq, entry_type) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
        datasets_docs["NONE"]=records
        if limit == 0 or new_count < limit:
            pass
        else:
            count = limit# pragma: no cover
        datasets_count["NONE"]=count
    return datasets_docs, datasets_count, count, entity_schema, include, datasets

@log_with_args(level)
async def execute_collection_function(self, entry_type: str, qparams: RequestParams, entry_id: Optional[str]):
    if entry_id == None:
        if entry_type == dtaset.endpoint_name:
            function=get_full_datasets
        elif entry_type == cohort.endpoint_name:
            function=get_cohorts
    else:
        if entry_type == dtaset.endpoint_name:
            function=get_dataset_with_id
        elif entry_type == cohort.endpoint_name:
            function=get_cohort_with_id
    response_converted, count, entity_schema = function(self, entry_id, qparams)
    return response_converted, count, entity_schema