from pydantic import (
    BaseModel
)
from typing import List, Optional, Dict
from beacon.validator.v2_1_1.framework.meta import Meta
from beacon.validator.v2_1_1.framework.common import Handover

class BooleanResponseSummary(BaseModel):
    exists: bool

class BooleanResponse(BaseModel):
    meta: Meta
    responseSummary: BooleanResponseSummary
    info: Optional[Dict] = None
    beaconHandovers: Optional[List[Handover]] = None