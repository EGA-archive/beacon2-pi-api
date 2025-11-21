from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.non_collections import get_phenotypic_cross_query, get_phenotypic_endpoint, get_phenotypic_endpoint_with_id, get_phenotypic_endpoint_of_cohort, get_phenotypic_endpoint_of_dataset, get_phenotypic_endpoint_of_variants, get_variants_of_cohort, get_variants_of_dataset, get_variants_of_phenotypic_endpoint
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.collections import get_full_datasets, get_dataset_with_id, get_cohorts, get_cohort_with_id, get_cross_collections
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.conf import genomicVariant, analysis, run, biosample, individual, dataset, cohort
from beacon.conf.conf import level

@log_with_args_mongo(level)
def get_function(self):
    if RequestAttributes.pre_entry_type == None:
        if RequestAttributes.entry_id == None:
            function=get_phenotypic_endpoint
        else:
            function=get_phenotypic_endpoint_with_id
    else:
        if RequestAttributes.pre_entry_type == dataset.endpoint_name and RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_dataset
        elif RequestAttributes.pre_entry_type == dataset.endpoint_name:
            function = get_phenotypic_endpoint_of_dataset
        elif RequestAttributes.pre_entry_type == cohort.endpoint_name and RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_cohort
        elif RequestAttributes.pre_entry_type == cohort.endpoint_name:
            function = get_phenotypic_endpoint_of_cohort
        elif RequestAttributes.pre_entry_type == genomicVariant.endpoint_name:
            function = get_phenotypic_endpoint_of_variants
        elif RequestAttributes.entry_type == genomicVariant.endpoint_name:
            function = get_variants_of_phenotypic_endpoint
        else:
            function = get_phenotypic_cross_query
    return function

@log_with_args_mongo(level)
def get_collections_function(self):
    if RequestAttributes.entry_id == None:
        if RequestAttributes.entry_type == dataset.endpoint_name:
            function=get_full_datasets
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            function=get_cohorts
    elif RequestAttributes.pre_entry_type != None:
        function=get_cross_collections
    else:
        if RequestAttributes.entry_type == dataset.endpoint_name:
            function=get_dataset_with_id
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            function=get_cohort_with_id
    return function