from typing import List, Optional
from pydantic import (
    BaseModel,
    field_validator,
    Field
)
from beacon.conf.conf_override import config
from beacon.utils.modules import load_class

class SecurityAttributes(BaseModel):
    # Default granularity level used by the Beacon when none is explicitly requested.
    defaultGranularity: Optional[str] = config.default_beacon_granularity

    # List of supported security levels configured for the Beacon instance.
    securityLevels: Optional[List[str]] = config.security_levels

    @field_validator('defaultGranularity')
    @classmethod
    def defaultGranularity_must_be_boolean_count_record(cls, v: str) -> str:
        """
        Ensure that the configured default granularity is valid.

        Allowed values:
        - boolean: only indicate whether data exists
        - count: return aggregate counts
        - record: return full records (subject to permissions)
        """
        if v not in ['boolean', 'count', 'record']:
            raise ValueError(
                'defaultGranularity must be one between boolean, count, record'
            )

        return v


class MaturityAttributes(BaseModel):
    # Deployment maturity level (e.g. DEV, TEST, PROD).
    # Retrieved from the application configuration and converted to uppercase.
    productionStatus: str = config.environment.upper()


# Generate dictionaries from the models while excluding fields with None values.
# These dictionaries are later used to instantiate the configuration schema.
maturity_attributes = MaturityAttributes().model_dump(exclude_none=True)
security_attributes = SecurityAttributes().model_dump(exclude_none=True)


class ConfigurationSchema(load_class("entry_types", "EntryTypesSchema")):
    """
    Beacon configuration schema.

    Extends the entry types schema with Beacon-wide configuration
    information such as security and maturity attributes.
    """

    # JSON schema definition used by Beacon configuration documents.
    schema: str = Field(
        alias="$schema",
        default=(
            "https://raw.githubusercontent.com/ga4gh-beacon/"
            "beacon-framework-v2/main/configuration/"
            "beaconConfigurationSchema.json"
        )
    )

    # Information about the deployment environment maturity.
    maturityAttributes: MaturityAttributes = (
        MaturityAttributes(**maturity_attributes)
    )

    # Security-related configuration settings.
    securityAttributes: Optional[SecurityAttributes] = (
        SecurityAttributes(**security_attributes)
    )


class ConfigurationResponse(BaseModel):
    """
    Standard API response wrapper for Beacon configuration endpoints.
    """

    # Response metadata (API version, timestamps, etc.).
    meta: load_class("meta", "InformationalMeta")

    # Main configuration payload returned to the client.
    response: ConfigurationSchema