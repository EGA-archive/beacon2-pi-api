from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    Field,
    ConfigDict
)
from beacon.validator.model.genomicVariations import OntologyTerm, GenomicVariations
from beacon.validator.model.analyses import Analyses
from beacon.validator.model.biosamples import Biosamples
from beacon.validator.model.cohorts import Cohorts
from beacon.validator.model.datasets import Datasets
from beacon.validator.model.individuals import Individuals
from beacon.validator.model.runs import Runs
from beacon.request.parameters import SchemasPerEntity, Pagination, SequenceQuery,RangeQuery,BracketQuery,AminoacidChangeQuery,GeneIdQuery,GenomicAlleleQuery,DatasetsRequested
from typing import List, Optional, Union, Dict
from beacon.logs.logs import LOG
from beacon.conf import conf, analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.request.classes import RequestAttributes
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.filtering_terms.resources import resources

class ReceivedRequestSummary(BaseModel):
    apiVersion: str
    requestedSchemas: List[SchemasPerEntity]
    pagination: Pagination
    requestedGranularity: str
    testMode: Optional[bool] = None
    filters: Optional[List[str]] = None
    requestParameters: Optional[Dict] = None
    includeResultsetResponses: Optional[str] = None

class Meta(BaseModel):
    apiVersion: str=conf.api_version
    beaconId: str=conf.beacon_id
    receivedRequestSummary: ReceivedRequestSummary
    returnedGranularity: str
    returnedSchemas: List[SchemasPerEntity]
    testMode: Optional[bool] = None

class InformationalMeta(BaseModel):
    apiVersion: str=conf.api_version
    beaconId: str=conf.beacon_id
    returnedSchemas: List[SchemasPerEntity]

class BeaconOrganization(BaseModel):
    address: Optional[str]=conf.org_adress if conf.org_adress != "" else None
    contactUrl: Optional[str]=conf.org_contact_url if conf.org_contact_url != "" else None
    description: Optional[str]=conf.org_description if conf.org_description != "" else None
    id: str=conf.org_id
    info: Optional[str]=conf.org_info if conf.org_info != "" else None
    logoUrl: Optional[str]=conf.org_logo_url if conf.org_logo_url != "" else None
    name: str=conf.org_name
    welcomeUrl: Optional[str]=conf.org_welcome_url if conf.welcome_url != "" else None

class Info(BaseModel):
    alternativeUrl: Optional[str]=conf.alternative_url if conf.alternative_url != "" else None
    createDateTime: Optional[str]=conf.create_datetime if conf.create_datetime != "" else None
    description: Optional[str]=conf.description if conf.description != "" else None
    info: Optional[Dict]=None
    updateDateTime: Optional[str]=conf.update_datetime if conf.update_datetime != "" else None
    version: Optional[str]=conf.version if conf.version != "" else None
    welcomeUrl: Optional[str]=conf.welcome_url if conf.welcome_url != "" else None
    id: str = conf.beacon_id
    name: str = conf.beacon_name
    apiVersion: str = conf.api_version
    environment: str = conf.environment
    organization: BeaconOrganization = BeaconOrganization().model_dump(exclude_none=True)
    
class InfoResponse(BaseModel):
    meta: InformationalMeta
    response: Info

class Handover(BaseModel):
    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str

