import re
import argparse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)

from typing import Optional, Union

#parser = argparse.ArgumentParser()
#parser.add_argument("-url", "--url")
#args = parser.parse_args()

class OntologyTerm(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class Runs(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    biosampleId: str
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    libraryLayout: Optional[str]=None
    librarySelection: Optional[str]=None
    librarySource: Optional[OntologyTerm] = None
    libraryStrategy: Optional[str] = None
    platform: Optional[str] = None
    platformModel: Optional[OntologyTerm] = None
    runDate: Optional[str] = None