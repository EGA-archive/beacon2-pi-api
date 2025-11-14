from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.conf import conf
from beacon.utils.modules import load_types_of_results, load_class

class ResultsetInstance(BaseModel):
    exists: bool
    id: str
    info: Optional[Dict] = None
    results: Optional[List[load_types_of_results()]]=None
    resultsCount: int
    resultsHandovers: Optional[List[load_class("common", "Handover")]] = None
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