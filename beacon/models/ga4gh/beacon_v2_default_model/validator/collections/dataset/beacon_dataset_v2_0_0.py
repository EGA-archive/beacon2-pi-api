import re
import argparse
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    PrivateAttr
)

from typing import Optional, Union, List
from beacon.framework.validator.v2_0_0.common import OntologyTerm
timestamp_regex = re.compile(
    r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"
)
# Regex used to validate timestamp strings in format:
# DD/Mon/YYYY:HH:MM:SS (e.g. 18/Jun/2026:12:30:45)


class DUODataUse(BaseModel):
    id: str
    label: Optional[str] = None
    modifiers: Optional[List[OntologyTerm]] = None
    version: str
    # Represents DUO (Data Use Ontology) usage constraints for a dataset

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensures DUO ID follows CURIE format (e.g., DUO:0000042)
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v


class DataUseConditions(BaseModel):
    duoDataUse: Optional[List[DUODataUse]] = None
    # Wrapper object for multiple DUO usage constraints


class Dataset(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        # Custom init used to strip private attributes before validation
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()
    # Internal/private identifier not exposed in schema validation

    createDateTime: Optional[str] = None
    # Timestamp when dataset was created (validated below)

    dataUseConditions: Optional[DataUseConditions] = None
    # DUO-based restrictions on dataset usage

    description: Optional[str] = None
    # Human-readable dataset description

    externalUrl: Optional[str] = None
    # External link to dataset resource

    id: str
    # Primary dataset identifier

    info: Optional[dict] = None
    # Free-form metadata container

    name: str
    # Human-readable dataset name

    updateDateTime: Optional[str] = None
    # Timestamp for last dataset update

    version: Optional[str] = None
    # Dataset version string (optional semantic/versioning info)

    @field_validator('createDateTime')
    @classmethod
    def check_createDateTime(cls, v: Optional[str]) -> Optional[str]:
        # Validate creation timestamp format if provided
        if v is None:
            return v

        try:
            timestamp_regex.match(v)
        except Exception as e:
            raise ValueError(
                'createDateTime, if string, must be Timestamp, getting this error: {}'.format(e)
            )

        return v

    @field_validator('updateDateTime')
    @classmethod
    def check_updateDateTime(cls, v: Optional[str]) -> Optional[str]:
        # Validate update timestamp format if provided
        if v is None:
            return v

        try:
            timestamp_regex.match(v)
        except Exception as e:
            raise ValueError(
                'updateDateTime, if string, must be Timestamp, getting this error: {}'.format(e)
            )

        return v