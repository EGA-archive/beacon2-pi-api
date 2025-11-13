from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.validator.v2_2_0.framework.meta import Meta
from beacon.conf import conf
from beacon.validator.v2_2_0.framework.common import Handover, ResponseSummary
import os
from beacon.logs.logs import LOG
from beacon.request.classes import RequestAttributes

list_of_resultSets=[]

dirs = os.listdir("/beacon/models")
for folder in dirs:
    subdirs = os.listdir("/beacon/models/"+folder)
    if "validator" in subdirs:
        validatordirs = os.listdir("/beacon/models/"+folder+"/validator")
        for validatorfolder in validatordirs:
            validatorfiles = os.listdir("/beacon/models/"+folder+"/validator/"+validatorfolder)
            for validatorfile in validatorfiles:
                if RequestAttributes.returned_apiVersion.replace(".","_") in validatorfile:
                    complete_module='beacon.models.'+folder+'.validator.'+validatorfolder+'.'+validatorfile
                    complete_module=complete_module.replace('.py', '')
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    klass = getattr(module, validatorfolder.capitalize())
                    list_of_resultSets.append(klass)
    else:
        for subfolder in subdirs:
            underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
            if "validator" in underdirs:
                validatordirs = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator")
                for validatorfolder in validatordirs:
                    validatorfiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator/"+validatorfolder)
                    for validatorfile in validatorfiles:
                        if RequestAttributes.returned_apiVersion.replace(".","_") in validatorfile:
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.validator.'+validatorfolder+'.'+validatorfile
                            complete_module=complete_module.replace('.py', '')
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            klass = getattr(module, validatorfolder.capitalize())
                            list_of_resultSets.append(klass)

union_type = Union[tuple(list_of_resultSets)]

class ResultsetInstance(BaseModel):
    countAdjustedTo: Optional[List[Union[str,int]]] = None
    countPrecision: Optional[str] = None
    exists: bool
    id: str
    info: Optional[Dict] = None
    results: Optional[List[union_type]]=None
    resultsCount: Optional[int]=None
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
        countAdjustedTo=None
        countPrecision=None
        for handover in list_of_handovers_per_dataset:
            if handover["dataset"]==datasetInstance.dataset:
                resultsHandovers=[handover["handover"]]
        if datasetInstance.granularity == 'record' and allowed_granularity=='record' and granularity =='record':                                        
            if conf.imprecise_count !=0:
                if datasetInstance.dataset_count < conf.imprecise_count:
                    resultsCount=conf.imprecise_count
                    countAdjustedTo=[conf.imprecise_count]
                    countPrecision='imprecise'
                else:
                    resultsCount=datasetInstance.dataset_count
                    
            elif conf.round_to_tens == True:
                resultsCount=math.ceil(datasetInstance.dataset_count / 10.0) * 10
                countAdjustedTo=['immediate ten']
                countPrecision='rounded'

            elif conf.round_to_hundreds == True:
                resultsCount=math.ceil(datasetInstance.dataset_count / 100.0) * 100
                countAdjustedTo=['immediate hundred']
                countPrecision='rounded'
            else:
                resultsCount=datasetInstance.dataset_count
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=datasetInstance.docs,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        elif datasetInstance.granularity != 'boolean' and allowed_granularity != 'boolean' and granularity != 'boolean':
            resultsCount=datasetInstance.dataset_count
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=None,
                        resultsCount=resultsCount,
                        countAdjustedTo=countAdjustedTo,
                        countPrecision=countPrecision,
                        resultsHandovers=resultsHandovers)
        else:
            resultsCount=None
            return self(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
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