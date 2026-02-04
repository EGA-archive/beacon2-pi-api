from pydantic import (
    BaseModel
)
from typing import Optional

class SingleDatasetResponse(BaseModel):
    # This class will host all the information to respond for a single dataset.
    exists: Optional[bool] = None
    dataset_count: Optional[int] = None
    docs: Optional[list[dict]] = None
    dataset: str
    granularity: str

class MultipleDatasetsResponse(BaseModel):
    # This class is the contract class of the resultSet response, owning the information for all the datasets in a list and the total count of records found for the query for all the datasets.
    datasets_responses: Optional[list[SingleDatasetResponse]] = None
    total_count: Optional[int] = None

class FilteringTermsResponse(BaseModel):
    # This class is the contract class of the filtering terms response, which consists of a list of the docs found in the corresponding database.
    docs: list

class CollectionsResponse(BaseModel):
    # This class is the contract class of the collections response, which consists of a list of the docs found in the corresponding database and the number of records being returned.
    docs: list[dict]
    count: int