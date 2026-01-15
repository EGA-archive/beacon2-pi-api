from beacon.request.classes import RequestAttributes

def return_found_granularity_in_exceptions(self, granularity_exceptions, default_granularity):
    for granularity_exception in granularity_exceptions:
        for entry_type_id, entry_type_granularity in granularity_exception.items():
            if entry_type_id == RequestAttributes.entry_type_id:
                default_granularity = entry_type_granularity
                return default_granularity
    return default_granularity

def return_granularity_and_exceptions(self, security_level_dict, username, default_granularity, granularity_exceptions):
    for security_level, dataset_properties in security_level_dict.items():
        if security_level == 'public':
            default_granularity = dataset_properties.get('default_entry_types_granularity')
            granularity_exceptions = dataset_properties.get('entry_types_exceptions')
        if username != 'public' and security_level == 'registered':
            default_granularity = dataset_properties.get('default_entry_types_granularity')
            granularity_exceptions = dataset_properties.get('entry_types_exceptions')
        elif username != 'public' and security_level == 'controlled':
            user_exceptions = dataset_properties.get('user-list')
            if user_exceptions != None:
                for user_exception in user_exceptions:
                    if user_exception['user_e-mail'] == username:
                        default_granularity = user_exception.get('default_entry_types_granularity')
                        granularity_exceptions = user_exception.get('entry_types_exceptions')
                        return default_granularity, granularity_exceptions
    return default_granularity, granularity_exceptions