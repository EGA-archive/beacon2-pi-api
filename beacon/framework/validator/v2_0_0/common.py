from pydantic import (
    BaseModel,
    field_validator
)
from typing import Optional
from beacon.request.classes import RequestAttributes
from beacon.conf import conf_override
import math
import re

class OntologyTerm(BaseModel):
    """
    Represents a controlled vocabulary term (ontology concept),
    identified by a CURIE-style identifier.
    """

    id: str
    label: Optional[str] = None

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensure identifier follows CURIE-like pattern (e.g. NCIT:C42331)
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')

        # Return validated identifier unchanged
        return v


class ResponseSummary(BaseModel):
    """
    Summary of a dataset response including existence and optional total count.
    """

    exists: bool
    numTotalResults: Optional[int] = None

    def build_response_summary_by_dataset(self, datasets):
        """
        Compute aggregated response metadata across datasets.

        This method determines:
        - Whether any results exist
        - Total number of results (possibly approximated depending on configuration)
        - Whether response should degrade to boolean granularity
        """

        # Running totals for counted and non-counted datasets
        count = 0
        non_counted = 0

        # Requested granularity from request context
        granularity = RequestAttributes.qparams.query.requestedGranularity

        # Iterate over all datasets contributing to the response
        for dataset in datasets:

            # If dataset is not boolean-only and system is not forcing boolean responses
            if dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':

                # --- Case 1: imprecise count mode ---
                if conf_override.config.imprecise_count != 0:
                    # Replace small counts with fixed imprecision threshold
                    if dataset.dataset_count < conf_override.config.imprecise_count:
                        count += conf_override.config.imprecise_count

                # --- Case 2: rounding to nearest 10 ---
                elif conf_override.config.round_to_tens == True:
                    count += math.ceil(dataset.dataset_count / 10.0) * 10

                # --- Case 3: rounding to nearest 100 ---
                elif conf_override.config.round_to_hundreds == True:
                    count += math.ceil(dataset.dataset_count / 100.0) * 100

                # --- Case 4: exact counting ---
                else:
                    count += dataset.dataset_count

            else:
                # If dataset is boolean-only or granularity restricts counting
                non_counted += dataset.dataset_count

        # ------------------------------------------------------------
        # Final response decision logic:
        # ------------------------------------------------------------

        # Case 1: nothing counted but non-counted results exist
        if count == 0 and non_counted > 0:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=True)

        # Case 2: counted results exist
        elif count > 0:
            return self(exists=count > 0, numTotalResults=count)

        # Case 3: no results at all
        else:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=False)


class Handover(BaseModel):
    """
    Represents a handover link or mechanism for external data transfer.
    """

    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str


class ReferenceToAnSchema(BaseModel):
    """
    Metadata describing a reference to an external schema definition.
    """

    id: str
    name: str
    description: Optional[str] = None
    referenceToSchemaDefinition: str
    schemaVersion: Optional[str] = None