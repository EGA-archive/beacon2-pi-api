import re
from rfc3339_validator import validate_rfc3339

from pydantic import (
    BaseModel,
    field_validator,
    PrivateAttr
)
from typing import Optional, List

class OntologyTerm(BaseModel):
    # Generic ontology reference structure used across the schema
    id: str  # CURIE-style identifier (e.g. EUCAIM:COM1001288)
    label: Optional[str] = None  # Human-readable label (optional)

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensure identifier follows CURIE pattern: prefix:local_id
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            # Reject malformed ontology identifiers early
            raise ValueError('id must be CURIE, e.g. EUCAIM:COM1001288')

        # Normalize formatting (title-casing the identifier)
        return v.title()


class Tumors(BaseModel, extra="forbid"):
    # Tumor-specific biomarker and staging metadata container

    def __init__(self, **data) -> None:
        # Remove private attributes before validation (internal bookkeeping)
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()  # Internal DB identifier (not exposed externally)

    tumorId: str  # Primary tumor identifier

    # Hormone receptor / biomarker annotations
    ER: Optional[OntologyTerm] = None
    PR: Optional[OntologyTerm] = None
    PSA: Optional[float] = None  # Numeric biomarker
    HER2: Optional[OntologyTerm] = None
    KI67: Optional[float] = None  # Proliferation index

    # Cancer staging fields (various clinical classification systems)
    cancerStageCMCategory: Optional[OntologyTerm] = None
    cancerStagePMCategory: Optional[OntologyTerm] = None

    # Histopathology grading systems
    histologicGraceGleasonScore: Optional[OntologyTerm] = None
    histologicGradeISUP: Optional[OntologyTerm] = None

    # Imaging-based tumor assessments
    tumorBIRADSAssesment: Optional[OntologyTerm] = None
    tumorPIRADSAssesment: Optional[OntologyTerm] = None


class Diseases(BaseModel, extra='forbid'):
    # Disease record linked to a patient or cohort entity

    def __init__(self, **data) -> None:
        # Strip private fields before Pydantic validation
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()  # Internal persistence ID

    diseaseId: str  # Unique disease record identifier
    ageAtDiagnosis: float  # Age in years (or standardized unit)
    diagnosis: OntologyTerm  # Primary diagnosis term

    yearOfDiagnosis: Optional[int] = None  # Year-only representation
    dateOfFirstTreatment: Optional[str] = None  # ISO/RFC3339 timestamp

    pathologyConfirmation: Optional[OntologyTerm] = None  # Confirmatory test
    pathology: Optional[list] = None  # List of pathology descriptors
    imagingProcedureProtocol: Optional[OntologyTerm] = None

    treatment: Optional[List] = None  # Treatment records (untyped list for flexibility)
    tumorMetadata: Optional[Tumors] = None  # Nested tumor characterization

    @field_validator('dateOfFirstTreatment')
    @classmethod
    def validate_datetime(cls, v):
        # Validate RFC3339-compliant timestamp for interoperability
        if not validate_rfc3339(v):
            raise ValueError("Must be a valid RFC3339 date-time (JSON Schema format=date-time)")
        return v

    @field_validator('pathology')
    @classmethod
    def check_pathology(cls, v):
        # Ensure each pathology entry conforms to OntologyTerm structure
        for pathology in v:
            OntologyTerm(**pathology)

    @field_validator('treatment')
    @classmethod
    def check_treatment(cls, v):
        # Validate each treatment entry as ontology-based object
        for treatment in v:
            OntologyTerm(**treatment)


class ImageStudies(BaseModel, extra='forbid'):
    # Imaging study metadata linked to disease context

    def __init__(self, **data) -> None:
        # Clean private attributes before model initialization
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()  # Internal identifier

    imageStudyId: str  # Unique imaging study ID
    disease: Diseases  # Linked disease object

    # Imaging acquisition metadata
    imageModality: OntologyTerm
    imageBodyPart: OntologyTerm
    imageManufacturer: OntologyTerm

    dateOfImageAcquisition: str  # Timestamp of imaging session

    @field_validator('dateOfImageAcquisition')
    @classmethod
    def validate_datetime(cls, v):
        # Ensure imaging date follows RFC3339 standard format
        if not validate_rfc3339(v):
            raise ValueError("Must be a valid RFC3339 date-time (JSON Schema format=date-time)")
        return v


class Patients(BaseModel, extra='forbid'):
    # Top-level patient entity aggregating clinical and imaging data

    def __init__(self, **data) -> None:
        # Remove internal/private fields before schema validation
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    _id: Optional[str] = PrivateAttr()  # Internal DB reference

    patientId: str  # Primary patient identifier
    sex: OntologyTerm  # Biological sex encoded as ontology term

    diseases: Optional[List[Diseases]] = None  # Associated disease records
    imageStudy: Optional[List[ImageStudies]] = None  # Linked imaging studies