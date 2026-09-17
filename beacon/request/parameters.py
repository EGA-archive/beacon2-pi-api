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

# Model representing schema metadata per entity, with strict field validation (no extra fields allowed)
class SchemasPerEntity(CamelModel, extra='forbid'):
    entityType: Optional[str] = None  # Type of entity (e.g., dataset, individual, etc.)
    schema: Optional[str] = None      # Schema identifier associated with the entity


# Pagination model controlling paging behavior for query results
class Pagination(CamelModel, extra='forbid'):
    skip: int = 0                     # Number of results to skip (offset-based pagination)
    limit: int = 10                   # Maximum number of results to return
    currentPage: Optional[str] = None # Current page cursor/token (if cursor-based pagination is used)
    nexttPage: Optional[str] = None   # Token for the next page (note: typo preserved from original code)
    previousPage: Optional[str] = None # Token for the previous page


# Metadata included in requests, including API version and requested schemas
class RequestMeta(CamelModel, extra='forbid'):
    requestedSchemas: Optional[List[SchemasPerEntity]] = []  # Optional list of schema requests per entity
    apiVersion: str = 'Not provided'  # API version string


# Sequence-based variant query model (position-based query with validation rules)
class SequenceQuery(BaseModel, extra='forbid'):
    referenceName: Union[str, int]  # Chromosome or reference identifier
    start: Union[int, list]         # Start position (single or list, but later restricted)
    alternateBases: str             # Observed alternate allele
    referenceBases: str             # Reference allele
    clinicalRelevance: Optional[str] = None
    mateName: Optional[str] = None
    assemblyId: Optional[str] = None  # Required for non-HGVS chromosome-based queries
    datasets: Optional[list] = []

    # Validator enforcing consistency between referenceName and assemblyId
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId(cls, values):

        # List of allowed chromosome identifiers (numeric and string forms)
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chr24','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]:

            # Assembly must be provided for standard chromosomal coordinates
            if values.assemblyId is None:
                raise ValueError(
                    'if referenceName is just the chromosome: assemblyId parameter is required'
                )

        # Reject unsupported referenceName formats
        else:
            raise ValueError(
                'referenceName must be a number between 1-24, or a string with X, Y, MT or chr-prefixed values'
            )

    # Ensures that start position is not an array of multiple values
    @field_validator('start')
    @classmethod
    def id_must_be_CURIE(cls, v: Union[int, list]) -> Union[int, list]:

        # If multiple start positions are provided, reject request
        if isinstance(v, list):
            if len(v) > 1:
                raise ValueError('start can only have one item in the array')


# Range-based variant query model (start/end interval queries)
class RangeQuery(BaseModel, extra='forbid'):
    referenceName: Union[str, int]
    start: Union[int, list]
    end: Union[int, list]
    variantType: Optional[str] = None
    alternateBases: Optional[str] = None
    aminoacidChange: Optional[str] = None
    variantMinLength: Optional[int] = None
    variantMaxLength: Optional[int] = None
    clinicalRelevance: Optional[str] = None
    mateName: Optional[str] = None
    assemblyId: Optional[str] = None
    datasets: Optional[list] = []

    # Validate referenceName and ensure correct coordinate ordering
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_2(cls, values):

        # Same chromosome validation as SequenceQuery
        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chr24','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]:

            if values.assemblyId is None:
                raise ValueError(
                    'if referenceName is just the chromosome: assemblyId parameter is required'
                )

        else:
            raise ValueError(
                'referenceName must be a number between 1-24 or a valid chr-prefixed identifier'
            )

        # Normalize start/end values (handle list inputs)
        start = values.start
        end = values.end

        if isinstance(start, list):
            start = start[0]
        if isinstance(end, list):
            end = end[0]

        # Ensure valid genomic interval ordering
        if int(start) > int(end):
            raise ValueError("start's value can not be greater than end's value")


# Gene-based variant query model
class GeneIdQuery(BaseModel, extra='forbid'):
    geneId: str
    variantType: Optional[str] = None
    alternateBases: Optional[str] = None
    aminoacidChange: Optional[str] = None
    variantMinLength: Optional[int] = None
    variantMaxLength: Optional[int] = None
    datasets: Optional[list] = []


# Bracket-style genomic interval query model
class BracketQuery(BaseModel, extra='forbid'):
    referenceName: Union[str, int]
    start: list
    end: list
    variantType: Optional[str] = None
    clinicalRelevance: Optional[str] = None
    mateName: Optional[str] = None
    assemblyId: Optional[str] = None
    datasets: Optional[list] = []

    # Validate and normalize start list values
    @field_validator('start')
    @classmethod
    def start_must_be_array_of_integers(cls, v: list) -> list:
        new_list = []

        for num in v:
            if isinstance(num, int):
                new_list.append(num)
            elif isinstance(num, str):
                try:
                    new_list.append(str(num))
                except Exception:
                    raise ValueError('start parameter must be an array of integers')

        return new_list

    # Validate and normalize end list values
    @field_validator('end')
    @classmethod
    def end_must_be_array_of_integers(cls, v: list) -> list:
        new_list = []

        for num in v:
            if isinstance(num, int):
                new_list.append(num)
            elif isinstance(num, str):
                try:
                    new_list.append(str(num))
                except Exception:
                    raise ValueError('end parameter must be an array of integers')

        return new_list

    # Ensure chromosome reference validity and assembly requirement
    @model_validator(mode='after')
    @classmethod
    def referenceName_must_have_assemblyId_if_not_HGVSId_3(cls, values):

        if values.referenceName in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','X','Y','MT','chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chr23','chr24','chrX','chrY','chrMT',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]:

            if values.assemblyId is None:
                raise ValueError('if referenceName is just the chromosome: assemblyId parameter is required')


# Genomic HGVS-style allele query
class GenomicAlleleQuery(BaseModel, extra='forbid'):
    genomicAlleleShortForm: str
    datasets: Optional[list] = []


# Amino acid substitution query model
class AminoacidChangeQuery(BaseModel, extra='forbid'):
    aminoacidChange: str
    geneId: str
    datasets: Optional[list] = []


# Dataset selection wrapper
class DatasetsRequested(BaseModel, extra='forbid'):
    datasets: list[str]


# Main request query model combining filters + multiple query types
class RequestQuery(CamelModel, extra='forbid'):

    # Flexible filter system supporting multiple filter types
    filters: List[
        Union[
            AlphanumericFilter,
            OntologyFilter,
            CustomFilter,
            List[Union[AlphanumericFilter, OntologyFilter, CustomFilter]]
        ]
    ] = []

    includeResultsetResponses: IncludeResultsetResponses = IncludeResultsetResponses.HIT  # Response detail level
    pagination: Pagination = Pagination()  # Paging configuration

    # Union of all supported query parameter models
    requestParameters: Union[
        SequenceQuery,
        RangeQuery,
        BracketQuery,
        AminoacidChangeQuery,
        GeneIdQuery,
        GenomicAlleleQuery,
        DatasetsRequested
    ] = {}

    testMode: bool = False  # Enables test-only behavior

    requestedGranularity: Granularity = Granularity(config.default_beacon_granularity)

    # Validate allowed granularity values
    @field_validator('requestedGranularity')
    @classmethod
    def requestedGranularity_must_be_boolean_count_record(cls, v: str) -> str:
        if v not in ['boolean', 'count', 'record']:
            raise ValueError('requestedGranularity must be one between boolean, count, record')
        return v

    # Validate includeResultsetResponses values
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
