from pydantic import (
    BaseModel
)
from typing import List, Optional, Dict
from beacon.utils.modules import load_class

class BooleanResponseSummary(BaseModel):
    exists: bool

class BooleanResponse(BaseModel):
    meta: load_class("meta", "Meta")
    responseSummary: BooleanResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[load_class("common", "Handover")]] = None