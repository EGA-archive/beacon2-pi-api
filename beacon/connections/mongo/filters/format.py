from typing import List, Union
from beacon.request.classes import Operator
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config

@log_with_args(config.level)
def format_value(self, value: Union[str, List[int]]) -> Union[List[int], str, int, float]:
    if isinstance(value, list):
        return value
    elif isinstance(value, int):
        return value
    
    elif value.isnumeric():
        return int(value)
    
    else:
        try:
            return float(value)
        except Exception:
            return value

@log_with_args(config.level)
def format_operator(self, operator: Operator) -> str:
    if operator == Operator.EQUAL:
        return "$eq"
    elif operator == Operator.NOT:
        return "$ne"
    elif operator == Operator.GREATER:
        return "$gt"
    elif operator == Operator.GREATER_EQUAL:
        return "$gte"
    elif operator == Operator.LESS:
        return "$lt"
    elif operator == Operator.LESS_EQUAL:
        return "$lte"