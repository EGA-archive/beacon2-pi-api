from pydantic import (
    BaseModel
)
from typing import Optional

class SingleDatasetResponse(BaseModel):
    count: Optional[int] = None
    dataset_count: Optional[int] = None
    docs: Optional[list[dict]] = None
    dataset: str
    granularity: str

class MultipleDatasetsResponse(BaseModel):
    datasets_responses: Optional[list[SingleDatasetResponse]] = None
    total_count: Optional[int] = None

class FilteringTermsResponse(BaseModel):
    total_count: int
    datasets_response: list[SingleDatasetResponse]
    datasets: list

class CollectionsResponse(BaseModel):
    docs: list[dict]
    count: int