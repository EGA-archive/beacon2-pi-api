import re
from pydantic import (
    BaseModel,
    field_validator,
    PrivateAttr
)

from typing import Optional, Union, List
from beacon.framework.validator.v2_0_0.common import OntologyTerm
# Regex used to validate timestamp-like strings in multiple clinical fields.
# Expected format resembles: "...DD/Mon/YYYY:HH:MM:SS"
timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")


class Age(BaseModel):
    # Age represented in ISO-8601 duration format (e.g., P30Y, P2M)
    iso8601duration: Optional[str] = None


class AgeRange(BaseModel):
    # Represents an age interval using structured Age objects
    end: Optional[Age] = None
    start: Optional[Age] = None


class GestationalAge(BaseModel):
    # Pregnancy age representation
    days: Optional[int] = None
    weeks: int


class TimeInterval(BaseModel):
    # Generic time interval using raw string boundaries
    end: str
    start: str


class ReferenceRange(BaseModel):
    # Clinical reference interval for quantitative measurements
    high: Union[int, float]
    low: Union[int, float]

    # Unit of measurement defined via ontology term
    unit: OntologyTerm


class Quantity(BaseModel):
    # Optional reference range for interpreting numeric value
    referenceRange: Optional[ReferenceRange] = None

    # Unit of measurement (ontology-driven)
    unit: OntologyTerm

    # Actual measured value (numeric)
    value: Union[int, float]


class TypedQuantity(BaseModel):
    # Wrapper that associates a quantity with its semantic type
    quantity: Quantity
    quantityType: OntologyTerm


class TypedQuantities(BaseModel):
    # Container for optional typed quantity payload
    typedQuantities: Optional[TypedQuantity] = None


class InterventionsOrProcedures(BaseModel):
    # Age at which a procedure occurred (multiple representations allowed)
    ageAtProcedure: Optional[Union[str, dict]] = None

    # Anatomical site of procedure
    bodySite: Optional[OntologyTerm] = None

    # Raw procedure date string (non-normalized format allowed)
    dateOfProcedure: Optional[str] = None

    # Required ontology-coded procedure identifier
    procedureCode: OntologyTerm

    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Optional[Union[str, dict]]) -> Optional[Union[str, dict]]:
        # Accept null values without validation
        if v is None:
            return v

        # Case 1: timestamp string validation
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
                return v
            except Exception as e:
                raise ValueError(
                    'ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e)
                )

        # Case 2: structured object validation using multiple allowed schemas
        elif isinstance(v, dict):
            for model in [Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm]:
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            # If none of the models match, validation fails
            raise ValueError(
                'ageAtProcedure, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Measurement(BaseModel):
    # Ontology-coded assay identifier for the measurement
    assayCode: OntologyTerm

    # Optional date of measurement acquisition
    date: Optional[str] = None

    # Measurement value can be numeric, ontology term, or typed structure
    measurementValue: Union[Quantity, OntologyTerm, TypedQuantities]

    # Optional free-text annotation
    notes: Optional[str] = None

    # Moment of observation (timestamp string or structured object)
    observationMoment: Optional[Union[str, dict]] = None

    # Optional associated procedure that produced the measurement
    procedure: Optional[InterventionsOrProcedures] = None

    @field_validator('observationMoment')
    @classmethod
    def check_observationMoment(cls, v: Optional[Union[str, dict]]) -> Optional[Union[str, dict]]:
        # Allow missing observation moment
        if v is None:
            return v

        # Validate timestamp string format
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
                return v
            except Exception as e:
                raise ValueError(
                    'observationMoment, if string, must be Timestamp, getting this error: {}'.format(e)
                )

        # Validate structured representations of time/age
        elif isinstance(v, dict):
            for model in [Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm]:
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'observationMoment, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Biosample(BaseModel):
    # Custom initializer used to extract private attributes before validation
    def __init__(self, **data) -> None:
        # Extract private attributes explicitly before BaseModel processing
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    # Internal identifier not exposed as standard field
    _id: Optional[str] = PrivateAttr()

    # Required biosample status (ontology-driven)
    biosampleStatus: OntologyTerm

    # Collection metadata (date and/or structured moment)
    collectionDate: Optional[str] = None
    collectionMoment: Optional[str] = None

    # Diagnostic annotations
    diagnosticMarkers: Optional[List[OntologyTerm]] = None
    histologicalDiagnosis: Optional[OntologyTerm] = None

    # Primary identifier
    id: str

    # Link to associated individual subject
    individualId: Optional[str] = None

    # Flexible metadata container
    info: Optional[dict] = None

    # List of clinical or laboratory measurements
    measurements: Optional[List[Measurement]] = None

    # Free-text notes
    notes: Optional[str] = None

    # Procedure used for sample collection
    obtentionProcedure: Optional[InterventionsOrProcedures] = None

    # Cancer staging / pathology metadata
    pathologicalStage: Optional[OntologyTerm] = None
    pathologicalTnmFinding: Optional[List] = None

    # Phenotypic annotations associated with sample
    phenotypicFeatures: Optional[List] = None

    # Origin classification of sample (e.g., tissue type)
    sampleOriginDetail: Optional[OntologyTerm] = None

    # Required classification of sample origin
    sampleOriginType: OntologyTerm

    # Processing and storage metadata
    sampleProcessing: Optional[OntologyTerm] = None
    sampleStorage: Optional[OntologyTerm] = None

    # Tumor-related grading and progression descriptors
    tumorGrade: Optional[OntologyTerm] = None
    tumorProgression: Optional[OntologyTerm] = None