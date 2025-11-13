from typing import Optional
from pydantic import (
    BaseModel,
    model_validator,
    Field
)
from beacon.conf import conf
from beacon.validator.v2_1_2.framework.meta import InformationalMeta
from beacon.models.ga4gh.beacon_v2_default_model.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run

class RelatedEndpoint(BaseModel):
    returnedEntryType: str
    url: str

class RelatedEndpointEntries(BaseModel):
    analysis: Optional[RelatedEndpoint] = None
    biosample: Optional[RelatedEndpoint] = None
    cohort: Optional[RelatedEndpoint] = None
    dataset: Optional[RelatedEndpoint] = None
    genomicVariant: Optional[RelatedEndpoint] = None
    individual: Optional[RelatedEndpoint] = None
    run: Optional[RelatedEndpoint] = None
    @model_validator(mode='after')
    def check_not_all_related_endpoints_are_none(self):
        if self.analysis == None and self.biosample == None and self.cohort == None and self.dataset == None and self.genomicVariant == None and self.individual == None and self.run == None:
            raise ValueError('Minimum 1 entry is required for endpoints')
        return self

class Endpoint(BaseModel):
    endpoints: RelatedEndpointEntries
    entryType: str
    openAPIEndpointsDefinition: Optional[str] = None
    entryType=analysis.id,
    rootUrl: str
    singleEntryUrl: Optional[str] = None

class EndpointEntries(BaseModel):
    analysis: Optional[Endpoint] = None
    biosample: Optional[Endpoint] = None
    cohort: Optional[Endpoint] = None
    dataset: Optional[Endpoint] = None
    genomicVariant: Optional[Endpoint] = None
    individual: Optional[Endpoint] = None
    run: Optional[Endpoint] = None
    @model_validator(mode='after')
    def check_not_all_endpoint_entries_are_none(self):
        if self.analysis == None and self.biosample == None and self.cohort == None and self.dataset == None and self.genomicVariant == None and self.individual == None and self.run == None:
            raise ValueError('Minimum 1 entry is required for endpointSets')
        return self

class MapSchema(BaseModel):
    schema: str = Field(alias="$schema", default="https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconConfigurationSchema.json")
    endpointSets: EndpointEntries
    def populate_endpoints(self):
        return self(endpointSets=EndpointEntries(analysis=Endpoint(id=analysis.id,openAPIEndpointsDefinition=analysis.open_api_endpoints_definition,
                                                            entryType=analysis.id,
                                                            rootUrl=conf.complete_url+'/'+analysis.endpoint_name, singleEntryUrl=conf.complete_url+'/'+analysis.endpoint_name+'/{id}' if analysis.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name) if analysis.biosample_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name) if analysis.cohort_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name) if analysis.dataset_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if analysis.genomicVariant_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name) if analysis.individual_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name) if analysis.run_lookup == True else None)) if analysis.enable_endpoint == True else None,
                                        biosample=Endpoint(id=biosample.id,openAPIEndpointsDefinition=biosample.open_api_endpoints_definition,
                                                            entryType=biosample.id,
                                                            rootUrl=conf.complete_url+'/'+biosample.endpoint_name, singleEntryUrl=conf.complete_url+'/'+biosample.endpoint_name+'/{id}' if biosample.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name) if biosample.analysis_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name) if biosample.cohort_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name) if biosample.dataset_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if biosample.genomicVariant_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name) if biosample.individual_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name) if biosample.run_lookup == True else None)) if biosample.enable_endpoint == True else None,
                                        cohort=Endpoint(id=cohort.id,openAPIEndpointsDefinition=cohort.open_api_endpoints_definition,
                                                            entryType=cohort.id,
                                                            rootUrl=conf.complete_url+'/'+cohort.endpoint_name, singleEntryUrl=conf.complete_url+'/'+cohort.endpoint_name+'/{id}' if cohort.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name) if cohort.analysis_lookup == True else None,
                                                                                             biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name) if cohort.biosample_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name) if cohort.dataset_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if cohort.genomicVariant_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name) if cohort.individual_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name) if cohort.run_lookup == True else None)) if cohort.enable_endpoint == True else None,
                                        dataset=Endpoint(id=dataset.id,openAPIEndpointsDefinition=dataset.open_api_endpoints_definition,
                                                            entryType=dataset.id,
                                                            rootUrl=conf.complete_url+'/'+dataset.endpoint_name, singleEntryUrl=conf.complete_url+'/'+dataset.endpoint_name+'/{id}' if dataset.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name) if dataset.analysis_lookup == True else None,
                                                                                             biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name) if dataset.biosample_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name) if dataset.cohort_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if dataset.genomicVariant_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name) if dataset.individual_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name) if dataset.run_lookup == True else None)) if dataset.enable_endpoint == True else None,
                                        genomicVariant=Endpoint(id=genomicVariant.id,openAPIEndpointsDefinition=genomicVariant.open_api_endpoints_definition,
                                                            entryType=genomicVariant.id,
                                                            rootUrl=conf.complete_url+'/'+genomicVariant.endpoint_name, singleEntryUrl=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}' if genomicVariant.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name) if genomicVariant.analysis_lookup == True else None,
                                                                                             biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name) if genomicVariant.biosample_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name) if genomicVariant.cohort_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name) if genomicVariant.dataset_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name) if genomicVariant.individual_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name) if genomicVariant.run_lookup == True else None)) if genomicVariant.enable_endpoint == True else None,
                                        individual=Endpoint(id=individual.id,openAPIEndpointsDefinition=individual.open_api_endpoints_definition,
                                                            entryType=individual.id,
                                                            rootUrl=conf.complete_url+'/'+individual.endpoint_name, singleEntryUrl=conf.complete_url+'/'+individual.endpoint_name+'/{id}' if individual.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name) if individual.analysis_lookup == True else None,
                                                                                             biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name) if individual.biosample_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name) if individual.cohort_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name) if individual.dataset_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if individual.genomicVariant_lookup == True else None,
                                                                                             run=RelatedEndpoint(returnedEntryType=run.id,url=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name) if individual.run_lookup == True else None)) if individual.enable_endpoint == True else None,
                                        run=Endpoint(id=run.id,openAPIEndpointsDefinition=run.open_api_endpoints_definition,
                                                            entryType=run.id,
                                                            rootUrl=conf.complete_url+'/'+run.endpoint_name, singleEntryUrl=conf.complete_url+'/'+run.endpoint_name+'/{id}' if run.singleEntryUrl==True else None,
                                                            endpoints=RelatedEndpointEntries(analysis=RelatedEndpoint(returnedEntryType=analysis.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name) if run.analysis_lookup == True else None,
                                                                                             biosample=RelatedEndpoint(returnedEntryType=biosample.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name) if run.biosample_lookup == True else None,
                                                                                             cohort=RelatedEndpoint(returnedEntryType=cohort.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name) if run.cohort_lookup == True else None,
                                                                                             dataset=RelatedEndpoint(returnedEntryType=dataset.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name) if run.dataset_lookup == True else None,
                                                                                             genomicVariant=RelatedEndpoint(returnedEntryType=genomicVariant.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name) if run.genomicVariant_lookup == True else None,
                                                                                             individual=RelatedEndpoint(returnedEntryType=individual.id,url=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name) if run.individual_lookup == True else None))if run.enable_endpoint == True else None))

class MapResponse(BaseModel):
    meta: InformationalMeta
    response: MapSchema