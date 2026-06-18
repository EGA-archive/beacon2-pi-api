from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.conf import conf_override
from beacon.utils.modules import load_class

class CountResponseSummary(BaseModel):
    """
    Response summary model for count-based queries.

    This model supports:
    - Exact counts
    - Imprecise counts (threshold-based masking)
    - Rounded counts (to tens/hundreds)
    - Metadata about how the final count was adjusted
    """

    countAdjustedTo: Optional[List[Union[str, int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    numTotalResults: int

    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded(cls, v: str) -> str:
        """
        Validate count precision mode.

        Allowed values:
        - exact: no modification applied
        - imprecise: values below threshold are masked
        - rounded: values are rounded to configured granularity
        """

        # Ensure only supported precision modes are accepted
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')

        return v

    def build_count_response_summary(self, count):
        """
        Build a response summary based on a raw numeric count.

        The returned summary may modify the raw count depending on:
        - Imprécision thresholds
        - Rounding rules (tens / hundreds)
        - Configuration overrides

        This method also annotates how the count was transformed.
        """

        # Initialize metadata fields describing transformations
        countAdjustedTo = None
        countPrecision = None

        # ------------------------------------------------------------
        # Case 1: Imprecise counting mode (threshold-based masking)
        # ------------------------------------------------------------
        if conf_override.config.imprecise_count != 0:

            # If count is below threshold, replace with minimum imprecise value
            if count < conf_override.config.imprecise_count:
                resultsCount = conf_override.config.imprecise_count

                # Record adjustment applied to output
                countAdjustedTo = [conf_override.config.imprecise_count]
                countPrecision = 'imprecise'

            else:
                # Otherwise keep exact value
                resultsCount = count

        # ------------------------------------------------------------
        # Case 2: Round counts to nearest 10
        # ------------------------------------------------------------
        elif conf_override.config.round_to_tens == True:
            resultsCount = math.ceil(count / 10.0) * 10
            countAdjustedTo = ['immediate ten']
            countPrecision = 'rounded'

        # ------------------------------------------------------------
        # Case 3: Round counts to nearest 100
        # ------------------------------------------------------------
        elif conf_override.config.round_to_hundreds == True:
            resultsCount = math.ceil(count / 100.0) * 100
            countAdjustedTo = ['immediate hundred']
            countPrecision = 'rounded'

        # ------------------------------------------------------------
        # Case 4: No transformation applied (exact mode)
        # ------------------------------------------------------------
        else:
            resultsCount = count

        # Return final structured response summary
        return self(
            exists=count > 0,
            numTotalResults=resultsCount,
            countAdjustedTo=countAdjustedTo,
            countPrecision=countPrecision
        )


class CountResponse(BaseModel):
    """
    Full API response wrapper for count queries.

    Combines:
    - Metadata
    - Count summary
    - Optional auxiliary information
    - Optional handover links to external systems
    """

    meta: load_class("meta", "Meta")
    responseSummary: CountResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[load_class("common", "Handover")]] = None