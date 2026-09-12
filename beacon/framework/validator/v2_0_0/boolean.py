from pydantic import (
    BaseModel
)
from typing import List, Optional, Dict
from beacon.framework.validator.v2_0_0.meta import Meta
from common import Handover

class BooleanResponseSummary(BaseModel):
    exists: bool

class BooleanResponse(BaseModel):
    meta: Meta
    responseSummary: BooleanResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None