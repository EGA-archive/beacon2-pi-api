from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.conf import conf
from beacon.validator.v2_1_2.framework.common import Handover
from beacon.validator.v2_1_2.framework.meta import Meta

class CountResponseSummary(BaseModel):
    exists: bool
    numTotalResults: int
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    def build_count_response_summary(self, count):                                  
        resultsCount=count
        return self(exists=count>0,
                    numTotalResults=resultsCount)
    
class CountResponse(BaseModel):
    meta: Meta
    responseSummary: CountResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None