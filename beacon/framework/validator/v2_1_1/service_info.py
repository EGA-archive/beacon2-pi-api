from beacon.conf import conf
from pydantic import (
    BaseModel)
from typing import Optional

class Organization(BaseModel):
    name: str = conf.org_name if conf.org_name != "" else None
    url: str = conf.org_contact_url if conf.org_contact_url != "" else None

class ServiceType(BaseModel):
    artifact: str = "org.ga4gh"
    group: str = "beacon"
    version: str = conf.version if conf.version != "" else None

class ServiceInfoResponse(BaseModel):
    contactUrl: Optional[str] = conf.org_contact_url if conf.org_contact_url != "" else None
    createdAt: Optional[str] = conf.create_datetime if conf.create_datetime != "" else None
    description: Optional[str] = conf.description if conf.description != "" else None
    documentationUrl: Optional[str] = conf.documentation_url if conf.documentation_url != "" else None
    environment: Optional[str] = conf.environment if conf.environment != "" else None
    id: Optional[str] = conf.beacon_id if conf.beacon_id != "" else None
    name: Optional[str] = conf.beacon_name if conf.beacon_name != "" else None
    organization: Organization = Organization().model_dump(exclude_none=True)
    type: ServiceType = ServiceType().model_dump(exclude_none=True)
    updatedAt: Optional[str] = conf.update_datetime if conf.update_datetime != "" else None
    version: str = conf.api_version if conf.api_version != "" else None