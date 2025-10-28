from pydantic import (
    BaseModel,
    field_validator
)
from beacon.validator.model.genomicVariations import GenomicVariations
from beacon.validator.model.analyses import Analyses
from beacon.validator.model.biosamples import Biosamples
from beacon.validator.model.biosamples import Biosamples
from beacon.validator.model.individuals import Individuals
from beacon.validator.model.runs import Runs
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.validator.framework.meta import Meta
from beacon.conf import conf
from beacon.validator.framework.common import Handover, ResponseSummary

class ResultsetInstance(BaseModel):
    countAdjustedTo: Optional[List[Union[str,int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    id: str
    info: Optional[Dict] = None
    results: Optional[List[Union[Analyses,Biosamples,GenomicVariations,Individuals,Runs]]]=None
    resultsCount: Optional[int]=None
    resultsHandovers: Optional[List[Handover]] = None
    setType: str
    @field_validator('countPrecision')
    @classmethod
    def countPrecision_must_be_exact_imprecise_rounded_resultSet(cls, v: str) -> str:
        if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
            raise ValueError('countPrecision must be one between exact, imprecise, rounded')
        return v
    
    def build_response_by_dataset(self, dataset, data, dict_counts, allowed_granularity, granularity):
        resultsHandovers=None
        countAdjustedTo=None
        countPrecision=None
        for handover in list_of_handovers_per_dataset:
            if handover["dataset"]==dataset.dataset:
                resultsHandovers=[handover["handover"]]
        if dataset.granularity == 'record' and allowed_granularity=='record' and granularity =='record':                                        
            if conf.imprecise_count !=0:
                if dict_counts[dataset.dataset] < conf.imprecise_count:
                    resultsCount=conf.imprecise_count
                    countAdjustedTo=[conf.imprecise_count]
                    countPrecision='imprecise'
                else:
                    resultsCount=dict_counts[dataset.dataset]
                    
            elif conf.round_to_tens == True:
                resultsCount=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                countAdjustedTo=['immediate ten']
                countPrecision='rounded'

            elif conf.round_to_hundreds == True:
                resultsCount=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                countAdjustedTo=['immediate hundred']
                countPrecision='rounded'
            else:
                resultsCount=dict_counts[dataset.dataset]
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=data[dataset.dataset],
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        elif dataset.granularity != 'boolean' and allowed_granularity != 'boolean' and granularity != 'boolean':
            resultsCount=dict_counts[dataset.dataset]
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=None,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        else:
            resultsCount=None
            return self(id=dataset.dataset,
                        setType='dataset',
                        exists=dict_counts[dataset.dataset]>0,
                        results=None,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=None,
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