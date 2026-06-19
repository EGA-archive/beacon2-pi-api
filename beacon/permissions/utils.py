from beacon.request.classes import RequestAttributes

def return_found_granularity_in_exceptions(self, granularity_exceptions, default_granularity):
    """Method to get the granularity needed to be returned for a specific permissions case"""
    for granularity_exception in granularity_exceptions:
        # Loop over all the exceptions that are handed in and take the one that belongs to the entry type that is being requested
        for entry_type_id, entry_type_granularity in granularity_exception.items():
            if entry_type_id == RequestAttributes.entry_type_id:
                # Assign the entry type granularity and return it back
                default_granularity = entry_type_granularity
                return default_granularity
    return default_granularity

def return_granularity_and_exceptions(self, security_level_dict, username, default_granularity, granularity_exceptions):
    """Methot to get the granularity and exceptions needed to be returned depending on the security leevl case"""
    # Loop over the datasets/datasets_permissions.yml file and
    for security_level, dataset_properties in security_level_dict.items():
        # If a dataset has security level as public and the request is not authenticated, get the granularity and the entry type exceptions
        if security_level == 'public':
            default_granularity = dataset_properties.get('default_entry_types_granularity')
            granularity_exceptions = dataset_properties.get('entry_types_exceptions')
        # If the request is correctly authenticated (username is not public) get the granularity and entry types exceptions in case the dataset has registered security level
        if username != 'public' and security_level == 'registered':
            default_granularity = dataset_properties.get('default_entry_types_granularity')
            granularity_exceptions = dataset_properties.get('entry_types_exceptions')
        # If the request is correctly authenticated (username is not public) get the granularity and entry types exceptions for the specific user that has logged in and in case the dataset has controlled security level
        elif username != 'public' and security_level == 'controlled':
            # Get the user list from the yaml file
            user_exceptions = dataset_properties.get('user-list')
            # If the user-list exists for the security level controlled
            if user_exceptions != None:
                for user_exception in user_exceptions:
                    # Match if the user authenticated has specific permissions for the dataset
                    if user_exception['user_e-mail'] == username:
                        # Get the granularity and entry type exceptions and return them back, as this will override registered security level
                        default_granularity = user_exception.get('default_entry_types_granularity')
                        granularity_exceptions = user_exception.get('entry_types_exceptions')
                        return default_granularity, granularity_exceptions
    return default_granularity, granularity_exceptions