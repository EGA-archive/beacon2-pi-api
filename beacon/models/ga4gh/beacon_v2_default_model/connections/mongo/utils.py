from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import genomicVariations, biosamples, runs, cohorts, analyses, datasets, individuals
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level
from beacon.exceptions.exceptions import InvalidRequest
import aiohttp.web as web
from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant, analysis, run, biosample, individual, dataset, cohort
from beacon.request.classes import RequestAttributes
from beacon.response.classes import SingleDatasetResponse

@log_with_args_mongo(level)
def lengthquery(self, collection: Collection,query: dict):
    # Return the length of al the records for the query
    return collection.find(query, {"_id": 1, "variation.location.interval.start.value": 1, "variation.location.interval.end.value": 1}).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def get_phenotypic_cross_query_attributes(self, entry_type, pre_entry_type):
    # For cross queries, save the attributes for the translation (linkage) between endpoints (idq to idq2) and the name of the collection for the initial endpoint queried (secondary_collection)
    mapping = {individual.endpoint_name: {analysis.endpoint_name: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": analyses},
                                        biosample.endpoint_name: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": biosamples},
                                        run.endpoint_name: {"idq": "id",
                                                        "idq2": "individualId",
                                                        "secondary_collection": runs}},
    biosample.endpoint_name: {analysis.endpoint_name: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                            individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals},
                            run.endpoint_name: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs}},
    analysis.endpoint_name: {run.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs},
                            biosample.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                            individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},
    run.endpoint_name: {biosample.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                        individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},                                                                                                                                                                                                                                                                                                                                                                                                                                  
    cohort.endpoint_name: {biosample.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        dataset.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "id",
                                                    "secondary_collection": datasets},
                        genomicVariant.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}},
    dataset.endpoint_name: {biosample.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        cohort.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": cohorts},
                        genomicVariant.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}}}
    return mapping[entry_type][pre_entry_type]