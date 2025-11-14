from pydantic import (
    BaseModel,
    model_validator,
    field_validator
)
import re
from typing import List, Optional
from beacon.utils.modules import load_class
from beacon.models.ga4gh.beacon_v2_default_model.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run

class OntologyTerm(BaseModel):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v

class EntryTypes(BaseModel):
    aCollectionOf: Optional[List] = None
    additionallySupportedSchemas: Optional[List[load_class("common","ReferenceToAnSchema")]] = None
    defaultSchema: load_class("common","ReferenceToAnSchema")
    description: Optional[str] = None
    id: str
    name: str
    nonFilteredQueriesAllowed: Optional[bool] = True
    ontologyTermForThisType: Optional[OntologyTerm] = None
    partOfSpecification: str

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
                   description=analysis.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=analysis.defaultSchema_id,name=analysis.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=analysis.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=analysis.defaultSchema_schema_version),
        additionallySupportedSchemas=analysis.aditionally_supported_schemas,nonFilteredQueriesAllowed=analysis.allow_queries_without_filters) if analysis.enable_endpoint == True else None,
        biosample=EntryTypes(id=biosample.id,name=biosample.name,ontologyTermForThisType=OntologyTerm(id=biosample.ontology_id, label=biosample.ontology_name),partOfSpecification=biosample.specification,
                   description=biosample.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=biosample.defaultSchema_id,name=biosample.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=biosample.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=biosample.defaultSchema_schema_version),
        additionallySupportedSchemas=biosample.aditionally_supported_schemas,nonFilteredQueriesAllowed=biosample.allow_queries_without_filters) if biosample.enable_endpoint == True else None,
        cohort=EntryTypes(id=cohort.id,name=cohort.name,ontologyTermForThisType=OntologyTerm(id=cohort.ontology_id, label=cohort.ontology_name),partOfSpecification=cohort.specification,
                   description=cohort.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=cohort.defaultSchema_id,name=cohort.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=cohort.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=cohort.defaultSchema_schema_version),
        additionallySupportedSchemas=cohort.aditionally_supported_schemas,nonFilteredQueriesAllowed=cohort.allow_queries_without_filters) if cohort.enable_endpoint == True else None,
        dataset=EntryTypes(id=dataset.id,name=dataset.name,ontologyTermForThisType=OntologyTerm(id=dataset.ontology_id, label=dataset.ontology_name),partOfSpecification=dataset.specification,
                   description=dataset.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=dataset.defaultSchema_id,name=dataset.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=dataset.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=dataset.defaultSchema_schema_version),
        additionallySupportedSchemas=dataset.aditionally_supported_schemas,nonFilteredQueriesAllowed=dataset.allow_queries_without_filters) if dataset.enable_endpoint == True else None,
        genomicVariant=EntryTypes(id=genomicVariant.id,name=genomicVariant.name,ontologyTermForThisType=OntologyTerm(id=genomicVariant.ontology_id, label=genomicVariant.ontology_name),partOfSpecification=genomicVariant.specification,
                   description=genomicVariant.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=genomicVariant.defaultSchema_id,name=genomicVariant.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=genomicVariant.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=genomicVariant.defaultSchema_schema_version),
        additionallySupportedSchemas=genomicVariant.aditionally_supported_schemas,nonFilteredQueriesAllowed=genomicVariant.allow_queries_without_filters) if genomicVariant.enable_endpoint == True else None,
        individual=EntryTypes(id=individual.id,name=individual.name,ontologyTermForThisType=OntologyTerm(id=individual.ontology_id, label=individual.ontology_name),partOfSpecification=individual.specification,
                   description=individual.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=individual.defaultSchema_id,name=individual.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=individual.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=individual.defaultSchema_schema_version),
        additionallySupportedSchemas=individual.aditionally_supported_schemas,nonFilteredQueriesAllowed=individual.allow_queries_without_filters) if individual.enable_endpoint == True else None,
        run=EntryTypes(id=run.id,name=run.name,ontologyTermForThisType=OntologyTerm(id=run.ontology_id, label=run.ontology_name),partOfSpecification=run.specification,
                   description=run.description, defaultSchema=load_class("common","ReferenceToAnSchema")(id=run.defaultSchema_id,name=run.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=run.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=run.defaultSchema_schema_version),
        additionallySupportedSchemas=run.aditionally_supported_schemas,nonFilteredQueriesAllowed=run.allow_queries_without_filters) if run.enable_endpoint == True else None))

class EntryTypesResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: EntryTypesSchema