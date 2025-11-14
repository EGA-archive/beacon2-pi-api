from pydantic import (
    BaseModel
)
from typing import List, Optional, Union, Dict
from beacon.utils.modules import load_class, load_types_of_results

class Collections(BaseModel):
    collections: List[Union[load_types_of_results("collections")]]

class CollectionResponse(BaseModel):
    meta: load_class("meta", "Meta")
    responseSummary: load_class("common", "ResponseSummary")
    response: Collections
    beaconHandovers: Optional[List[load_class("common", "Handover")]] = None
    info: Optional[Dict] = None