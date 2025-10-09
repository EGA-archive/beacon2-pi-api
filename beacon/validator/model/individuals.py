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

class OntologyTerm(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class Age(BaseModel, extra='forbid'):
    iso8601duration: str

class AgeRange(BaseModel, extra='forbid'):
    end: Age
    start: Age

class GestationalAge(BaseModel, extra='forbid'):
    days: Optional[int] = None
    weeks: int

class TimeInterval(BaseModel, extra='forbid'):
    end: str
    start: str

class ReferenceRange(BaseModel, extra='forbid'):
    high: Union[int,float]
    low: Union[int, float]
    unit: OntologyTerm

class Quantity(BaseModel, extra='forbid'):
    referenceRange: Optional[ReferenceRange] = None
    unit: OntologyTerm
    value: Union[int, float]

class TypedQuantity(BaseModel, extra='forbid'):
    quantity: Quantity
    quantityType: OntologyTerm

class Members(BaseModel, extra='forbid'):
    affected: bool
    memberId: str
    role: OntologyTerm

class Reference(BaseModel, extra='forbid'):
    id: Optional[str] = None
    notes: Optional[str] = None
    reference: Optional[str] = None

class Evidence(BaseModel, extra='forbid'):
    evidenceCode: OntologyTerm
    reference: Optional[Reference] = None

class DoseIntervals(BaseModel, extra='forbid'):
    interval: Union[str,dict]
    quantity: Quantity
    scheduleFrequency: OntologyTerm
    @field_validator('interval')
    @classmethod
    def check_interval(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('interval, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
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
                raise ValueError('interval, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')

class Diseases(BaseModel, extra='forbid'):
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
            return v.title()
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

class Ethnicity(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    
class Exposures(BaseModel, extra='forbid'):
    ageAtExposure: Age
    date: Optional[str] = None
    duration: str
    exposureCode: OntologyTerm
    unit: OntologyTerm
    value: Optional[Union[int, float]] = None

class GeographicOrigin(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class InterventionsOrProcedures(BaseModel, extra='forbid'):
    ageAtProcedure: Optional[Union[str,dict]]=None
    bodySite: Optional[OntologyTerm]=None
    dateOfProcedure: Optional[str]=None
    procedureCode: OntologyTerm
    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
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
                raise ValueError('ageAtProcedure, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            
class Measurement(BaseModel, extra='forbid'):
    assayCode: OntologyTerm
    date: Optional[str] = None
    measurementValue: Union[Quantity, OntologyTerm, list]
    notes: Optional[str]=None
    observationMoment: Optional[Union[str,dict]]=None
    procedure: Optional[dict] = None
    @field_validator('measurementValue')
    @classmethod
    def check_measurementValue(cls, v: Union[Quantity, OntologyTerm, list]= Field(union_mode='left_to_right')) -> Union[Quantity, OntologyTerm, list]:
        if isinstance(v, list):
            for measurement in v:
                try:
                    Quantity(**measurement)
                except Exception:
                    TypedQuantity(**measurement)
    @field_validator('observationMoment')
    @classmethod
    def check_observationMoment(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('observationMoment, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
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
                raise ValueError('observationMoment, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
    @field_validator('procedure')
    @classmethod
    def check_procedure(cls, v: dict) -> dict:
        InterventionsOrProcedures(**v)

class Pedigrees(BaseModel, extra='forbid'):
    disease: Diseases
    id: str
    members: list
    numSubjects: Optional[int] = None
    @field_validator('members')
    @classmethod
    def check_members(cls, v: list) -> list:
        for member in v:
            Members(**member)

class PhenotypicFeatures(BaseModel, extra='forbid'):
    evidence: Optional[dict]=None
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
    @field_validator('onset')
    @classmethod
    def check_onset(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('onset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
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
    @field_validator('resolution')
    @classmethod
    def check_resolution(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('resolution, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
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

class Sex(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()
            
class Treatment(BaseModel, extra='forbid'):
    ageAtOnset: Optional[Age] = None
    cumulativeDose: Optional[Quantity] = None
    doseIntervals: Optional[list] = None
    routeOfAdministration: Optional[OntologyTerm] = None
    treatmentCode: OntologyTerm
    @field_validator('doseIntervals')
    @classmethod
    def check_doseIntervals(cls, v: list) -> list:
        for doseInterval in v:
            DoseIntervals(**doseInterval)

class Individuals(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    diseases: Optional[list] = None
    ethnicity: Optional[dict] = None
    exposures: Optional[list] = None
    geographicOrigin: Optional[dict] = None
    id: str
    info: Optional[dict] = None
    interventionsOrProcedures: Optional[list] = None
    karyotypicSex: Optional[str] = None
    measures: Optional[list]=None
    pedigrees: Optional[list] = None
    phenotypicFeatures: Optional[list] = None
    sex: Sex
    treatments: Optional[list] = None
    @field_validator('ethnicity')
    @classmethod
    def check_ethnicity(cls, v: dict) -> dict:
        Ethnicity(**v)
    @field_validator('diseases')
    @classmethod
    def check_diseases(cls, v: list) -> list:
        for disease in v:
            Diseases(**disease)
    @field_validator('exposures')
    @classmethod
    def check_exposures(cls, v: list) -> list:
        for exposure in v:
            Exposures(**exposure)
    @field_validator('geographicOrigin')
    @classmethod
    def check_geographicOrigin(cls, v: dict) -> dict:
        GeographicOrigin(**v)
    @field_validator('interventionsOrProcedures')
    @classmethod
    def check_interventions(cls, v: list) -> list:
        for procedure in v:
            InterventionsOrProcedures(**procedure)
    @field_validator('measures')
    @classmethod
    def check_measures(cls, v: list) -> list:
        for measure in v:
            Measurement(**measure)
    @field_validator('pedigrees')
    @classmethod
    def check_pedigrees(cls, v: list) -> list:
        for pedigree in v:
            Pedigrees(**pedigree)
    @field_validator('phenotypicFeatures')
    @classmethod
    def check_phenotypicFeatures(cls, v: list) -> list:
        for phenotypicFeature in v:
            PhenotypicFeatures(**phenotypicFeature)
    @field_validator('treatments')
    @classmethod
    def check_treatments(cls, v: list) -> list:
        for treatment in v:
            Treatment(**treatment)