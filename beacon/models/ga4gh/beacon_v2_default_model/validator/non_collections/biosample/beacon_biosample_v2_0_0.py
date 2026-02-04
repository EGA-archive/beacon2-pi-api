import re
import argparse
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)

from typing import Optional, Union, List
from beacon.framework.validator.v2_0_0.common import OntologyTerm

timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")

class Age(BaseModel):
    iso8601duration: Optional[str]=None

class AgeRange(BaseModel):
    end: Optional[Age]=None
    start: Optional[Age]=None

class GestationalAge(BaseModel):
    days: Optional[int] = None
    weeks: int

class TimeInterval(BaseModel):
    end: str
    start: str

class ReferenceRange(BaseModel):
    high: Union[int,float]
    low: Union[int, float]
    unit: OntologyTerm

class Quantity(BaseModel):
    referenceRange: Optional[ReferenceRange] = None
    unit: OntologyTerm
    value: Union[int, float]

class TypedQuantity(BaseModel):
    quantity: Quantity
    quantityType: OntologyTerm

class TypedQuantities(BaseModel):
    typedQuantities: Optional[TypedQuantity]=None

class InterventionsOrProcedures(BaseModel):
    ageAtProcedure: Optional[Union[str,dict]]=None
    bodySite: Optional[OntologyTerm]=None
    dateOfProcedure: Optional[str]=None
    procedureCode: OntologyTerm
    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Optional[Union[str,dict]]) -> Optional[Union[str,dict]]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
                return v
            except Exception as e:
                raise ValueError('ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e))
        elif isinstance(v, dict):
            for model in [Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm]:
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
    def check_observationMoment(cls, v: Optional[Union[str,dict]]) -> Optional[Union[str,dict]]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                timestamp_regex.match(v)
                return v
            except Exception as e:
                raise ValueError('observationMoment, if string, must be Timestamp, getting this error: {}'.format(e))
        elif isinstance(v, dict):
            for model in [Age, AgeRange, GestationalAge, TimeInterval, OntologyTerm]:
                try:
                    model(**v)
                    return v
                except Exception:
                    continue
            raise ValueError('observationMoment, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')

class Biosample(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    biosampleStatus: OntologyTerm
    collectionDate: Optional[str] = None
    collectionMoment: Optional[str] = None
    diagnosticMarkers: Optional[List[OntologyTerm]] = None
    histologicalDiagnosis: Optional[OntologyTerm] = None
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    measurements: Optional[List[Measurement]] = None
    notes: Optional[str]=None
    obtentionProcedure: Optional[InterventionsOrProcedures] = None
    pathologicalStage: Optional[OntologyTerm] = None
    pathologicalTnmFinding: Optional[List] = None
    phenotypicFeatures: Optional[List] = None
    sampleOriginDetail: Optional[OntologyTerm] = None
    sampleOriginType: OntologyTerm
    sampleProcessing: Optional[OntologyTerm] = None
    sampleStorage: Optional[OntologyTerm] = None
    tumorGrade: Optional[OntologyTerm] = None
    tumorProgression: Optional[OntologyTerm] = None