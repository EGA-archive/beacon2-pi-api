
from beacon.response.classes import SingleDatasetResponse, MultipleDatasetsResponse, CollectionsResponse

import beacon.models.omop.connections.postgresql.individuals as individuals
import beacon.models.omop.connections.postgresql.biosamples as biosamples
import beacon.models.omop.connections.postgresql.cohorts as cohorts

async def execute_function(self, datasets):
    if (self.request_attributes.pre_entry_type == "individuals"
        and self.request_attributes.entry_type == "biosamples"):
        schema, count, docs = await individuals.get_biosamples_of_individual(
            self.request_attributes.entry_id,
            self.request_attributes.qparams,
        )
    elif (self.request_attributes.pre_entry_type == "biosamples"
            and self.request_attributes.entry_type == "individuals"):
            schema, count, docs = await biosamples.get_individuals_of_biosample(
                self.request_attributes.entry_id,
                self.request_attributes.qparams,
            )
    elif self.request_attributes.entry_type == "individuals":
        schema, count, docs = await individuals.get_the_individuals(
            self.request_attributes.entry_id,
            self.request_attributes.qparams,
        )
    elif self.request_attributes.entry_type == "biosamples":
        schema, count, docs = await biosamples.get_biosamples(
            self.request_attributes.entry_id,
            self.request_attributes.qparams,
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
    request_attributes = endpoint_view.request_attributes
    if request_attributes.entry_type == "cohorts":
        if request_attributes.entry_id:
            schema, count, docs = await cohorts.get_cohort_with_id(
                request_attributes.entry_id,
                request_attributes.qparams,
            )
        else:
            schema, count, docs = await cohorts.get_cohorts(
                request_attributes.entry_id,
                request_attributes.qparams,
            )

    return CollectionsResponse(
        docs=docs,
        count=count,           
    )