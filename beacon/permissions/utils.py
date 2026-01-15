from beacon.request.classes import RequestAttributes

def return_found_granularity_in_permissions(self, granularity_exceptions, default_granularity):
    for granularity_exception in granularity_exceptions:
        for entry_type_id, entry_type_granularity in granularity_exception.items():
            if entry_type_id == RequestAttributes.entry_type_id:
                default_granularity = entry_type_granularity
                return default_granularity
    return default_granularity