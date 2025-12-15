from pydantic import (
    BaseModel
)
from typing import List, Optional, Dict
from beacon.request.parameters import SchemasPerEntity, Pagination
from beacon.conf import conf_override

class ReceivedRequestSummary(BaseModel):
    apiVersion: str
    requestedSchemas: List[SchemasPerEntity]
    pagination: Pagination
    requestedGranularity: str
    testMode: Optional[bool] = None
    filters: Optional[List[str]] = None
    requestParameters: Optional[Dict] = None
    includeResultsetResponses: Optional[str] = None

class Meta(BaseModel):
    apiVersion: str=conf_override.config.api_version
    beaconId: str=conf_override.config.beacon_id
    receivedRequestSummary: ReceivedRequestSummary
    returnedGranularity: str
    returnedSchemas: List[SchemasPerEntity]
    testMode: Optional[bool] = None

class InformationalMeta(BaseModel):
    apiVersion: str=conf_override.config.api_version
    beaconId: str=conf_override.config.beacon_id
    returnedSchemas: List[SchemasPerEntity]