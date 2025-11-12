from typing import List, Optional
from pydantic import (
    BaseModel,
    field_validator,
    Field
)
from beacon.conf import conf
from beacon.validator.v2_1_2.framework.entry_types import EntryTypesSchema
from beacon.validator.v2_1_2.framework.meta import InformationalMeta

class SecurityAttributes(BaseModel):
    defaultGranularity: Optional[str] = conf.default_beacon_granularity
    securityLevels: Optional[List[str]] = conf.security_levels
    @field_validator('defaultGranularity')
    @classmethod
    def defaultGranularity_must_be_boolean_count_record(cls, v: str) -> str:
        if v not in ['boolean', 'count', 'record']:
            raise ValueError('defaultGranularity must be one between boolean, count, record')
        return v

class MaturityAttributes(BaseModel):
    productionStatus: str = conf.environment.upper()

class ConfigurationSchema(EntryTypesSchema):
    schema: str = Field(alias="$schema", default="https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconConfigurationSchema.json")
    maturityAttributes: MaturityAttributes = MaturityAttributes().model_dump(exclude_none=True)
    securityAttributes: Optional[SecurityAttributes] = SecurityAttributes().model_dump(exclude_none=True)

class ConfigurationResponse(BaseModel):
    meta: InformationalMeta
    response: ConfigurationSchema