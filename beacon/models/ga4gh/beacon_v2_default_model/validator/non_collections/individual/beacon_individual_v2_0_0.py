import re
from pydantic import (
    BaseModel,
    field_validator,
    PrivateAttr
)

from typing import Optional, Union
from beacon.framework.validator.v2_0_0.common import OntologyTerm
from beacon.models.ga4gh.beacon_v2_default_model.validator.non_collections.biosample.beacon_biosample_v2_1_0 import GestationalAge, TimeInterval, Quantity, Age, AgeRange, TypedQuantities
# Regex used across multiple clinical timestamp-like fields.
# Expected format resembles: "...DD/Mon/YYYY:HH:MM:SS"
timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")


class Members(BaseModel):
    # Participant/member within pedigree or group context
    affected: bool
    memberId: str
    role: OntologyTerm  # role is ontology-driven (e.g., proband, sibling)


class Reference(BaseModel):
    # Generic literature or evidence reference object
    id: Optional[str] = None
    notes: Optional[str] = None
    reference: Optional[str] = None


class Evidence(BaseModel):
    # Evidence supporting an annotation or phenotype association
    evidenceCode: OntologyTerm
    reference: Optional[Reference] = None


class DoseIntervals(BaseModel):
    # Represents dosing schedule information for treatments or exposures
    interval: Union[str, dict]
    quantity: Quantity
    scheduleFrequency: OntologyTerm

    @field_validator('interval')
    @classmethod
    def check_interval(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Interval can be either timestamp-like string or structured object
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'interval, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured interval: validated against known temporal models
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'interval, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Diseases(BaseModel):
    # Clinical disease annotation for an individual
    ageOfOnset: Optional[Union[str, dict]] = None
    diseaseCode: OntologyTerm
    familyHistory: Optional[bool] = None
    notes: Optional[str] = None
    severity: Optional[OntologyTerm] = None
    stage: Optional[OntologyTerm] = None

    @field_validator('ageOfOnset')
    @classmethod
    def check_ageOfOnset(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Optional field: allows missing value
        if v is None:
            return v

        # String-based timestamp validation
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'ageOfOnset, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured temporal/ontology-based representation
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'ageOfOnset, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Ethnicity(BaseModel):
    # Ethnicity descriptor using CURIE-style identifier
    id: str
    label: Optional[str] = None

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensure CURIE format (prefix:value)
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v


class Exposures(BaseModel):
    # Environmental or clinical exposure record
    ageAtExposure: Age
    date: Optional[str] = None
    duration: str
    exposureCode: OntologyTerm
    unit: OntologyTerm
    value: Optional[Union[int, float]] = None


class GeographicOrigin(BaseModel):
    # Geographic origin descriptor (ontology-linked)
    id: str
    label: Optional[str] = None

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # Ensure identifier follows CURIE format
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v


class InterventionsOrProcedures(BaseModel):
    # Clinical procedure or intervention record
    ageAtProcedure: Optional[Union[str, dict]] = None
    bodySite: Optional[OntologyTerm] = None
    dateOfProcedure: Optional[str] = None
    procedureCode: OntologyTerm

    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Allow missing values
        if v is None:
            return v

        # Timestamp-based representation
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured temporal representation
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'ageAtProcedure, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Measurement(BaseModel):
    # Clinical or laboratory measurement record
    assayCode: OntologyTerm
    date: Optional[str] = None
    measurementValue: Union[Quantity, OntologyTerm, TypedQuantities]
    notes: Optional[str] = None
    observationMoment: Optional[Union[str, dict]] = None
    procedure: Optional[InterventionsOrProcedures] = None

    @field_validator('observationMoment')
    @classmethod
    def check_observationMoment(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Allow missing observation moment
        if v is None:
            return v

        # Timestamp validation path
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'observationMoment, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured temporal representation validation
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'observationMoment, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Pedigrees(BaseModel):
    # Family pedigree structure linking multiple individuals
    disease: Diseases
    id: str
    members: list
    numSubjects: Optional[int] = None

    @field_validator('members')
    @classmethod
    def check_members(cls, v: list) -> list:
        # Validate each pedigree member structure
        for member in v:
            Members(**member)


class PhenotypicFeatures(BaseModel):
    # Phenotype annotations for an individual
    evidence: Optional[Evidence] = None
    id: Optional[str] = None
    excluded: Optional[bool] = None
    featureType: OntologyTerm
    modifiers: Optional[list[OntologyTerm]] = None
    notes: Optional[str] = None
    onset: Optional[Union[str, dict]] = None
    resolution: Optional[Union[str, dict]] = None
    severity: Optional[OntologyTerm] = None

    @field_validator('onset')
    @classmethod
    def check_onset(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Optional onset of phenotype
        if v is None:
            return v

        # Timestamp-based onset
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'onset, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured onset representation
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'onset, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )

    @field_validator('resolution')
    @classmethod
    def check_resolution(cls, v: Union[str, dict]) -> Union[str, dict]:
        # Optional resolution of phenotype
        if v is None:
            return v

        # Timestamp-based resolution
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError(
                    'resolution, if string, must be Timestamp, getting this error: {}'.format(e)
                )
            return v

        # Structured resolution representation
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue

            raise ValueError(
                'resolution, if object, must be any format possible between '
                'age, ageRange, gestationalAge, timeInterval or OntologyTerm'
            )


class Sex(BaseModel):
    # Biological sex classification using CURIE identifier
    id: str
    label: Optional[str] = None

    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        # CURIE format validation
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v


class Treatment(BaseModel):
    # Therapeutic intervention record
    ageAtOnset: Optional[Age] = None
    cumulativeDose: Optional[Quantity] = None
    doseIntervals: Optional[list[DoseIntervals]] = None
    routeOfAdministration: Optional[OntologyTerm] = None
    treatmentCode: OntologyTerm

    @field_validator('doseIntervals')
    @classmethod
    def check_doseIntervals(cls, v: list) -> list:
        # Validate nested dosing schedule structure
        for doseInterval in v:
            DoseIntervals(**doseInterval)
        return v


class Individual(BaseModel):
    # Core individual/subject entity in clinical dataset
    def __init__(self, **data) -> None:
        # Extract private attributes before BaseModel validation
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)

    # Internal identifier (not exposed as standard field)
    _id: Optional[str] = PrivateAttr()

    # Clinical and demographic attributes
    diseases: Optional[list[Diseases]] = None
    ethnicity: Optional[OntologyTerm] = None
    exposures: Optional[list[Exposures]] = None
    geographicOrigin: Optional[OntologyTerm] = None
    id: str
    info: Optional[dict] = None

    # Clinical procedures and measurements
    interventionsOrProcedures: Optional[list[InterventionsOrProcedures]] = None
    measures: Optional[list[Measurement]] = None
    treatments: Optional[list[Treatment]] = None

    # Family and phenotype information
    pedigrees: Optional[list[Pedigrees]] = None
    phenotypicFeatures: Optional[list[PhenotypicFeatures]] = None

    # Sex and karyotype information
    sex: OntologyTerm
    karyotypicSex: Optional[str] = None

    @field_validator('karyotypicSex')
    @classmethod
    def check_karyotypic(cls, v: str) -> str:
        # Allowed karyotype values for validation
        karyotypic_values = [
            "UNKNOWN_KARYOTYPE", "XX", "XY", "XO", "XXY", "XXX",
            "XXYY", "XXXY", "XXXX", "XYY", "OTHER_KARYOTYPE"
        ]

        if v not in karyotypic_values:
            raise ValueError('id must be one from {}'.format(karyotypic_values))
        return v