from pydantic import (
    BaseModel,
    create_model
)
from typing import List, Optional, Union, Dict
from beacon.utils.modules import load_class, load_types_of_results
from beacon.models.EUCAIM.validator.collections.collections.EUCAIM_collections_v0_0_1 import Collections as Collections_

def make_Collections():
    CollectionType = load_types_of_results("collections")

    @classmethod
    def create(cls, collections: List[Union[CollectionType]]):
        return cls(collections=collections)

    model = create_model(
        "Collections",
        collections=(List[Union[CollectionType]], ...),
        __base__=BaseModel
    )

    setattr(model, "create", create)

    return model

def make_CollectionResponse(Collections):
    # Create the types of the meta, responseSumarry and the handovers depending on the existing entry types in the models
    MetaType = load_class("meta", "Meta")
    ResponseSummaryType = load_class("common", "ResponseSummary")
    HandoverType = load_class("common", "Handover")
    # Create a function to obtain the class with the properties values of the Collections to come by args
    @classmethod
    def create(cls, meta, response: Collections, responseSummary, beaconHandovers=None, info=None):
        return cls(
            meta=meta,
            response=response,
            responseSummary=responseSummary,
            beaconHandovers=beaconHandovers,
            info=info
        )
    # Create the dynamic class with the properties and types defined previously
    model = create_model(
        "CollectionResponse",
        meta=(MetaType, ...),
        responseSummary=(ResponseSummaryType, ...),
        response=(Collections, ...),
        beaconHandovers=(Optional[List[HandoverType]], None),
        info=(Optional[Dict], None),
        __base__=BaseModel
    )
    # Assign the function create for the dynamic class to be able to be used to instantiate a class of it
    setattr(model, "create", create)
    return model