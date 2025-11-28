from beacon.request.parameters import AlphanumericFilter
from typing import List
from beacon.request.classes import Operator
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.mapping import VARIANTS_PROPERTY_MAP

@log_with_args(level)
def generate_position_filter_start(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    # Initiate variable for filters to process depending on value length.
    filters = []
    if len(value) == 1: # If length is 1, just apply the >= of the start value.
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.GREATER_EQUAL
        ))
    elif len(value) == 2: # If length is 2, just apply a >= and a <= of the start value.
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.GREATER_EQUAL
        ))
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[1],
            operator=Operator.LESS_EQUAL
        ))
    return filters