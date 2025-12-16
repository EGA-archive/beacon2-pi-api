from beacon.filtering_terms.resources import resources
from typing import Optional, List
from pydantic import (
    BaseModel, field_validator)
from beacon.utils.modules import load_class
from beacon.framework.validator.v2_0_0.filtering_terms import Resource

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

class FilteringTermsResults(BaseModel):
    filteringTerms: Optional[List[FilteringTermInResponse]] = None
    resources: Optional[List[Resource]] = resources

class FilteringTermsResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: FilteringTermsResults