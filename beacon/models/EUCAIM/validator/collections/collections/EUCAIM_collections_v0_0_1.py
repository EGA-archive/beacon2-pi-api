from pydantic import (
    BaseModel,
    PrivateAttr
)

from typing import Optional, List

class AgeRange(BaseModel, extra='forbid'):
    min: float
    max: float

class Collections(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    name: str
    id: str
    description: str
    ageRange:AgeRange
    modalities: List[str]
    bodyParts: List[str]
    gender: List[str]
    subjectsCount: int
    studiesCount: int
    datasetId: Optional[str] = None