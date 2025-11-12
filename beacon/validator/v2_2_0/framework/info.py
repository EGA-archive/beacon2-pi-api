from beacon.conf import conf
from typing import Optional, Dict
from pydantic import (
    BaseModel)
from beacon.validator.v2_2_0.framework.meta import InformationalMeta

class BeaconOrganization(BaseModel):
    address: Optional[str]=conf.org_adress if conf.org_adress != "" else None
    contactUrl: Optional[str]=conf.org_contact_url if conf.org_contact_url != "" else None
    description: Optional[str]=conf.org_description if conf.org_description != "" else None
    id: str=conf.org_id
    info: Optional[str]=conf.org_info if conf.org_info != "" else None
    logoUrl: Optional[str]=conf.org_logo_url if conf.org_logo_url != "" else None
    name: str=conf.org_name
    welcomeUrl: Optional[str]=conf.org_welcome_url if conf.welcome_url != "" else None

class InfoBody(BaseModel):
    alternativeUrl: Optional[str]=conf.alternative_url if conf.alternative_url != "" else None
    createDateTime: Optional[str]=conf.create_datetime if conf.create_datetime != "" else None
    description: Optional[str]=conf.description if conf.description != "" else None
    info: Optional[Dict]=None
    updateDateTime: Optional[str]=conf.update_datetime if conf.update_datetime != "" else None
    version: Optional[str]=conf.version if conf.version != "" else None
    welcomeUrl: Optional[str]=conf.welcome_url if conf.welcome_url != "" else None
    id: str = conf.beacon_id
    name: str = conf.beacon_name
    apiVersion: str = conf.api_version
    environment: str = conf.environment
    organization: BeaconOrganization = BeaconOrganization().model_dump(exclude_none=True)
    
class InfoResponse(BaseModel):
    meta: InformationalMeta
    response: InfoBody