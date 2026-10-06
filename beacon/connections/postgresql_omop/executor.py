
from beacon.response.classes import SingleDatasetResponse, MultipleDatasetsResponse, CollectionsResponse
from beacon.request.classes import RequestAttributes

import beacon.models.omop.connections.postgresql.individuals as individuals
import beacon.models.omop.connections.postgresql.biosamples as biosamples
import beacon.models.omop.connections.postgresql.cohorts as cohorts

async def execute_function(self, datasets):
    if (RequestAttributes.pre_entry_type == "individuals"
        and RequestAttributes.entry_type == "biosamples"):
        schema, count, docs = await individuals.get_biosamples_of_individual(
            RequestAttributes.entry_id,
            RequestAttributes.qparams,
        )
    elif (RequestAttributes.pre_entry_type == "biosamples"
            and RequestAttributes.entry_type == "individuals"):
            schema, count, docs = await biosamples.get_individuals_of_biosample(
                RequestAttributes.entry_id,
                RequestAttributes.qparams,
            )
    elif RequestAttributes.entry_type == "individuals":
        schema, count, docs = await individuals.get_the_individuals(
            RequestAttributes.entry_id,
            RequestAttributes.qparams,
        )
    elif RequestAttributes.entry_type == "biosamples":
        schema, count, docs = await biosamples.get_biosamples(
            RequestAttributes.entry_id,
            RequestAttributes.qparams,
        )
    return MultipleDatasetsResponse(
        datasets_responses=[
            SingleDatasetResponse(
                dataset="postgresql_omop",
                exists=count > 0,
                dataset_count=count,
                docs=docs,
                granularity="record",
            )
        ],
        total_count=count,
    )

async def execute_collection_function(endpoint_view):
    if RequestAttributes.entry_type == "cohorts":
        if RequestAttributes.entry_id:
            schema, count, docs = await cohorts.get_cohort_with_id(
                RequestAttributes.entry_id,
                RequestAttributes.qparams,
            )
        else:
            schema, count, docs = await cohorts.get_cohorts(
                RequestAttributes.entry_id,
                RequestAttributes.qparams,
            )

    return CollectionsResponse(
        docs=docs,
        count=count,           
    )