from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    create_model
)
import re
from typing import List, Optional
from beacon.utils.modules import load_class, get_all_modules_conf
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

prelist_of_modules = get_all_modules_conf()

list_of_modules=[x for x in prelist_of_modules if x.id != ""]

fields_related = {str(field_name.id): (Optional[EntryTypes],None) for field_name in list_of_modules}

Entries = create_model("Entries", **fields_related)

ReferenceToAnSchema = load_class("common","ReferenceToAnSchema")

class Entries(Entries):
    @model_validator(mode="before")
    def at_least_one_not_none(cls, values):
        if not any(value is not None for value in values.values()):
            raise ValueError("At least one entry type must be active for the beacon")
        return values

class EntryTypesSchema(BaseModel):
    entryTypes: Entries

    def return_schema(self):
        Entries_values_to_Set={}
        for module in list_of_modules:
            values_to_set = {}
            
            if module.enable_endpoint == True:
                values_to_set["id"] = module.id
                values_to_set["name"] = module.name
                values_to_set["ontologyTermForThisType"] = OntologyTerm(id=module.ontology_id,label=module.ontology_name)
                values_to_set["partOfSpecification"] = module.specification
                values_to_set["description"] = module.description
                values_to_set["defaultSchema"] = ReferenceToAnSchema(id=module.defaultSchema_id,name=module.defaultSchema_name,
                                                                                       referenceToSchemaDefinition=module.defaultSchema_reference_to_schema_definition,
                                                                                       schemaVersion=module.defaultSchema_schema_version)
                values_to_set["additionallySupportedSchemas"] = module.aditionally_supported_schemas
                values_to_set["nonFilteredQueriesAllowed"] =module.allow_queries_without_filters

                Entries_values_to_Set[module.id]=values_to_set


            
        if Entries_values_to_Set !={}:
            entryTypes_values_to_set = Entries(**Entries_values_to_Set)
        else:
            entryTypes_values_to_set = None
        return self(entryTypes=entryTypes_values_to_set)

class EntryTypesResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: EntryTypesSchema