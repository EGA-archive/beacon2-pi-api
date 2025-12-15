from beacon.conf import conf_override
from pydantic import (
    BaseModel)
from typing import Optional

class Organization(BaseModel):
    name: str = conf_override.config.org_name if conf_override.config.org_name != "" else None
    url: str = conf_override.config.org_contact_url if conf_override.config.org_contact_url != "" else None

class ServiceType(BaseModel):
    artifact: str = "org.ga4gh"
    group: str = "beacon"
    version: str = conf_override.config.version if conf_override.config.version != "" else None

class ServiceInfoResponse(BaseModel):
    contactUrl: Optional[str] = conf_override.config.org_contact_url if conf_override.config.org_contact_url != "" else None
    createdAt: Optional[str] = conf_override.config.create_datetime if conf_override.config.create_datetime != "" else None
    description: Optional[str] = conf_override.config.description if conf_override.config.description != "" else None
    documentationUrl: Optional[str] = conf_override.config.documentation_url if conf_override.config.documentation_url != "" else None
    environment: Optional[str] = conf_override.config.environment if conf_override.config.environment != "" else None
    id: Optional[str] = conf_override.config.beacon_id if conf_override.config.beacon_id != "" else None
    name: Optional[str] = conf_override.config.beacon_name if conf_override.config.beacon_name != "" else None
    organization: Organization = Organization().model_dump(exclude_none=True)
    type: ServiceType = ServiceType().model_dump(exclude_none=True)
    updatedAt: Optional[str] = conf_override.config.update_datetime if conf_override.config.update_datetime != "" else None
    version: str = conf_override.config.api_version if conf_override.config.api_version != "" else None