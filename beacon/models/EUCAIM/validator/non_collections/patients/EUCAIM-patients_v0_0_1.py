import re
from rfc3339_validator import validate_rfc3339

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

class Tumors(BaseModel, extra="forbid"):

    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass
        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()
    tumorId: str
    ER: Optional[OntologyTerm] = None
    PR: Optional[OntologyTerm] = None
    PSA: Optional[float] = None
    HER2: Optional[OntologyTerm] = None
    KI67: Optional[float] = None
    cancerStageCMCategory: Optional[OntologyTerm] = None
    cancerStagePMCategory: Optional[OntologyTerm] = None
    histologicGraceGleasonScore: Optional[OntologyTerm] = None
    histologicGradeISUP: Optional[OntologyTerm] = None
    tumorBIRADSAssesment: Optional[OntologyTerm] = None
    tumorPIRADSAssesment: Optional[OntologyTerm] = None

class Diseases(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    diseaseId: str
    ageAtDiagnosis: float
    diagnosis: OntologyTerm
    yearOfDiagnosis:  Optional[int]=None
    dateOfFirstTreatment: Optional[str]=None
    pathologyConfirmation: Optional[OntologyTerm]=None
    pathology: Optional[list]=None
    imagingProcedureProtocol: Optional[OntologyTerm]=None
    treatment: Optional[List]=None
    tumorMetadata: Optional[Tumors]=None
    @field_validator('dateOfFirstTreatment')
    @classmethod
    def validate_datetime(cls, v):
        if not validate_rfc3339(v):
            raise ValueError("Must be a valid RFC3339 date-time (JSON Schema format=date-time)")
        return v
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

class ImageStudies(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    imageStudyId: str
    disease: Diseases
    imageModality: OntologyTerm
    imageBodyPart: OntologyTerm
    imageManufacturer: OntologyTerm
    dateOfImageAcquisition: str
    @field_validator('dateOfImageAcquisition')
    @classmethod
    def validate_datetime(cls, v):
        if not validate_rfc3339(v):
            raise ValueError("Must be a valid RFC3339 date-time (JSON Schema format=date-time)")
        return v

class Patients(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    patientId: str
    sex: OntologyTerm
    diseases: Optional[List[Diseases]]=None
    imageStudy: Optional[List[ImageStudies]]=None