from typing import Optional
from pydantic import (
    BaseModel)
from beacon.framework.validator.v2_0_0.meta import Meta

class BeaconError(BaseModel):
    errorCode: int
    errorMessage: Optional[str] = None

class ErrorResponse(BaseModel):
    error: BeaconError
    meta: Meta