class ResultsetInstance(BaseModel):
    countAdjustedTo: Optional[List[Union[str,int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    id: str
    info: Optional[Dict] = None
    results: Optional[List[Union[Analyses,Biosamples,GenomicVariations,Individuals,Runs]]]=None
    resultsCount: Optional[int]=None
    resultsHandovers: Optional[List[Handover]] = None
    setType: str
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded_resultSet(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    
    def build_response_by_dataset(self, dataset, data, dict_counts, allowed_granularity, granularity):
        resultsHandovers=None
        countAdjustedTo=None
        countPrecision=None
        for handover in list_of_handovers_per_dataset:
            if handover["dataset"]==dataset.dataset:
                resultsHandovers=[handover["handover"]]
        if dataset.granularity == 'record' and allowed_granularity=='record' and granularity =='record':                                        
            if conf.imprecise_count !=0:
                if dict_counts[dataset.dataset] < conf.imprecise_count:
                    resultsCount=conf.imprecise_count
                    countAdjustedTo=[conf.imprecise_count]
                    countPrecision='imprecise'
                else:
                    resultsCount=dict_counts[dataset.dataset]
                    
            elif conf.round_to_tens == True:
                resultsCount=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                countAdjustedTo=['immediate ten']
                countPrecision='rounded'

            elif conf.round_to_hundreds == True:
                resultsCount=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                countAdjustedTo=['immediate hundred']
                countPrecision='rounded'
            else:
                resultsCount=dict_counts[dataset.dataset]
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=data[dataset.dataset],
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        elif dataset.granularity != 'boolean' and allowed_granularity != 'boolean' and granularity != 'boolean':
            resultsCount=dict_counts[dataset.dataset]
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=None,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        else:
            resultsCount=None
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=None,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=None,
                        resultsHandovers=resultsHandovers)


class ResponseSummary(BaseModel):
    exists: bool
    numTotalResults: Optional[int] = None
    def build_response_summary_by_dataset(self, datasets, dict_counts):
        count=0
        non_counted=0
        granularity = RequestAttributes.qparams.query.requestedGranularity
        for dataset in datasets:
            if dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':
                if conf.imprecise_count !=0:
                    if dict_counts[dataset.dataset] < conf.imprecise_count:
                        count+=conf.imprecise_count
                elif conf.round_to_tens == True:
                    count+=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                elif conf.round_to_hundreds == True:
                    count+=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                else:
                    count +=dict_counts[dataset.dataset]
            else:
                non_counted+=dict_counts[dataset.dataset]
        if count == 0 and non_counted >0:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=True)
        elif count > 0:
            return self(exists=count > 0,numTotalResults=count)
        else:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=False)

class CountResponseSummary(BaseModel):
    countAdjustedTo: Optional[List[Union[str,int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    numTotalResults: int
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    def build_count_response_summary(self, count):
        countAdjustedTo=None
        countPrecision=None                                    
        if conf.imprecise_count !=0:
            if count < conf.imprecise_count:
                resultsCount=conf.imprecise_count
                countAdjustedTo=[conf.imprecise_count]
                countPrecision='imprecise'
            else:
                resultsCount=count
                
        elif conf.round_to_tens == True:
            resultsCount=math.ceil(count / 10.0) * 10
            countAdjustedTo=['immediate ten']
            countPrecision='rounded'

        elif conf.round_to_hundreds == True:
            resultsCount=math.ceil(count / 100.0) * 100
            countAdjustedTo=['immediate hundred']
            countPrecision='rounded'
        else:
            resultsCount=count
        return self(exists=count>0,
                    numTotalResults=resultsCount,
                    countAdjustedTo=countAdjustedTo,
                    countPrecision=countPrecision)

class BooleanResponseSummary(BaseModel):
    exists: bool
        
class Resultsets(BaseModel):
    resultSets: List[ResultsetInstance]
    
    def return_resultSets(self, resultSets):
        return self(resultSets = resultSets)
        
class ResultsetsResponse(BaseModel):
    meta: Meta
    responseSummary: ResponseSummary
    response: Resultsets
    beaconHandovers: Optional[List[Handover]] = None
    info: Optional[Dict] = None
    
    def return_response(self, meta, resultSets, responseSummary):
        return self(meta = meta, response = resultSets, responseSummary = responseSummary)
    
class CountResponse(BaseModel):
    meta: Meta
    responseSummary: CountResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None

class BooleanResponse(BaseModel):
    meta: Meta
    responseSummary: BooleanResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None

class Collection(BaseModel):
    collections: List[Union[Cohorts,Datasets]]

class CollectionResponse(BaseModel):
    meta: Meta
    responseSummary: ResponseSummary
    response: Collection
    beaconHandovers: Optional[List[Handover]] = None
    info: Optional[Dict] = None

class MaturityAttributes(BaseModel):
    productionStatus: str = conf.environment.upper()

class ReferenceToAnSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    referenceToSchemaDefinition: str
    schemaVersion: Optional[str] = None

class EntryTypes(BaseModel):
    aCollectionOf: Optional[List] = None
    additionallySupportedSchemas: Optional[List[ReferenceToAnSchema]] = None
    defaultSchema: ReferenceToAnSchema
    description: Optional[str] = None
    id: str
    name: str
    nonFilteredQueriesAllowed: Optional[bool] = True
    ontologyTermForThisType: Optional[OntologyTerm] = None
    partOfSpecification: str

class SecurityAttributes(BaseModel):
    defaultGranularity: Optional[str] = conf.default_beacon_granularity
    securityLevels: Optional[List[str]] = conf.security_levels
    @field_validator('defaultGranularity')
    @classmethod
    def defaultGranularity_must_be_boolean_count_record(cls, v: str) -> str:
        if v not in ['boolean', 'count', 'record']:
            raise ValueError('defaultGranularity must be one between boolean, count, record')
        return v

class Entries(BaseModel):
    analysis: Optional[EntryTypes] = None
    biosample: Optional[EntryTypes] = None
    cohort: Optional[EntryTypes] = None
    dataset: Optional[EntryTypes] = None
    genomicVariant: Optional[EntryTypes] = None
    individual: Optional[EntryTypes] = None
    run: Optional[EntryTypes] = None

    @model_validator(mode='after')
    def check_not_all_entries_are_none(self):
        if self.analysis == None and self.biosample == None and self.cohort == None and self.dataset == None and self.genomicVariant == None and self.individual == None and self.run == None:
            raise ValueError('Minimum 1 entry is required for entryTypes')
        return self

class EntryTypesSchema(BaseModel):
    entryTypes: Entries

    def return_schema(self):
        return self(entryTypes=Entries(analysis=EntryTypes(id=analysis.id,name=analysis.name,ontologyTermForThisType=OntologyTerm(id=analysis.ontology_id, label=analysis.ontology_name),partOfSpecification=analysis.specification,
                   description=analysis.description, defaultSchema=ReferenceToAnSchema(id=analysis.defaultSchema_id,name=analysis.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=analysis.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=analysis.defaultSchema_schema_version),
        additionallySupportedSchemas=analysis.aditionally_supported_schemas,nonFilteredQueriesAllowed=analysis.allow_queries_without_filters) if analysis.enable_endpoint == True else None,
        biosample=EntryTypes(id=biosample.id,name=biosample.name,ontologyTermForThisType=OntologyTerm(id=biosample.ontology_id, label=biosample.ontology_name),partOfSpecification=biosample.specification,
                   description=biosample.description, defaultSchema=ReferenceToAnSchema(id=biosample.defaultSchema_id,name=biosample.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=biosample.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=biosample.defaultSchema_schema_version),
        additionallySupportedSchemas=biosample.aditionally_supported_schemas,nonFilteredQueriesAllowed=biosample.allow_queries_without_filters) if biosample.enable_endpoint == True else None,
        cohort=EntryTypes(id=cohort.id,name=cohort.name,ontologyTermForThisType=OntologyTerm(id=cohort.ontology_id, label=cohort.ontology_name),partOfSpecification=cohort.specification,
                   description=cohort.description, defaultSchema=ReferenceToAnSchema(id=cohort.defaultSchema_id,name=cohort.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=cohort.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=cohort.defaultSchema_schema_version),
        additionallySupportedSchemas=cohort.aditionally_supported_schemas,nonFilteredQueriesAllowed=cohort.allow_queries_without_filters) if cohort.enable_endpoint == True else None,
        dataset=EntryTypes(id=dataset.id,name=dataset.name,ontologyTermForThisType=OntologyTerm(id=dataset.ontology_id, label=dataset.ontology_name),partOfSpecification=dataset.specification,
                   description=dataset.description, defaultSchema=ReferenceToAnSchema(id=dataset.defaultSchema_id,name=dataset.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=dataset.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=dataset.defaultSchema_schema_version),
        additionallySupportedSchemas=dataset.aditionally_supported_schemas,nonFilteredQueriesAllowed=dataset.allow_queries_without_filters) if dataset.enable_endpoint == True else None,
        genomicVariant=EntryTypes(id=genomicVariant.id,name=genomicVariant.name,ontologyTermForThisType=OntologyTerm(id=genomicVariant.ontology_id, label=genomicVariant.ontology_name),partOfSpecification=genomicVariant.specification,
                   description=genomicVariant.description, defaultSchema=ReferenceToAnSchema(id=genomicVariant.defaultSchema_id,name=genomicVariant.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=genomicVariant.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=genomicVariant.defaultSchema_schema_version),
        additionallySupportedSchemas=genomicVariant.aditionally_supported_schemas,nonFilteredQueriesAllowed=genomicVariant.allow_queries_without_filters) if genomicVariant.enable_endpoint == True else None,
        individual=EntryTypes(id=individual.id,name=individual.name,ontologyTermForThisType=OntologyTerm(id=individual.ontology_id, label=individual.ontology_name),partOfSpecification=individual.specification,
                   description=individual.description, defaultSchema=ReferenceToAnSchema(id=individual.defaultSchema_id,name=individual.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=individual.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=individual.defaultSchema_schema_version),
        additionallySupportedSchemas=individual.aditionally_supported_schemas,nonFilteredQueriesAllowed=individual.allow_queries_without_filters) if individual.enable_endpoint == True else None,
        run=EntryTypes(id=run.id,name=run.name,ontologyTermForThisType=OntologyTerm(id=run.ontology_id, label=run.ontology_name),partOfSpecification=run.specification,
                   description=run.description, defaultSchema=ReferenceToAnSchema(id=run.defaultSchema_id,name=run.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=run.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=run.defaultSchema_schema_version),
        additionallySupportedSchemas=run.aditionally_supported_schemas,nonFilteredQueriesAllowed=run.allow_queries_without_filters) if run.enable_endpoint == True else None))



class ConfigurationSchema(EntryTypesSchema):
    schema: str = Field(alias="$schema", default="https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconConfigurationSchema.json")
    maturityAttributes: MaturityAttributes = MaturityAttributes().model_dump(exclude_none=True)
    securityAttributes: Optional[SecurityAttributes] = SecurityAttributes().model_dump(exclude_none=True)

class ConfigurationResponse(BaseModel):
    meta: InformationalMeta
    response: ConfigurationSchema

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

class EntryTypesResponse(BaseModel):
    meta: InformationalMeta
    response: EntryTypesSchema

class Organization(BaseModel):
    name: str = conf.org_name if conf.org_name != "" else None
    url: str = conf.org_contact_url if conf.org_contact_url != "" else None

class ServiceType(BaseModel):
    artifact: str = "org.ga4gh"
    group: str = "beacon"
    version: str = conf.version if conf.version != "" else None

class ServiceInfo(BaseModel):
    contactUrl: Optional[str] = conf.org_contact_url if conf.org_contact_url != "" else None
    createdAt: Optional[str] = conf.create_datetime if conf.create_datetime != "" else None
    description: Optional[str] = conf.description if conf.description != "" else None
    documentationUrl: Optional[str] = conf.documentation_url if conf.documentation_url != "" else None
    environment: Optional[str] = conf.environment if conf.environment != "" else None
    id: Optional[str] = conf.beacon_id if conf.beacon_id != "" else None
    name: Optional[str] = conf.beacon_name if conf.beacon_name != "" else None
    organization: Organization = Organization().model_dump(exclude_none=True)
    type: ServiceType = ServiceType().model_dump(exclude_none=True)
    updatedAt: Optional[str] = conf.update_datetime if conf.update_datetime != "" else None
    version: str = conf.api_version if conf.api_version != "" else None

class FilteringTermInResponse(BaseModel):
    id: str
    label: Optional[str] = None
    scopes: Optional[List[str]] = None
    type: str
    values: Optional[List[str]] = None
    @field_validator('type')
    @classmethod
    def type_must_be_alphanumeric_custom_ontology(cls, v: str) -> str:
        if v not in ['alphanumeric', 'ontology', 'custom']:
            raise ValueError('type must be one between alphanumeric, ontology, custom')
        return v

class Resource(BaseModel):
    id: str
    iriPrefix: Optional[str] = None
    name: Optional[str] = None
    nameSpacePrefix: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None

class FilteringTermsResults(BaseModel):
    filteringTerms: Optional[List[FilteringTermInResponse]] = None
    resources: Optional[List[Resource]] = resources

class FilteringTermsResponse(BaseModel):
    meta: InformationalMeta
    response: FilteringTermsResults

class BeaconError(BaseModel):
    errorCode: int
    errorMessage: Optional[str] = None

class ErrorResponse(BaseModel):
    error: BeaconError
    meta: Meta