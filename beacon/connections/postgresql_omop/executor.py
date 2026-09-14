
from beacon.response.classes import SingleDatasetResponse, MultipleDatasetsResponse
from beacon.request.classes import RequestAttributes
import beacon.models.omop.connections.postgresql.individuals as individuals
import beacon.models.omop.connections.postgresql.biosamples as biosamples

async def execute_function(self, datasets):
    if RequestAttributes.entry_type == "individuals":
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