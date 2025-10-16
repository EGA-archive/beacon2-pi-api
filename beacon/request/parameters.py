from typing_extensions import Self
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    Field
)
from strenum import StrEnum
from typing import List, Optional, Union
from beacon.conf.conf import default_beacon_granularity
from humps.main import camelize
from aiohttp.web_request import Request
from aiohttp import web
from beacon.request.classes import Granularity
from beacon.logs.logs import LOG
import re

class CamelModel(BaseModel, extra='forbid'):
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

class OntologyFilter(CamelModel, extra='forbid'):
    id: str
    scope: Optional[str] =None
    includeDescendantTerms: Optional[bool] = True
    similarity: Optional[Similarity] = Similarity.EXACT
    @field_validator('id')
    @classmethod
    def id__ontology_filter_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v

class AlphanumericFilter(CamelModel, extra='forbid'):
    id: str
    value: Union[str, int, List[int]]
    scope: Optional[str] =None
    operator: Operator = Operator.EQUAL
    @field_validator('id')
    @classmethod
    def id__alphanumeric_filter_must_not_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            raise ValueError('id must be a schema field reference, not a CURIE')
        return v


class CustomFilter(CamelModel, extra='forbid'):
    id: str
    scope: Optional[str] =None

class SchemasPerEntity(CamelModel, extra='forbid'):
    entityType: Optional[str] = None
    schema: Optional[str] = None


class Pagination(CamelModel, extra='forbid'):
    skip: int = 0
    limit: int = 10
    currentPage: Optional[str] = None
    nexttPage: Optional[str] = None
    previousPage: Optional[str] = None


class RequestMeta(CamelModel, extra='forbid'):
    requestedSchemas: Optional[List[SchemasPerEntity]] = []
    apiVersion: str = 'Not provided' # TODO: add supported schemas parsing, by default,

class SequenceQuery(BaseModel, extra='forbid'):
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
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            if values.assemblyId == None:
                raise ValueError('if referenceName is just the chromosome: assemblyId parameter is required')
        else:
            raise ValueError('referenceName must be a number between 1-24, or a string with X, Y, MT or all the previous mentioned values with chr at the beginning')
    @field_validator('start')
    @classmethod
    def id_must_be_CURIE(cls, v: Union[int,list]) -> Union[int,list]:
        if isinstance(v,list):
            if len(v)>1:
                raise ValueError('start can only have one item in the array')

class RangeQuery(BaseModel, extra='forbid'):
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
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            if values.assemblyId == None:
                raise ValueError('if referenceName is just the chromosome: assemblyId parameter is required')
        else:
            raise ValueError('referenceName must be a number between 1-24, or a string with X, Y, MT or all the previous mentioned values with chr at the beginning')
        start=values.start
        end=values.end
        if isinstance(start, list):
            start = start[0]
        if isinstance(end, list):
            end = end [0]
        if int(start) > int(end):
            raise ValueError("start's value can not be greater than end's value")



class GeneIdQuery(BaseModel, extra='forbid'):
    geneId: str
    variantType: Optional[str] =None
    alternateBases: Optional[str] =None
    aminoacidChange: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    datasets: Optional[list]=[]

class BracketQuery(BaseModel, extra='forbid'):
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
        new_list=[]
        for num in v:
            if isinstance(num, int):
                new_list.append(num)
            elif isinstance(num, str):
                try:
                    new_list.append(str(num))
                except Exception:
                    raise ValueError('start parameter must be an array of integers')
        return new_list
    @field_validator('end')
    @classmethod
    def end_must_be_array_of_integers(cls, v: list) -> list:
        new_list=[]
        for num in v:
            if isinstance(num, int):
                new_list.append(num)
            elif isinstance(num, str):
                try:
                    new_list.append(str(num))
                except Exception:
                    raise ValueError('end parameter must be an array of integers')
        return new_list

    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_3(cls, values):
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            if values.assemblyId == None:
                raise ValueError('if referenceName is just the chromosome: assemblyId parameter is required')
        else:
            raise ValueError('referenceName must be a number between 1-24, or a string with X, Y, MT or all the previous mentioned values with chr at the beginning')

class GenomicAlleleQuery(BaseModel, extra='forbid'):
    genomicAlleleShortForm: str
    datasets: Optional[list]=[]

class AminoacidChangeQuery(BaseModel, extra='forbid'):
    aminoacidChange: str
    geneId: str
    datasets: Optional[list]=[]

class DatasetsRequested(BaseModel, extra='forbid'):
    datasets: list[str]

class RequestQuery(CamelModel, extra='forbid'):
    filters: List[Union[AlphanumericFilter,OntologyFilter,CustomFilter]] = []
    includeResultsetResponses: IncludeResultsetResponses = IncludeResultsetResponses.HIT
    pagination: Pagination = Pagination()
    requestParameters: Union[SequenceQuery,RangeQuery,BracketQuery,AminoacidChangeQuery,GeneIdQuery,GenomicAlleleQuery,DatasetsRequested] = {}
    testMode: bool = False
    requestedGranularity: Granularity = Granularity(default_beacon_granularity)
    @field_validator('requestedGranularity')
    @classmethod
    def requestedGranularity_must_be_boolean_count_record(cls, v: str) -> str:
        if v not in ['boolean', 'count', 'record']:
            raise ValueError('requestedGranularity must be one between boolean, count, record')
        return v
    @field_validator('includeResultsetResponses')
    @classmethod
    def includeResultsetResponses_is_correct(cls, v: str) -> str:
        if v not in ['HIT', 'MISS', 'ALL', 'NONE']:
            raise ValueError('includeResultsetResponses must be one between HIT, MISS, ALL, NONE')
        return v

class RequestParams(CamelModel, extra='forbid'):
    meta: RequestMeta = RequestMeta()
    query: RequestQuery = RequestQuery()

    def from_request(self, request: Request) -> Self:
        '''
        Return an instance of RequestParams class and also trigger the initialistion of the ones that belong to Union or List subclasses.
        '''
        try:
            self.query.filters = request["query"]["filters"]
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
        return self
        

    def summary(self):
        "Return a summary of all the query parameters from the request in a json format to be returnend in recieved request summary."
        return {
            "apiVersion": self.meta.apiVersion,
            "requestedSchemas": self.meta.requestedSchemas,
            "filters": [filtering_term["id"] for filtering_term in self.query.filters],
            "requestParameters": self.query.requestParameters,
            "includeResultsetResponses": self.query.includeResultsetResponses,
            "pagination": self.query.pagination.dict(),
            "requestedGranularity": self.query.requestedGranularity,
            "testMode": self.query.testMode
        }
