from pydantic import (
    field_validator,
)
from typing import List, Optional, Union
from beacon.request.classes import CamelModel, Similarity, Operator
import re
from beacon.request.classes import RequestAttributes

# Filter based on ontology terms (e.g., disease ontologies, phenotype ontologies)
class OntologyFilter(CamelModel, extra='forbid'):
    id: str  # Must be a CURIE (e.g. NCIT:C42331)
    scope: Optional[str] = None  # Optional domain scope restriction
    includeDescendantTerms: Optional[bool] = True  # Whether ontology hierarchy descendants are included
    similarity: Optional[Similarity] = Similarity.EXACT  # Matching strictness for ontology search


# Filter for structured alphanumeric comparisons (e.g., numeric or string equality/range queries)
class AlphanumericFilter(CamelModel, extra='forbid'):
    id: str  # Must NOT be a CURIE; must reference a schema field
    value: Union[str, int, List[int], float, List[float]]  # Filter value(s)
    scope: Optional[str] = None  # Optional domain scope
    operator: Operator = Operator.EQUAL  # Comparison operator (default: equality)


# Generic custom filter structure (no validation rules beyond schema constraint)
class CustomFilter(CamelModel, extra='forbid'):
    id: str  # Arbitrary filter identifier (schema-defined field)
    scope: Optional[str] = None  # Optional scope for filtering context