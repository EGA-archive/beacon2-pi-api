from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.connections.omopcdm.biosamples import get_biosamples
from beacon.connections.omopcdm.individuals import get_individuals


# There are no different datasets in OMOPCDM
@log_with_args(level)
def get_full_datasets(self, entry_id: Optional[str], qparams: RequestParams):
    schema = DefaultSchemas.DATASETS
    response = [{'id':'cdm', 'name':'OMOP CDM dataset'}]
    count = 1
    return response, count, schema

@log_with_args(level)
def get_list_of_datasets(self):
    datasets, count, schema = get_full_datasets(self, None, None)
    return datasets

@log_with_args(level)
def get_dataset_with_id(self, entry_id: Optional[str], qparams: RequestParams):
    schema = DefaultSchemas.DATASETS
    if entry_id=='cdm':
        response = [{'id':'cdm', 'name':'OMOP CDM dataset'}]
        count = 1
        return response, count, schema
    return {}, 0, schema

@log_with_args(level)
def get_biosamples_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.BIOSAMPLES
    if entry_id=='cdm':
        return get_biosamples(self, None, qparams, dataset)
    return schema, 0, 0, {}, dataset

@log_with_args(level)
def get_individuals_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.INDIVIDUALS
    if entry_id=='cdm':
        return get_individuals(self, None, qparams, dataset)
    return schema, 0, 0, {}, dataset