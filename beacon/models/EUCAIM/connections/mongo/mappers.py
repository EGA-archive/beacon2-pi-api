from beacon.models.EUCAIM.connections.mongo.non_collections import get_endpoint, get_endpoint_with_id, get_endpoint_cross_query
from beacon.models.EUCAIM.connections.mongo.collections import get_full_datasets, get_dataset_with_id
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant, analysis, run, biosample, individual, dataset, cohort
from beacon.conf.conf import level

@log_with_args_mongo(level)
def choose_function(self):
    if RequestAttributes.pre_entry_type == None:
        if RequestAttributes.entry_id == None:
            function=get_endpoint
        else:
            function=get_endpoint_with_id
    else:
        function=get_endpoint_cross_query
    return function

@log_with_args_mongo(level)
def choose_collections_function(self):
    if RequestAttributes.entry_id == None:
         function=get_full_datasets
    else:
        if RequestAttributes.entry_type == dataset.endpoint_name:
            function=get_dataset_with_id
    return function