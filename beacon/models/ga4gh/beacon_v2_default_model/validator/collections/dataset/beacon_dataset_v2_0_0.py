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

timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")
            
class DUODataUse(BaseModel):
    id: str
    label: Optional[str]=None
    modifiers: Optional[List[OntologyTerm]] = None
    version: str
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v

class DataUseConditions(BaseModel):
    duoDataUse: Optional[List[DUODataUse]] = None

class Dataset(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    createDateTime: Optional[str] = None
    dataUseConditions: Optional[DataUseConditions]=None
    description: Optional[str] = None
    externalUrl: Optional[str] = None
    id: str
    info: Optional[dict] = None
    name: str
    updateDateTime: Optional[str]=None
    version: Optional[str] = None
    @field_validator('createDateTime')
    @classmethod
    def check_createDateTime(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            timestamp_regex.match(v)
        except Exception as e:
            raise ValueError('createDateTime, if string, must be Timestamp, getting this error: {}'.format(e))
        return v
    @field_validator('updateDateTime')
    @classmethod
    def check_updateDateTime(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            timestamp_regex.match(v)
        except Exception as e:
            raise ValueError('updateDateTime, if string, must be Timestamp, getting this error: {}'.format(e))
        return v