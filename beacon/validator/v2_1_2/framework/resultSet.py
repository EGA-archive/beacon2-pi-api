from pydantic import (
    BaseModel,
    field_validator
)
from beacon.validator.v2_1_2.model.genomicVariations import GenomicVariations
from beacon.validator.v2_1_2.model.analyses import Analyses
from beacon.validator.v2_1_2.model.biosamples import Biosamples
from beacon.validator.v2_1_2.model.biosamples import Biosamples
from beacon.validator.v2_1_2.model.individuals import Individuals
from beacon.validator.v2_1_2.model.runs import Runs
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.validator.v2_1_2.framework.meta import Meta
from beacon.conf import conf
from beacon.validator.v2_1_2.framework.common import Handover, ResponseSummary

class ResultsetInstance(BaseModel):
    exists: bool
    id: str
    info: Optional[Dict] = None
    results: List[Union[Analyses,Biosamples,GenomicVariations,Individuals,Runs]]
    resultsCount: int
    resultsHandovers: Optional[List[Handover]] = None
    setType: str
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded_resultSet(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    
    def build_response_by_dataset(self, datasetInstance, allowed_granularity, granularity):
        resultsHandovers=None
        for handover in list_of_handovers_per_dataset:
            if handover["dataset"]==datasetInstance.dataset:
                resultsHandovers=[handover["handover"]]
        if datasetInstance.granularity == 'record' and allowed_granularity=='record' and granularity =='record':                                        
            resultsCount=datasetInstance.dataset_count
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=datasetInstance.docs,
                        resultsCount=resultsCount,
                        resultsHandovers=resultsHandovers)
        elif datasetInstance.granularity != 'boolean' and allowed_granularity != 'boolean' and granularity != 'boolean':
            resultsCount=datasetInstance.dataset_count
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=None,
                        resultsCount=resultsCount,
                        resultsHandovers=resultsHandovers)
        else:
            resultsCount=None
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=None,
                        resultsCount=resultsCount,
                        resultsHandovers=resultsHandovers)

class Resultsets(BaseModel):
    resultSets: List[ResultsetInstance]
    
    def return_resultSets(self, resultSets):
        return self(resultSets = resultSets)
        
class ResultsetsResponse(BaseModel):
    meta: Meta
    responseSummary: ResponseSummary
    response: Resultsets
    beaconHandovers: Optional[List[Handover]] = None
    info: Optional[Dict] = None
    
    def return_response(self, meta, resultSets, responseSummary):
        return self(meta = meta, response = resultSets, responseSummary = responseSummary)