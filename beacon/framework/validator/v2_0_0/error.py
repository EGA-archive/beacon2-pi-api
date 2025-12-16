from typing import Optional
from pydantic import (
    BaseModel)
from beacon.utils.modules import load_class

class BeaconError(BaseModel):
    errorCode: int
    errorMessage: Optional[str] = None

class ErrorResponse(BaseModel):
    error: BeaconError
    meta: load_class("meta", "Meta")