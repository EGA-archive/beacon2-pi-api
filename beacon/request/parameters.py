from typing_extensions import Self
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    Field
)
from strenum import StrEnum
from typing import List, Optional, Union
from beacon.conf.conf_override import config
from aiohttp.web_request import Request
from beacon.request.classes import Granularity, CamelModel, IncludeResultsetResponses
from beacon.request.filters import AlphanumericFilter, OntologyFilter, CustomFilter

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
    apiVersion: str = 'Not provided'

class BV2alleleRequest(BaseModel, extra='forbid'):
    referenceName: Union[str,int]
    start: list[int]
    alternateBases:str
    referenceBases: str
    assemblyId: Optional[str] =None
    datasets: Optional[list]=[]
    requestProfileId: str
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId(cls, values):
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            if values.assemblyId == None:
                raise ValueError('if referenceName is just the chromosome: assemblyId parameter is required')
        else:
            raise ValueError('referenceName must be a number between 1-24, or a string with X, Y, MT or all the previous mentioned values with chr at the beginning')
        start=values.start
        if isinstance(start, list):
            start = start[0]
        if values.requestProfileId != 'BV2alleleRequest':
            raise ValueError('requestProfileId has to be BV2alleleRequest with these combination of parameters')

class BV2rangeRequest(BaseModel, extra='forbid'):
    referenceName: str
    start: list[int]
    end: list[int]
    variantType: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    assemblyId: Optional[str] =None
    datasets: Optional[list]=[]
    requestProfileId: str
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
        if values.requestProfileId != 'BV2rangeRequest':
            raise ValueError('requestProfileId has to be BV2rangeRequest with these combination of parameters')

class GeneIdQuery(BaseModel, extra='forbid'):
    geneId: str
    variantType: Optional[str] =None
    alternateBases: Optional[str] =None
    aminoacidChange: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    datasets: Optional[list]=[]

class BV2bracketRequest(BaseModel, extra='forbid'):
    referenceName: str
    start: list[int]
    end: list[int]
    variantType: Optional[str] =None
    assemblyId: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None
    requestProfileId: str
    datasets: Optional[list]=[]
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_3(cls, values):
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
        if values.requestProfileId != 'BV2bracketRequest':
            raise ValueError('requestProfileId has to be BV2bracketRequest with these combination of parameters')

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
    filters: List[Union[AlphanumericFilter,OntologyFilter,CustomFilter,List[Union[AlphanumericFilter,OntologyFilter,CustomFilter]]]] = []
    includeResultsetResponses: IncludeResultsetResponses = IncludeResultsetResponses.HIT
    pagination: Pagination = Pagination()
    requestParameters: Union[BV2alleleRequest,BV2rangeRequest,BV2bracketRequest,AminoacidChangeQuery,GeneIdQuery,GenomicAlleleQuery,DatasetsRequested] = {}
    testMode: bool = False
    requestedGranularity: Granularity = Granularity(config.default_beacon_granularity)
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
            "filters": [
                    item["id"]
                    for filtering_term in self.query.filters
                    for item in (filtering_term if isinstance(filtering_term, list) else [filtering_term])
                ],
            "requestParameters": self.query.requestParameters,
            "includeResultsetResponses": self.query.includeResultsetResponses,
            "pagination": self.query.pagination.dict(),
            "requestedGranularity": self.query.requestedGranularity,
            "testMode": self.query.testMode
        }
