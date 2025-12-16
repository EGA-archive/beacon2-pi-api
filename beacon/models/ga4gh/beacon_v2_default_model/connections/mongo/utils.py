from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import genomicVariations, biosamples, runs, cohorts, analyses, datasets, individuals
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import InvalidRequest
import aiohttp.web as web
import yaml

def import_genomicVariant_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/genomicVariant.yml", 'r') as pfile:
        genomicVariant_confile= yaml.safe_load(pfile)
    pfile.close()
    return genomicVariant_confile

def import_dataset_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml", 'r') as pfile:
        dataset_confile= yaml.safe_load(pfile)
    pfile.close()
    return dataset_confile

def import_analysis_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'r') as pfile:
        analysis_confile= yaml.safe_load(pfile)
    pfile.close()
    return analysis_confile

def import_biosample_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml", 'r') as pfile:
        biosample_confile= yaml.safe_load(pfile)
    pfile.close()
    return biosample_confile

def import_cohort_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml", 'r') as pfile:
        cohort_confile= yaml.safe_load(pfile)
    pfile.close()
    return cohort_confile

def import_individual_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/individual.yml", 'r') as pfile:
        individual_confile= yaml.safe_load(pfile)
    pfile.close()
    return individual_confile

def import_run_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'r') as pfile:
        run_confile= yaml.safe_load(pfile)
    pfile.close()
    return run_confile

@log_with_args_mongo(config.level)
def lengthquery(self, collection: Collection,query: dict):
    # Return the length of al the records for the query
    return collection.find(query, {"_id": 1, "variation.location.interval.start.value": 1, "variation.location.interval.end.value": 1}).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def get_phenotypic_cross_query_attributes(self, entry_type, pre_entry_type):
    individual_confile = import_individual_confile()
    analysis_confile = import_analysis_confile()
    biosample_confile = import_biosample_confile()
    cohort_confile = import_cohort_confile()
    dataset_confile = import_dataset_confile()
    genomicVariant_confile = import_genomicVariant_confile()
    run_confile = import_run_confile()
    # For cross queries, save the attributes for the translation (linkage) between endpoints (idq to idq2) and the name of the collection for the initial endpoint queried (secondary_collection)
    mapping = {individual_confile["individual"]["endpoint_name"]: {analysis_confile["analysis"]["endpoint_name"]: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": analyses},
                                        biosample_confile["biosample"]["endpoint_name"]: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": biosamples},
                                        run_confile["run"]["endpoint_name"]: {"idq": "id",
                                                        "idq2": "individualId",
                                                        "secondary_collection": runs}},
    biosample_confile["biosample"]["endpoint_name"]: {analysis_confile["analysis"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                            individual_confile["individual"]["endpoint_name"]: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals},
                            run_confile["run"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs}},
    analysis_confile["analysis"]["endpoint_name"]: {run_confile["run"]["endpoint_name"]: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs},
                            biosample_confile["biosample"]["endpoint_name"]: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                            individual_confile["individual"]["endpoint_name"]: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},
    run_confile["run"]["endpoint_name"]: {biosample_confile["biosample"]["endpoint_name"]: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                        analysis_confile["analysis"]["endpoint_name"]: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                        individual_confile["individual"]["endpoint_name"]: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},                                                                                                                                                                                                                                                                                                                                                                                                                                  
    cohort_confile["cohort"]["endpoint_name"]: {biosample_confile["biosample"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis_confile["analysis"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        dataset_confile["dataset"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "id",
                                                    "secondary_collection": datasets},
                        genomicVariant_confile["genomicVariant"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual_confile["individual"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run_confile["run"]["endpoint_name"]: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}},
    dataset_confile["dataset"]["endpoint_name"]: {biosample_confile["biosample"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis_confile["analysis"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        cohort_confile["cohort"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": cohorts},
                        genomicVariant_confile["genomicVariant"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual_confile["individual"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run_confile["run"]["endpoint_name"]: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}}}
    return mapping[entry_type][pre_entry_type]