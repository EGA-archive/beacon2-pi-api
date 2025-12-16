from pydantic import (
    BaseModel,
    field_validator
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.utils.modules import load_types_of_results, load_class

from pydantic import (
    BaseModel,
    field_validator,
    create_model
)
from typing import List, Optional, Union, Dict
import math
from beacon.utils.handovers import list_of_handovers_per_dataset
from beacon.utils.modules import load_types_of_results, load_class


def validate_count_precision(v: str) -> str:
    if isinstance(v, str) and v not in ['exact', 'imprecise', 'rounded']:
        raise ValueError(
            'countPrecision must be one between exact, imprecise, rounded'
        )
    return v


def make_ResultsetInstance():
    # Create the types of the results and the handovers depending on the existing entry types in the models
    ResultType = load_types_of_results("non_collections")
    HandoverType = load_class("common", "Handover")

    @field_validator('countPrecision')
    def countPrecision_validator(cls, v):
        return validate_count_precision(v)

    @classmethod
    def build_response_by_dataset(cls, datasetInstance, allowed_granularity, granularity):
        resultsHandovers = None
        # Get if there are any handovers specific to the dataset
        for handover in list_of_handovers_per_dataset:
            if handover["dataset"] == datasetInstance.dataset:
                resultsHandovers = [handover["handover"]]
        # Get the count of the dataset in a variable.
        resultsCount = datasetInstance.dataset_count
        # Depending on the granularity return an instance with some of the values empty or not
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
    # Create a function to obtain the class with the properties values typed by the ResultType and HandoverType from the models obtained
    @classmethod
    def create(cls, **kwargs):
        if 'results' not in kwargs or kwargs['results'] is None:
            kwargs['results'] = [ResultType]
        if 'resultsHandovers' not in kwargs or kwargs['resultsHandovers'] is None:
            kwargs['resultsHandovers'] = [HandoverType]
        return cls(**kwargs)
    # Create the dynamic class with the properties and types defined previously
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
    # Assign the functions create and build_response_by_dataset for the dynamic class to be able to be used to instantiate a class of it
    setattr(model, "create", create)
    setattr(model, "build_response_by_dataset", build_response_by_dataset)

    return model


def make_Resultsets(ResultsetInstance):
    # Create the dynamic class with the properties and types defined previously
    model = create_model(
        "Resultsets",
        resultSets=(List[ResultsetInstance], ...),
        __base__=BaseModel
    )
    # Create a function to obtain the class with the properties values of the resultSets to come by args
    @classmethod
    def return_resultSets(cls, resultSets: List[ResultsetInstance]):
        return cls(resultSets=resultSets)
    # Assign the function return_resultSets for the dynamic class to be able to be used to instantiate a class of it
    setattr(model, "return_resultSets", return_resultSets)
    return model

        
def make_ResultsetsResponse(Resultsets):
    # Create the types of the meta, responseSumarry and the handovers depending on the existing entry types in the models
    MetaType = load_class("meta", "Meta")
    ResponseSummaryType = load_class("common", "ResponseSummary")
    HandoverType = load_class("common", "Handover")
    # Create the dynamic class with the properties and types defined previously
    model = create_model(
        "ResultsetsResponse",
        meta=(MetaType, ...),
        responseSummary=(ResponseSummaryType, ...),
        response=(Resultsets, ...),
        beaconHandovers=(Optional[List[HandoverType]], None),
        info=(Optional[Dict], None),
        __base__=BaseModel
    )
    # Create a function to obtain the class with the properties values of the resultSets to come by args
    @classmethod
    def return_response(cls, meta, response: Resultsets, responseSummary, beaconHandovers=None, info=None):
        return cls(
            meta=meta,
            response=response,
            responseSummary=responseSummary,
            beaconHandovers=beaconHandovers,
            info=info
        )
    # Assign the function return_response for the dynamic class to be able to be used to instantiate a class of it
    setattr(model, "return_response", return_response)

    return model

def build_full_dynamic_response():
    # Generate the three classes for an object of the Resultsets class, the class of all the resultSets as a list of the single object ResultsetInstance classs and the whole ResultSetsResponse class dynamically
    ResultsetInstance = make_ResultsetInstance()

    Resultsets = make_Resultsets(ResultsetInstance)

    ResultsetsResponse = make_ResultsetsResponse(Resultsets)

    return ResultsetInstance, Resultsets, ResultsetsResponse