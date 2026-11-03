def return_found_granularity_in_exceptions(self, granularity_exceptions, default_granularity, request_attr_entry_type_id,):
    """Method to get the granularity needed to be returned for a specific permissions case"""
    for granularity_exception in granularity_exceptions:
        # Loop over all the exceptions that are handed in and take the one that belongs to the entry type that is being requested
        for entry_type_id, entry_type_granularity in granularity_exception.items():
            if entry_type_id == request_attr_entry_type_id:
                # Assign the entry type granularity and return it back
                default_granularity = entry_type_granularity
                return default_granularity
    return default_granularity

def return_granularity_and_exceptions(self, security_level_dict, user_id, default_granularity, granularity_exceptions):
    """Method to get the granularity and exceptions needed to be returned depending on the security leevl case"""
    # Loop over the datasets/datasets_permissions.yml file and
    if 'public' in security_level_dict:
         # If a dataset has security level as public and the request is not authenticated, get the granularity and the entry type exceptions
        try:
            default_granularity = security_level_dict['public'].get('default_entry_types_granularity')
        except Exception:
            default_granularity = 'boolean'
        try:
            granularity_exceptions = security_level_dict['public'].get('entry_types_exceptions')
        except Exception:
            granularity_exceptions = None
    if 'registered' in security_level_dict and user_id != None:
        try:
            default_granularity = security_level_dict['registered'].get('default_entry_types_granularity')
        except Exception:
            default_granularity = 'boolean'
        try:
            granularity_exceptions = security_level_dict['registered'].get('entry_types_exceptions')
        except Exception:
            granularity_exceptions = None
    if 'controlled' in security_level_dict and user_id != None:
        user_exceptions = security_level_dict['controlled'].get('user-list')
        # If the user-list exists for the security level controlled
        if user_exceptions != None:
            for user_exception in user_exceptions:
                # Match if the user authenticated has specific permissions for the dataset
                if user_exception['user_id'] == user_id:
                    try:
                        default_granularity = security_level_dict['controlled'].get('default_entry_types_granularity')
                    except Exception:
                        default_granularity = None
                    try:
                        granularity_exceptions = security_level_dict['controlled'].get('entry_types_exceptions')
                    except Exception:
                        granularity_exceptions = None
                    # Get the granularity and entry type exceptions and return them back, as this will override registered security level
                    if 'default_entry_types_granularity' in user_exception:
                        default_granularity = user_exception.get('default_entry_types_granularity')
                    if 'entry_types_exceptions' in user_exception:
                        granularity_exceptions = user_exception.get('entry_types_exceptions')
                    if default_granularity is None:
                        default_granularity = 'boolean'
                    return default_granularity, granularity_exceptions
    if default_granularity is None:
        default_granularity == 'boolean'
    return default_granularity, granularity_exceptions