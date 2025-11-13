import re
from pydantic import (
    BaseModel,
    ValidationError,
    PrivateAttr,
    field_validator
)
from typing import Optional, Union

class OntologyTerm(BaseModel):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v

class Imaging(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    patient_id: str
    image_modality: OntologyTerm
    image_body_part: OntologyTerm
    image_manufacturer: OntologyTerm
    date_of_image_acquisition: str
    patient_age_at_study: Optional[Union[int,float]]=None