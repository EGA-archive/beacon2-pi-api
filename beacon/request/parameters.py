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
from beacon.conf.conf import api_version, max_beacon_granularity
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


class Pagination(CamelModel):
    skip: int = 0
    limit: int = 10


class RequestMeta(CamelModel):
    requested_schemas: List[str] = []
    api_version: str = api_version


class RequestQuery(CamelModel):
    filters: List[dict] = []
    include_resultset_responses: IncludeResultsetResponses = IncludeResultsetResponses.HIT
    pagination: Pagination = Pagination()
    request_parameters: Union[list,dict] = {}
    test_mode: bool = False
    requested_granularity: Granularity = Granularity(max_beacon_granularity)
    scope: str = None

class SequenceQuery(BaseModel):
    referenceName: Union[str,int]
    start: Union[int,list]
    alternateBases:str
    referenceBases: str
    clinicalRelevance: Optional[str] =None
    mateName: Optional[str] =None
    assemblyId: Optional[str] =None
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
        else:# pragma: no cover
            raise ValueError

class DatasetsRequested(BaseModel):
    datasets: list

class GeneIdQuery(BaseModel):
    geneId: str
    variantType: Optional[str] =None
    alternateBases: Optional[str] =None
    aminoacidChange: Optional[str] =None
    variantMinLength: Optional[int] =None
    variantMaxLength: Optional[int] =None

class BracketQuery(BaseModel):
    referenceName: Union[str,int]
    start: list
    end: list
    variantType: Optional[str] =None
    clinicalRelevance: Optional[str] =None
    mateName: Optional[str] =None
    assemblyId: Optional[str] =None
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

class AminoacidChangeQuery(BaseModel):
    aminoacidChange: str
    geneId: str

class RequestParams(CamelModel):
    meta: RequestMeta = RequestMeta()
    query: RequestQuery = RequestQuery()

    def from_request(self, request: Request) -> Self:
        request_params={}
        try:
            if request.method != "POST" or not request.has_body or not request.can_read_body:            
                for k, v in request.query.items():
                    if k == "requestedSchema":# pragma: no cover
                        self.meta.requested_schemas = [html.escape(v)] # comprovar si és la sanitització recomanada
                    elif k == "skip":# pragma: no cover
                        self.query.pagination.skip = int(html.escape(v))
                    elif k == "limit":
                        self.query.pagination.limit = int(html.escape(v))
                    elif k == "includeResultsetResponses":
                        self.query.include_resultset_responses = IncludeResultsetResponses(html.escape(v))
                    elif k == 'datasets':
                        self.query.request_parameters[k] = html.escape(v)
                    elif k == 'filters':
                        self.query.request_parameters[k] = html.escape(v)
                    elif k == 'testMode':
                        v = html.escape(v)
                        if v.lower() == 'true':
                            v = True
                        elif v.lower() == 'false':# pragma: no cover
                            v = False
                        else:
                            ErrorClass.error_code=400
                            ErrorClass.error_message='testMode parameter can only be either true or false value'
                            raise
                        self.query.test_mode = v
                    elif k in ["start", "end", "assemblyId", "referenceName", "referenceBases", "alternateBases", "variantType","variantMinLength","variantMaxLength","geneId","genomicAlleleShortForm","aminoacidChange","clinicalRelevance", "mateName"]:
                        try:
                            if ',' in v:# pragma: no cover
                                v_splitted = v.split(',')
                                request_params[k]=[int(v) for v in v_splitted]
                            else:
                                request_params[k]=int(v)
                        except Exception as e:
                            request_params[k]=v
                        self.query.request_parameters[k] = html.escape(v)
                    else:
                        catch_req_params = {}
                        for k, v in request.query.items():
                            catch_req_params[k]=v
                        ErrorClass.error_code=400
                        ErrorClass.error_message='set of request parameters: {} not allowed'.format(catch_req_params)
                        raise
        except Exception:
            request_params=request["query"]["requestParameters"]
        if request_params != {}:
            try:
                RangeQuery(**request_params)
                return self
            except Exception as e:
                pass
            try:
                SequenceQuery(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            try:
                BracketQuery(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            try:
                GeneIdQuery(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            try:
                AminoacidChangeQuery(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            try:
                GenomicAlleleQuery(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            try:
                DatasetsRequested(**request_params)
                return self# pragma: no cover
            except Exception as e:
                pass
            ErrorClass.error_code=400
            ErrorClass.error_message='set of request parameters: {} not allowed'.format(request_params)
            raise
        return self

    def summary(self):
        try:
            list_of_filters=[]
            for item in self.query.filters:
                for k,v in item.items():
                    if v not in list_of_filters:
                        list_of_filters.append(html.escape(v))
            return {
                "apiVersion": self.meta.api_version,
                "requestedSchemas": self.meta.requested_schemas,
                "filters": list_of_filters,
                "requestParameters": self.query.request_parameters,
                "includeResultsetResponses": self.query.include_resultset_responses,
                "pagination": self.query.pagination.dict(),
                "requestedGranularity": self.query.requested_granularity,
                "testMode": self.query.test_mode
            }
        except Exception as e:# pragma: no cover
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise
