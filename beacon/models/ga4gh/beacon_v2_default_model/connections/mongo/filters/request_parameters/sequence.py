from beacon.request.parameters import AlphanumericFilter
from typing import List
from beacon.request.classes import Operator
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.mapping import VARIANTS_PROPERTY_MAP

@log_with_args(level)
def generate_position_filter_start_sequence_query(self, key: str, value: List[int]) -> List[AlphanumericFilter]:
    filters = []
    if len(value) == 1:
        filters.append(AlphanumericFilter(
            id=VARIANTS_PROPERTY_MAP[key],
            value=value[0],
            operator=Operator.EQUAL
        ))
    return filters