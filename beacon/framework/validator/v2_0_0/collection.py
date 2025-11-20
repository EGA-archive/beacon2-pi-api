from pydantic import (
    BaseModel,
    create_model
)
from typing import List, Optional, Union, Dict
from beacon.utils.modules import load_class, load_types_of_results

def make_Collections():
    CollectionType = load_types_of_results("collections")

    def create(cls, collections: List[Union[CollectionType]]):
        return cls(collections=collections)

    model = create_model(
        "Collections",
        collections=(List[Union[CollectionType]], ...),
        __base__=BaseModel
    )


    setattr(model, "create", classmethod(create))

    return model

def make_CollectionResponse(Collections):
    MetaType = load_class("meta", "Meta")
    ResponseSummaryType = load_class("common", "ResponseSummary")
    HandoverType = load_class("common", "Handover")

    def create(cls, meta, response: Collections, responseSummary, beaconHandovers=None, info=None):
        return cls(
            meta=meta,
            response=response,
            responseSummary=responseSummary,
            beaconHandovers=beaconHandovers,
            info=info
        )

    model = create_model(
        "CollectionResponse",
        meta=(MetaType, ...),
        responseSummary=(ResponseSummaryType, ...),
        response=(Collections, ...),
        beaconHandovers=(Optional[List[HandoverType]], None),
        info=(Optional[Dict], None),
        __base__=BaseModel
    )

    setattr(model, "create", classmethod(create))
    return model