import re
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)

from typing import Optional, Union
from beacon.framework.validator.v2_0_0.common import OntologyTerm
from beacon.models.ga4gh.beacon_v2_default_model.validator.non_collections.biosample.beacon_biosample_v2_1_0 import GestationalAge, TimeInterval, Quantity, Age, AgeRange, TypedQuantities
from beacon.models.ga4gh.beacon_v2_default_model.validator.non_collections.individual.beacon_individual_v2_0_0 import Evidence, Ethnicity, GeographicOrigin, Pedigrees, Sex

timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")

class DoseIntervals(BaseModel):
    interval: Union[str,dict]
    quantity: Quantity
    scheduleFrequency: OntologyTerm
    @field_validator('interval')
    @classmethod
    def check_interval(cls, v: Union[str,dict]) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('interval, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('interval, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')

class Diseases(BaseModel):
    ageOfOnset: Optional[Union[str,dict]]=None
    diseaseCode: OntologyTerm
    familyHistory: Optional[bool]=None
    notes: Optional[str]=None
    severity: Optional[OntologyTerm]=None
    stage: Optional[OntologyTerm]=None
    @field_validator('ageOfOnset')
    @classmethod
    @field_validator('ageOfOnset')
    @classmethod
    def check_ageOfOnset(cls, v: Union[str,dict]) -> Union[str,dict]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('ageOfOnset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('ageOfOnset, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            return v
    
class Exposures(BaseModel):
    ageAtExposure: Age
    date: Optional[str] = None
    duration: str
    exposureCode: OntologyTerm
    unit: OntologyTerm
    value: Optional[Union[int, float]] = None

class InterventionsOrProcedures(BaseModel):
    ageAtProcedure: Optional[Union[str,dict]]=None
    bodySite: Optional[OntologyTerm]=None
    dateOfProcedure: Optional[str]=None
    procedureCode: OntologyTerm
    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Union[str,dict]) -> Union[str,dict]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('ageAtProcedure, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            
class Measurement(BaseModel):
    assayCode: OntologyTerm
    date: Optional[str] = None
    measurementValue: Union[Quantity, OntologyTerm, TypedQuantities]
    notes: Optional[str]=None
    observationMoment: Optional[Union[str,dict]]=None
    procedure: Optional[InterventionsOrProcedures] = None
    @field_validator('observationMoment')
    @classmethod
    def check_observationMoment(cls, v: Union[str,dict]) -> Union[str,dict]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('observationMoment, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('observationMoment, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')

class PhenotypicFeatures(BaseModel):
    evidence: Optional[Evidence]=None
    id: Optional[str] = None
    excluded: Optional[bool]=None
    featureType: OntologyTerm
    modifiers: Optional[list[OntologyTerm]]=None
    notes: Optional[str]=None
    onset: Optional[Union[str,dict]]=None
    resolution: Optional[Union[str,dict]]=None
    severity: Optional[OntologyTerm]=None
    @field_validator('onset')
    @classmethod
    def check_onset(cls, v: Union[str,dict]) -> Union[str,dict]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('onset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('onset, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
    @field_validator('resolution')
    @classmethod
    def check_resolution(cls, v: Union[str,dict]) -> Union[str,dict]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
            except Exception as e:
                raise ValueError('resolution, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            for model in (Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm):
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('resolution, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            
class Treatment(BaseModel):
    ageAtOnset: Optional[Age] = None
    cumulativeDose: Optional[Quantity] = None
    doseIntervals: Optional[list[DoseIntervals]] = None
    routeOfAdministration: Optional[OntologyTerm] = None
    treatmentCode: OntologyTerm
    @field_validator('doseIntervals')
    @classmethod
    def check_doseIntervals(cls, v: list) -> list:
        for doseInterval in v:
            DoseIntervals(**doseInterval)
        return v
# TODO: fer que el que es retorna de cada connection sigui una classe de model de beacon a retornar (no un JSON)
class Individual(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    diseases: Optional[list[Diseases]] = None
    ethnicity: Optional[OntologyTerm] = None
    exposures: Optional[list[Exposures]] = None
    geographicOrigin: Optional[OntologyTerm] = None
    id: str
    info: Optional[dict] = None
    interventionsOrProcedures: Optional[list[InterventionsOrProcedures]] = None
    karyotypicSex: Optional[str] = None
    measures: Optional[list[Measurement]]=None
    pedigrees: Optional[list[Pedigrees]] = None
    phenotypicFeatures: Optional[list[PhenotypicFeatures]] = None
    sex: OntologyTerm
    treatments: Optional[list[Treatment]] = None
    @field_validator('karyotypicSex')
    @classmethod
    def check_karyotypic(cls, v: str) -> str:
        karyotypic_values=[
                "UNKNOWN_KARYOTYPE",
                "XX",
                "XY",
                "XO",
                "XXY",
                "XXX",
                "XXYY",
                "XXXY",
                "XXXX",
                "XYY",
                "OTHER_KARYOTYPE"]
        if v not in karyotypic_values:
            raise ValueError('id must be one from {}'.format(karyotypic_values))
        return v