from typing import Optional, List
from pydantic import (
    BaseModel, field_validator)
from beacon.utils.modules import load_class
import json

class FilteringTermInResponse(BaseModel):
    """
    Represents a filtering term returned by the Beacon filtering terms endpoint.

    Filtering terms can originate from ontology resources, custom vocabularies,
    or simple alphanumeric values.
    """

    # Unique identifier of the filtering term.
    id: str

    # Human-readable label associated with the filtering term.
    label: Optional[str] = None

    # Category of filtering term.
    # Allowed values:
    # - alphanumeric: plain text or code values
    # - ontology: ontology-backed terms
    # - custom: custom Beacon-specific terms
    type: str

    @field_validator('type')
    @classmethod
    def type_must_be_alphanumeric_custom_ontology(cls, v: str) -> str:
        """
        Validate that the filtering term type is one of the supported values.
        """
        if v not in ['alphanumeric', 'ontology', 'custom']:
            raise ValueError(
                'type must be one between alphanumeric, ontology, custom'
            )

        return v


class Resource(BaseModel):
    """
    Describes an ontology or controlled vocabulary resource that provides
    filtering terms.
    """

    # Unique identifier for the resource.
    id: str

    # IRI prefix used by terms from this resource.
    iriPrefix: Optional[str] = None

    # Human-readable resource name.
    name: Optional[str] = None

    # Namespace prefix used by the resource (e.g. NCIT, EFO).
    nameSpacePrefix: Optional[str] = None

    # URL where the resource can be accessed.
    url: Optional[str] = None

    # Version of the ontology/resource.
    version: Optional[str] = None


# Load ontology resource definitions from the configuration file.
# These resources are included in filtering terms responses to help
# clients interpret ontology-based filtering terms.
with open("beacon/filtering_terms/resources.json") as resources_file:
    try:
        # Parse JSON configuration.
        resources_loaded = json.load(resources_file)

        # Convert each resource definition into a validated Resource model.
        resources = []

        for resource in resources_loaded:
            resources.append(Resource(**resource))

    except Exception:
        # If the file cannot be loaded or contains invalid data,
        # fall back to None rather than preventing application startup.
        resources = None


class FilteringTermsResults(BaseModel):
    """
    Response payload containing available filtering terms and
    supporting ontology resources.
    """

    # Collection of filtering terms available for querying.
    filteringTerms: Optional[List[FilteringTermInResponse]] = None

    # Ontology and vocabulary resources referenced by filtering terms.
    # Defaults to the resources loaded from resources.json.
    resources: Optional[List[Resource]] = resources


class FilteringTermsResponse(BaseModel):
    """
    Standard Beacon API response wrapper for filtering terms endpoints.
    """

    # Response metadata such as API version and schema information.
    meta: load_class("meta", "InformationalMeta")

    # Main response payload containing filtering terms and resources.
    response: FilteringTermsResults