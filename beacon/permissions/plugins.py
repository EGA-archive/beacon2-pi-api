from beacon.request.classes import ErrorClass, RequestAttributes
import yaml
from beacon.logs.logs import LOG

class DatasetPermission:
    def __init__(self, dataset, default_granularity):
        self.dataset = dataset
        self.granularity = default_granularity


class Permissions():
    """Base class, just to agree on the interface."""
    def __init__(self, *args, **kwargs):
        pass

    async def initialize(self):
        raise NotImplementedError('Overload this function in a subclass')

    async def get(self, username, requested_datasets=None):
        """Return an iterable for the granted datasets for the given username and within a requested list of datasets."""
        raise NotImplementedError('Overload this function in a subclass')

    async def close(self):
        raise NotImplementedError('Overload this function in a subclass')



class DummyPermissions(Permissions):
    """
    Dummy permissions plugin
    
    We hard-code the dataset permissions.
    """

    async def initialize(self):
        pass
    
    async def get_permissions(self, username, requested_datasets=None, testMode=False):
        datasets = []
        try:
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                datasets_permissions = yaml.safe_load(pfile)
            pfile.close()
            if testMode == True:
                with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as confile:
                    datasets_conf = yaml.safe_load(confile)
                confile.close()
                test_datasets=[]
                for confdataset, confvalue in datasets_conf.items():
                    for key, value in confvalue.items():
                        if key == 'isTest':
                            if value == True:
                                test_datasets.append(confdataset)
            for dataset, security_level_dict in datasets_permissions.items():
                if testMode == True:
                    if dataset not in test_datasets:
                        continue
                default_granularity = None
                granularity_exceptions = None
                user_granularity_exceptions = None

                for security_level, dataset_properties in security_level_dict.items():
                    if username == 'public' and security_level == 'public':
                        default_granularity = dataset_properties.get('default_entry_types_granularity')
                        granularity_exceptions = dataset_properties.get('entry_types_exceptions')
                    elif username != 'public' and security_level == 'registered':
                        default_granularity = dataset_properties.get('default_entry_types_granularity')
                        granularity_exceptions = dataset_properties.get('entry_types_exceptions')
                    elif username != 'public' and security_level == 'controlled':
                        user_exceptions = dataset_properties.get('user-list')
                        if user_exceptions != None:
                            for user_exception in user_exceptions:
                                if user_exception['user_e-mail'] == username:
                                    user_default_granularity = user_exception.get('default_entry_types_granularity')
                                    default_granularity = dataset_properties.get('default_entry_types_granularity')
                                    granularity_exceptions = dataset_properties.get('entry_types_exceptions')
                                    if user_default_granularity != None:
                                        default_granularity = user_default_granularity
                                    user_granularity_exceptions = user_exception.get('entry_types_exceptions')
                if user_granularity_exceptions != None:
                    for entry_type_id, entry_type_granularity in user_granularity_exceptions[0].items():
                        if entry_type_id == RequestAttributes.entry_type_id:
                            default_granularity = entry_type_granularity
                elif granularity_exceptions != None:
                    for entry_type_id, entry_type_granularity in granularity_exceptions[0].items():
                        if entry_type_id == RequestAttributes.entry_type_id:
                            default_granularity = entry_type_granularity
                if default_granularity != None:
                    datasetInstance = DatasetPermission(dataset, default_granularity)
                    datasets.append(datasetInstance)
            return datasets
        except Exception as e:
            self._error.handle_exception(e, "Check if datasets_permissions.yml file is not empty of datasets or has any header missing.")
            raise

    async def close(self):
        pass