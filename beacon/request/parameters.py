from typing_extensions import Self
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr,
    model_validator
)
from strenum import StrEnum
from typing import List, Optional, Union
from beacon.conf.conf import api_version, default_beacon_granularity
from humps.main import camelize
from aiohttp.web_request import Request
from aiohttp import web
import html
import json
from beacon.logs.logs import log_with_args, LOG
from beacon.request.classes import ErrorClass
from beacon.request.classes import Granularity
from beacon.conf.conf import api_version, beacon_id 

class CamelModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class IncludeResultsetResponses(StrEnum):
    ALL = "ALL",
    HIT = "HIT",
    MISS = "MISS",
    NONE = "NONE"


class Similarity(StrEnum):
    EXACT = "exact",
    HIGH = "high",
    MEDIUM = "medium",
    LOW = "low"


class Operator(StrEnum):
    EQUAL = "=",
    LESS = "<",
    GREATER = ">",
    NOT = "!",
    LESS_EQUAL = "<=",
    GREATER_EQUAL = ">="

class OntologyFilter(CamelModel):
    id: str
    scope: Optional[str] =None
    include_descendant_terms: bool = False
    similarity: Similarity = Similarity.EXACT


class AlphanumericFilter(CamelModel):
    id: str
    value: Union[str, int, List[int]]
    scope: Optional[str] =None
    operator: Operator = Operator.EQUAL


class CustomFilter(CamelModel):
    id: str
    scope: Optional[str] =None


class SchemasPerEntity(CamelModel):
    entityType: Optional[str]
    schema: Optional[str]


class Pagination(CamelModel):
    skip: int = 0
    limit: int = 10


class RequestMeta(CamelModel):
    requestedSchemas: List[SchemasPerEntity] = []
    apiVersion: str = 'v2.0.0'

class SequenceQuery(BaseModel):
    referenceName: Union[str,int]
    start: Union[int,list]
    alternateBases:str
    referenceBases: str
    clinicalRelevance: Optional[str] =None
    mateName: Optional[str] =None
    assemblyId: Optional[str] =None
    datasets: Optional[list]=[]
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId(cls, values):
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            try:
                if values.assemblyId == None:
                    ErrorClass.error_code=400
                    ErrorClass.error_message='if referenceName is just the chromosome: assemblyId parameter is required'
                    raise
                else:
                    pass
            except Exception as e:# pragma: no cover
                raise ValueError
        else:# pragma: no cover
            raise ValueError
    @field_validator('start')
    @classmethod
    def id_must_be_CURIE(cls, v: Union[int,list]) -> Union[int,list]:
        if isinstance(v,list):
            if len(v)>1:
                raise ValueError

class RangeQuery(BaseModel):
    referenceName: Union[str,int]
    start: Union[int,list]
    end: Union[int,list]
    variantType: Optional[str] =None
    alternateBases: Optional[str] =None
    aminoacidChange: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    clinicalRelevance: Optional[str] =None
    mateName: Optional[str] =None
    assemblyId: Optional[str] =None
    datasets: Optional[list]=[]
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_2(cls, values):
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            try:
                if values.assemblyId == None:
                    ErrorClass.error_code=400
                    ErrorClass.error_message='if referenceName is just the chromosome: assemblyId parameter is required'
                    raise
                else:
                    pass
            except Exception as e:# pragma: no cover
                raise ValueError
        start=values.start
        end=values.end
        if isinstance(start, list):
            start = start[0]
        if isinstance(end, list):
            end = end [0]
        if int(start) > int(end):
            ErrorClass.error_code=400
            ErrorClass.error_message="start's value can not be greater than end's value"
            raise



class GeneIdQuery(BaseModel):
    geneId: str
    variantType: Optional[str] =None
    alternateBases: Optional[str] =None
    aminoacidChange: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    datasets: Optional[list]=[]

class BracketQuery(BaseModel):
    referenceName: Union[str,int]
    start: list
    end: list
    variantType: Optional[str] =None
    clinicalRelevance: Optional[str] =None
    mateName: Optional[str] =None
    assemblyId: Optional[str] =None
    datasets: Optional[list]=[]
    @field_validator('start')
    @classmethod
    def start_must_be_array_of_integers(cls, v: list) -> list:
        for num in v:# pragma: no cover
            if isinstance(num, int):
                pass
            else:
                raise ValueError
    @field_validator('end')
    @classmethod
    def end_must_be_array_of_integers(cls, v: list) -> list:
        for num in v:# pragma: no cover
            if isinstance(num, int):
                pass
            else:
                raise ValueError
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_3(cls, values):
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            try:
                if values.assemblyId == None:
                    ErrorClass.error_code=400
                    ErrorClass.error_message='if referenceName is just the chromosome: assemblyId parameter is required'
                    raise
                else:
                    pass
            except Exception as e:# pragma: no cover
                raise ValueError
        else:# pragma: no cover
            raise ValueError

class GenomicAlleleQuery(BaseModel):
    genomicAlleleShortForm: str
    datasets: Optional[list]=[]

class AminoacidChangeQuery(BaseModel):
    aminoacidChange: str
    geneId: str
    datasets: Optional[list]=[]

class DatasetsRequested(BaseModel):
    datasets: list[str]

class RequestQuery(CamelModel):
    filters: List[dict] = []
    includeResultsetResponses: IncludeResultsetResponses = IncludeResultsetResponses.HIT
    pagination: Pagination = Pagination()
    requestParameters: Optional[Union[SequenceQuery,RangeQuery,BracketQuery,AminoacidChangeQuery,GeneIdQuery,GenomicAlleleQuery,DatasetsRequested]] = {}
    testMode: bool = False
    requestedGranularity: Granularity = Granularity(default_beacon_granularity)

class RequestParams(CamelModel):
    meta: RequestMeta = RequestMeta()
    query: RequestQuery = RequestQuery()

    def from_request(self, request: Request) -> Self:
        try:
            self.meta.apiVersion = request["meta"]["apiVersion"]
        except Exception:
            pass
        try:
            self.meta.requestedSchemas = request["meta"]["requestedSchemas"]
        except Exception:
            pass
        try:
            self.query.requestParameters = request["query"]["requestParameters"]
        except Exception:
            pass
        try:
            self.query.filters = request["query"]["filters"]
        except Exception:
            pass
        return self
        

    def summary(self):
        try:
            return {
                "apiVersion": self.meta.apiVersion,
                "requestedSchemas": self.meta.requestedSchemas,
                "filters": self.query.filters,
                "requestParameters": self.query.requestParameters,
                "includeResultsetResponses": self.query.includeResultsetResponses,
                "pagination": self.query.pagination.dict(),
                "requestedGranularity": self.query.requestedGranularity,
                "testMode": self.query.testMode
            }
        except Exception as e:# pragma: no cover
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise
