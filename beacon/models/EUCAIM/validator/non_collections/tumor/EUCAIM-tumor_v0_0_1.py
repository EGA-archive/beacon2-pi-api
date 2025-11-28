import re
from typing import Optional
from pydantic import BaseModel, field_validator, PrivateAttr


class OntologyTerm(BaseModel):

    id: str
    label: Optional[str] = None

    @field_validator("id")
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError("id must be CURIE, e.g. EUCAIM:COM1001288")
        return v.title()


class Tumor(BaseModel, extra="forbid"):

    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass
        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()
    tumorId: str
    patientId: str
    diseaseId: str

    # optional
    imageId: Optional[str] = None
    tumorMarkerTestResult: Optional[OntologyTerm] = None
    cancerStageCMCategory: Optional[OntologyTerm] = None
    cancerStagePMCategory: Optional[OntologyTerm] = None
    histologicGraceGleasonScore: Optional[OntologyTerm] = None
    histologicGradeISUP: Optional[OntologyTerm] = None
    tumorBIRADSAssesment: Optional[OntologyTerm] = None
    tumorPIRADSAssesment: Optional[OntologyTerm] = None
