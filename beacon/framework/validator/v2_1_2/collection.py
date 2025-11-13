from pydantic import (
    BaseModel
)
from beacon.validator.v2_1_2.model.cohorts import Cohorts
from beacon.validator.v2_1_2.model.datasets import Datasets
from typing import List, Optional, Union, Dict
from beacon.validator.v2_1_2.framework.meta import Meta
from beacon.validator.v2_1_2.framework.common import Handover, ResponseSummary

class Collections(BaseModel):
    collections: List[Union[Cohorts,Datasets]]

class CollectionResponse(BaseModel):
    meta: Meta
    responseSummary: ResponseSummary
    response: Collections
    beaconHandovers: Optional[List[Handover]] = None
    info: Optional[Dict] = None