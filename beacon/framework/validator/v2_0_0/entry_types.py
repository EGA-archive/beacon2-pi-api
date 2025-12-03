from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    create_model
)
import re
from typing import List, Optional
from beacon.utils.modules import load_class, get_modules_confiles

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

list_of_modules=get_modules_confiles()

fields_related = {str(key): (Optional[EntryTypes],None) for field_name in list_of_modules for key, value in field_name.items() }

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
            for entry_type, set_of_params in module.items():
                if set_of_params["entry_type_enabled"] == True:
                    values_to_set["id"] = entry_type
                    values_to_set["name"] = set_of_params["info"]["name"]
                    values_to_set["ontologyTermForThisType"] = OntologyTerm(id=set_of_params["info"]["ontology_id"],label=set_of_params["info"]["ontology_name"])
                    values_to_set["partOfSpecification"] = set_of_params["schema"]["specification"]
                    values_to_set["description"] = set_of_params["info"]["description"]
                    values_to_set["defaultSchema"] = ReferenceToAnSchema(id=set_of_params["schema"]["default_schema_id"],name=set_of_params["schema"]["default_schema_name"],
                                                                                        referenceToSchemaDefinition=set_of_params["schema"]["reference_to_default_schema_definition"],
                                                                                        schemaVersion=set_of_params["schema"]["default_schema_version"])
                    values_to_set["additionallySupportedSchemas"] = set_of_params["schema"]["supported_schemas"]
                    values_to_set["nonFilteredQueriesAllowed"] =set_of_params["allow_queries_without_filters"]

                    Entries_values_to_Set[entry_type]=values_to_set


            
        if Entries_values_to_Set !={}:
            entryTypes_values_to_set = Entries(**Entries_values_to_Set)
        else:
            entryTypes_values_to_set = None
        return self(entryTypes=entryTypes_values_to_set)

class EntryTypesResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: EntryTypesSchema