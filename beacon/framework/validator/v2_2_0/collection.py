from pydantic import (
    BaseModel
)
from typing import List, Optional, Union, Dict
from beacon.utils.modules import load_class

class Collections(BaseModel):
    collections: List[Union[Cohorts,Datasets]]

class CollectionResponse(BaseModel):
    meta: load_class("meta", "Meta")
    responseSummary: load_class("common", "ResponseSummary")
    response: Collections
    beaconHandovers: Optional[List[load_class("common", "Handover")]] = None
    info: Optional[Dict] = None