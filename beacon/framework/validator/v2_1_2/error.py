from typing import Optional
from pydantic import (
    BaseModel)
from beacon.validator.v2_1_2.framework.meta import Meta

class BeaconError(BaseModel):
    errorCode: int
    errorMessage: Optional[str] = None

class ErrorResponse(BaseModel):
    error: BeaconError
    meta: Meta