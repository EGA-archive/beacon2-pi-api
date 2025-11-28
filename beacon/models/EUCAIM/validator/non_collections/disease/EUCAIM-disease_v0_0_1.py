import re

from pydantic import (
    BaseModel,
    field_validator,
    PrivateAttr
)
from typing import Optional, List

class OntologyTerm(BaseModel):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. EUCAIM:COM1001288')
        return v.title()

class Disease(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    diseaseId: str
    patientId: str
    ageAtDiagnosis: float
    diagnosis: OntologyTerm
    yearOfDiagnosis:  Optional[int]=None
    dateOfFirstTreatment: Optional[str]=None
    pathologyConfirmation: Optional[OntologyTerm]=None
    pathology: Optional[list]=None
    imagingProcedureProtocol: Optional[OntologyTerm]=None
    treatment: Optional[List]=None
    @field_validator('pathology')
    @classmethod
    def check_pathology(cls, v):
        for pathology in v:
            OntologyTerm(**pathology)
    @field_validator('treatment')
    @classmethod
    def check_treatment(cls, v):
        for treatment in v:
            OntologyTerm(**treatment)