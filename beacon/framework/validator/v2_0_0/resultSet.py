from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.conf import conf
from beacon.utils.modules import load_types_of_results, load_class

from pydantic import (
    BaseModel,
    field_validator,
    create_model
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.conf import conf
from beacon.utils.modules import load_types_of_results, load_class


def validate_count_precision(v: str) -> str:
    if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
        raise ValueError(
            'countPrecision must be one between exact, imprecise, rounded'
        )
    return v


def make_ResultsetInstance():
    ResultType = load_types_of_results("non_collections")
    HandoverType = load_class("common", "Handover")

    @field_validator('countPrecision')
    def countPrecision_validator(cls, v):
        return validate_count_precision(v)

    def build_response_by_dataset(cls, datasetInstance, allowed_granularity, granularity):
        resultsHandovers = None

        for handover in list_of_handovers_per_dataset:
            if handover["dataset"] == datasetInstance.dataset:
                resultsHandovers = [handover["handover"]]

        resultsCount = datasetInstance.dataset_count

        if datasetInstance.granularity == 'record' and allowed_granularity=='record' and granularity =='record':                                        
            resultsCount=datasetInstance.dataset_count
            return cls(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=datasetInstance.docs,
                        resultsCount=resultsCount,
                        resultsHandovers=resultsHandovers)
        elif datasetInstance.granularity != 'boolean' and allowed_granularity != 'boolean' and granularity != 'boolean':
            resultsCount=datasetInstance.dataset_count
            return cls(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=None,
                        resultsCount=None,
                        resultsHandovers=resultsHandovers)
        else:
            resultsCount=None
            return cls(id=datasetInstance.dataset,
                        setType='dataset',
                        exists=datasetInstance.exists,
                        results=None,
                        resultsCount=resultsCount,
                        resultsHandovers=resultsHandovers)

    def create(cls, **kwargs):
        if 'results' not in kwargs or kwargs['results'] is None:
            kwargs['results'] = [ResultType]
        if 'resultsHandovers' not in kwargs or kwargs['resultsHandovers'] is None:
            kwargs['resultsHandovers'] = [HandoverType]
        return cls(**kwargs)

    model = create_model(
        "ResultsetInstance",
        countAdjustedTo=(Optional[List[Union[str, int]]], None),
        countPrecision=(Optional[str], None),
        exists=(bool, ...),
        id=(str, ...),
        info=(Optional[Dict], None),
        results=(Optional[List[ResultType]], None),
        resultsCount=(Optional[int], None),
        resultsHandovers=(Optional[List[HandoverType]], None),
        setType=(str, ...),
        __validators__={
            'countPrecision_validator': countPrecision_validator
        }
    )

    setattr(model, "create", classmethod(create))
    setattr(model, "build_response_by_dataset", classmethod(build_response_by_dataset))

    return model


def make_Resultsets(ResultsetInstance):
    model = create_model(
        "Resultsets",
        resultSets=(List[ResultsetInstance], ...),
        __base__=BaseModel
    )

    @classmethod
    def return_resultSets(cls, resultSets: List[ResultsetInstance]):
        return cls(resultSets=resultSets)

    setattr(model, "return_resultSets", return_resultSets)
    return model

        
def make_ResultsetsResponse(Resultsets):

    MetaType = load_class("meta", "Meta")
    ResponseSummaryType = load_class("common", "ResponseSummary")
    HandoverType = load_class("common", "Handover")

    model = create_model(
        "ResultsetsResponse",
        meta=(MetaType, ...),
        responseSummary=(ResponseSummaryType, ...),
        response=(Resultsets, ...),
        beaconHandovers=(Optional[List[HandoverType]], None),
        info=(Optional[Dict], None),
        __base__=BaseModel
    )

    @classmethod
    def return_response(cls, meta, response: Resultsets, responseSummary, beaconHandovers=None, info=None):
        return cls(
            meta=meta,
            response=response,
            responseSummary=responseSummary,
            beaconHandovers=beaconHandovers,
            info=info
        )

    setattr(model, "return_response", return_response)

    return model

def build_full_dynamic_response():
    ResultsetInstance = make_ResultsetInstance()

    Resultsets = make_Resultsets(ResultsetInstance)

    ResultsetsResponse = make_ResultsetsResponse(Resultsets)

    return ResultsetInstance, Resultsets, ResultsetsResponse