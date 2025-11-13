from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.conf import conf
from beacon.validator.v2_2_0.framework.common import Handover
from beacon.validator.v2_2_0.framework.meta import Meta

class CountResponseSummary(BaseModel):
    countAdjustedTo: Optional[List[Union[str,int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    numTotalResults: int
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    def build_count_response_summary(self, count):
        countAdjustedTo=None
        countPrecision=None                                    
        if conf.imprecise_count !=0:
            if count < conf.imprecise_count:
                resultsCount=conf.imprecise_count
                countAdjustedTo=[conf.imprecise_count]
                countPrecision='imprecise'
            else:
                resultsCount=count
                
        elif conf.round_to_tens == True:
            resultsCount=math.ceil(count / 10.0) * 10
            countAdjustedTo=['immediate ten']
            countPrecision='rounded'

        elif conf.round_to_hundreds == True:
            resultsCount=math.ceil(count / 100.0) * 100
            countAdjustedTo=['immediate hundred']
            countPrecision='rounded'
        else:
            resultsCount=count
        return self(exists=count>0,
                    numTotalResults=resultsCount,
                    countAdjustedTo=countAdjustedTo,
                    countPrecision=countPrecision)
    
class CountResponse(BaseModel):
    meta: Meta
    responseSummary: CountResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None