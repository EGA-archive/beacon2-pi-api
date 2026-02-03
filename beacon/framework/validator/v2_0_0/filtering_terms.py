from typing import Optional, List
from pydantic import (
    BaseModel, field_validator)
from beacon.utils.modules import load_class
import json



class FilteringTermInResponse(BaseModel):
    id: str
    label: Optional[str] = None
    type: str
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

with open("beacon/filtering_terms/resources.json") as resources_file:
    try:
        resources_loaded = json.load(resources_file)
        resources=[]
        for resource in resources_loaded:
            resources.append(Resource(**resource))
    except Exception:
        resources = None

class FilteringTermsResults(BaseModel):
    filteringTerms: Optional[List[FilteringTermInResponse]] = None
    resources: Optional[List[Resource]] = resources

class FilteringTermsResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: FilteringTermsResults