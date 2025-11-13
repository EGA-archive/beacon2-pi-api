from typing import Optional
from pydantic import (
    BaseModel)

class BeaconError(BaseModel):
    errorCode: int
    errorMessage: Optional[str] = None

class ErrorResponse(BaseModel):
    error: BeaconError
    meta: load_class("meta", "Meta")