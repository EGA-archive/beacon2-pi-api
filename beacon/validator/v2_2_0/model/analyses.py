import json
import argparse
from pydantic import (
    BaseModel,
    ValidationError,
    PrivateAttr
)
from typing import Optional, Union

class Analyses(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    aligner: Optional[str] = None
    analysisDate: str
    biosampleId: Optional[str] = None
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    pipelineName: str
    pipelineRef: Optional[str]=None
    runId: Optional[str]=None
    variantCaller: Optional[str]=None
    