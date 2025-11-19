from pydantic import (
    field_validator,
)
from typing import List, Optional, Union
from beacon.request.classes import CamelModel, Similarity, Operator
import re

class OntologyFilter(CamelModel, extra='forbid'):
    id: str
    scope: Optional[str] =None
    includeDescendantTerms: Optional[bool] = True
    similarity: Optional[Similarity] = Similarity.EXACT
    @field_validator('id')
    @classmethod
    def id__ontology_filter_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v

class AlphanumericFilter(CamelModel, extra='forbid'):
    id: str
    value: Union[str, int, List[int]]
    scope: Optional[str] =None
    operator: Operator = Operator.EQUAL
    @field_validator('id')
    @classmethod
    def id__alphanumeric_filter_must_not_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError('id must be a schema field reference, not a CURIE')
        return v

class CustomFilter(CamelModel, extra='forbid'):
    id: str
    scope: Optional[str] =None