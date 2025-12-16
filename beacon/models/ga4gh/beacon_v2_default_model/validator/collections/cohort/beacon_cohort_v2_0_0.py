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
from beacon.framework.validator.v2_0_0.common import OntologyTerm

from typing import Optional, Union

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

class EventTimeline(BaseModel):
    end: Optional[str]=None
    start: Optional[str]=None
    @field_validator('end')
    @classmethod
    def check_end(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('end, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
    @field_validator('start')
    @classmethod
    def check_start(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('start, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        

class Diseases(BaseModel):
    ageOfOnset: Optional[Union[str,dict]]=None
    diseaseCode: OntologyTerm
    familyHistory: Optional[bool]=None
    notes: Optional[str]=None
    severity: Optional[OntologyTerm]=None
    stage: Optional[OntologyTerm]=None
    @field_validator('ageOfOnset')
    @classmethod
    def check_ageOfOnset(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('ageOfOnset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('ageOfOnset, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            return v
            
class Ethnicity(BaseModel):
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
    
class Sex(BaseModel):
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
    
class Reference(BaseModel):
    id: Optional[str] = None
    notes: Optional[str] = None
    reference: Optional[str] = None
    
class Evidence(BaseModel):
    evidenceCode: OntologyTerm
    reference: Optional[Reference] = None

class PhenotypicFeatures(BaseModel):
    evidence: Optional[Evidence]=None
    id: Optional[str] = None
    excluded: Optional[bool]=None
    featureType: OntologyTerm
    modifiers: Optional[list]=None
    notes: Optional[str]=None
    onset: Optional[Union[str,dict]]=None
    resolution: Optional[Union[str,dict]]=None
    severity: Optional[OntologyTerm]=None
    @field_validator('evidence')
    @classmethod
    def check_evidence(cls, v: dict) -> dict:
        Evidence(**v)
    @field_validator('modifiers')
    @classmethod
    def check_modifiers(cls, v: list) -> list:
        for modifier in v:
            OntologyTerm(**modifier)
        return v
    @field_validator('onset')
    @classmethod
    def check_onset(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('onset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('onset, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            return v
    @field_validator('resolution')
    @classmethod
    def check_resolution(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('resolution, if string, must be Timestamp, getting this error: {}'.format(e))
            return v
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('resolution, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            return v

class CohortCriteria(BaseModel):
    ageRange: Optional[AgeRange]=None
    diseaseConditions: Optional[list]=None
    ethnicities: Optional[list]=None
    genders: Optional[list]=None
    locations: Optional[list]=None
    phenotypicConditions: Optional[list]=None
    @field_validator('diseaseConditions')
    @classmethod
    def check_diseaseConditions(cls, v: list) -> list:
        for disease in v:
            Diseases(**disease)
        return v
    @field_validator('ethnicities')
    @classmethod
    def check_ethnicities(cls, v: list) -> list:
        for ethnicity in v:
            Ethnicity(**ethnicity)
        return v
    @field_validator('genders')
    @classmethod
    def check_genders(cls, v: list) -> list:
        for gender in v:
            Sex(**gender)
        return v
    @field_validator('locations')
    @classmethod
    def check_locations(cls, v: list) -> list:
        for location in v:
            OntologyTerm(**location)
        return v
    @field_validator('phenotypicConditions')
    @classmethod
    def check_phenotypicConditions(cls, v: list) -> list:
        for phenotypicCondition in v:
            PhenotypicFeatures(**phenotypicCondition)
        return v

class DataAvailabilityAndDistribution(BaseModel):
    availability: bool
    availabilityCount: Optional[int]=None
    distribution: Optional[dict]=None
            
class CollectionEvent(BaseModel):
    eventAgeRange: Optional[DataAvailabilityAndDistribution]=None
    eventCases: Optional[int] = None
    eventControls: Optional[int] = None
    eventDataTypes: Optional[DataAvailabilityAndDistribution]=None
    eventDate: Optional[str]=None
    eventDiseases: Optional[DataAvailabilityAndDistribution]=None
    eventEthnicities: Optional[DataAvailabilityAndDistribution]=None
    eventGenders: Optional[DataAvailabilityAndDistribution]=None
    eventLocations: Optional[DataAvailabilityAndDistribution]=None
    eventNum: Optional[int] = None
    eventPhenotypes: Optional[DataAvailabilityAndDistribution]=None
    eventSize: Optional[int] = None
    eventTimeline: Optional[EventTimeline] = None
    @field_validator('eventDate')
    @classmethod
    def check_eventDate(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('eventDate, if string, must be Timestamp, getting this error: {}'.format(e))
            return v

class Cohort(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    cohortDataTypes: Optional[list] = None
    cohortDesign: Optional[OntologyTerm] = None
    cohortSize: Optional[int] = None
    cohortType: str
    collectionEvents: Optional[list] = None
    exclusionCriteria: Optional[CohortCriteria] = None
    id: str
    inclusionCriteria: Optional[CohortCriteria] = None
    name: str
    @field_validator('cohortDataTypes')
    @classmethod
    def check_cohortDataTypes(cls, v: list) -> list:
        for cohortDataType in v:
            OntologyTerm(**cohortDataType)
        return v
    @field_validator('collectionEvents')
    @classmethod
    def check_collectionEvents(cls, v: list) -> list:
        for collectionEvent in v:
            CollectionEvent(**collectionEvent)
        return v