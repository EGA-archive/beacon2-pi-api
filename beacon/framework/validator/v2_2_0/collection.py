from pydantic import (
    BaseModel
)
from typing import List, Optional, Union, Dict
from beacon.validator.v2_2_0.framework.meta import Meta
from beacon.validator.v2_2_0.framework.common import Handover, ResponseSummary

class Collections(BaseModel):
    collections: List[Union[Cohorts,Datasets]]

class CollectionResponse(BaseModel):
    meta: Meta
    responseSummary: ResponseSummary
    response: Collections
    beaconHandovers: Optional[List[Handover]] = None
    info: Optional[Dict] = None