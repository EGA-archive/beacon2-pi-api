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
from beacon.framework.validator.v2_0_0.common import OntologyTerm

class Run(BaseModel):
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