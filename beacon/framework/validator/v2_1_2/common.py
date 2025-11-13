from pydantic import (
    BaseModel
)
from beacon.validator.v2_1_2.model.genomicVariations import OntologyTerm
from typing import Optional
from beacon.request.classes import RequestAttributes
from beacon.conf import conf
import math

class ResponseSummary(BaseModel):
    exists: bool
    numTotalResults: Optional[int] = None
    def build_response_summary_by_dataset(self, datasets):
        count=0
        non_counted=0
        granularity = RequestAttributes.qparams.query.requestedGranularity
        for dataset in datasets:
            if dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':
                if conf.imprecise_count !=0:
                    if dataset.dataset_count < conf.imprecise_count:
                        count+=conf.imprecise_count
                elif conf.round_to_tens == True:
                    count+=math.ceil(dataset.dataset_count / 10.0) * 10
                elif conf.round_to_hundreds == True:
                    count+=math.ceil(dataset.dataset_count / 100.0) * 100
                else:
                    count +=dataset.dataset_count
            else:
                non_counted+=dataset.dataset_count
        if count == 0 and non_counted >0:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=True)
        elif count > 0:
            return self(exists=count > 0,numTotalResults=count)
        else:
            RequestAttributes.returned_granularity = 'boolean'
            return self(exists=False)

class Handover(BaseModel):
    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str

class ReferenceToAnSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    referenceToSchemaDefinition: str
    schemaVersion: Optional[str] = None