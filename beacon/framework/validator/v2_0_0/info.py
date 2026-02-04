from beacon.conf import conf_override
from typing import Optional, Dict
from pydantic import (
    BaseModel)
from beacon.utils.modules import load_class

class BeaconOrganization(BaseModel):
    address: Optional[str]=conf_override.config.org_adress if conf_override.config.org_adress != "" else None
    contactUrl: Optional[str]=conf_override.config.org_contact_url if conf_override.config.org_contact_url != "" else None
    description: Optional[str]=conf_override.config.org_description if conf_override.config.org_description != "" else None
    id: str=conf_override.config.org_id
    info: Optional[str]=conf_override.config.org_info if conf_override.config.org_info != "" else None
    logoUrl: Optional[str]=conf_override.config.org_logo_url if conf_override.config.org_logo_url != "" else None
    name: str=conf_override.config.org_name
    welcomeUrl: Optional[str]=conf_override.config.org_welcome_url if conf_override.config.welcome_url != "" else None

class InfoBody(BaseModel):
    alternativeUrl: Optional[str]=conf_override.config.alternative_url if conf_override.config.alternative_url != "" else None
    createDateTime: Optional[str]=conf_override.config.create_datetime if conf_override.config.create_datetime != "" else None
    description: Optional[str]=conf_override.config.description if conf_override.config.description != "" else None
    info: Optional[Dict]=None
    updateDateTime: Optional[str]=conf_override.config.update_datetime if conf_override.config.update_datetime != "" else None
    version: Optional[str]=conf_override.config.version if conf_override.config.version != "" else None
    welcomeUrl: Optional[str]=conf_override.config.welcome_url if conf_override.config.welcome_url != "" else None
    id: str = conf_override.config.beacon_id
    name: str = conf_override.config.beacon_name
    apiVersion: str = conf_override.config.api_version
    environment: str = conf_override.config.environment
    organization: BeaconOrganization = BeaconOrganization().model_dump(exclude_none=True)
    
class InfoResponse(BaseModel):
    meta: load_class("meta", "InformationalMeta")
    response: InfoBody