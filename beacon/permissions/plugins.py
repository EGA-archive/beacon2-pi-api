from beacon.request.classes import RequestAttributes
import yaml
from beacon.logs.logs import LOG
from beacon.exceptions.exceptions import NoPermissionsAvailable
from beacon.response.classes import SingleDatasetResponse


class Permissions():
    """Base class, just to agree on the interface."""
    def __init__(self, *args, **kwargs):
        pass

    async def initialize(self):
        raise NotImplementedError('Overload this function in a subclass')

    async def get(self, username):
        """Return an iterable for the granted datasets for the given username and within a requested list of datasets."""
        raise NotImplementedError('Overload this function in a subclass')

    async def close(self):
        raise NotImplementedError('Overload this function in a subclass')



class DummyPermissions(Permissions):
    async def initialize(self):
        pass
    
    async def get_permissions(self, username, testMode=False):
        # Initialize the list of datasets that will be returned depending on the permissions.
        datasets = []
        try:
            # Open the permissions config file and save it in a dictionary.
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                datasets_permissions = yaml.safe_load(pfile)
            pfile.close()
            if testMode == True:
                # If the testMode is requested, open the datasets configuration file and save it in a dictionary.
                with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as confile:
                    datasets_conf = yaml.safe_load(confile)
                confile.close()
                # Initialize the list of test datasets that will be returned depending on the permissions.
                test_datasets=[]
                # Iterate the datasets configuration dictionary and get the test datasets ids.
                for confdataset, confvalue in datasets_conf.items():
                    for key, value in confvalue.items():
                        if key == 'isTest':
                            if value == True:
                                test_datasets.append(confdataset)
            # Iterate through the datasets permissions.
            for dataset, security_level_dict in datasets_permissions.items():
                if testMode == True:
                    # In case testMode is active, get rid of the datasets that are not meant for testMode.
                    if dataset not in test_datasets:
                        continue
                # Initialize the default granularity and granularity restrictions to return.
                default_granularity = None
                granularity_exceptions = None
                # Get the default granularity and any granularity restriction to return for the dataset and user (in case there is authentication).
                for security_level, dataset_properties in security_level_dict.items():
                    if security_level == 'public':
                        default_granularity = dataset_properties.get('default_entry_types_granularity')
                        granularity_exceptions = dataset_properties.get('entry_types_exceptions')
                    if username != 'public' and security_level == 'registered':
                        default_granularity = dataset_properties.get('default_entry_types_granularity')
                        granularity_exceptions = dataset_properties.get('entry_types_exceptions')
                    if username != 'public' and security_level == 'controlled':
                        user_exceptions = dataset_properties.get('user-list')
                        if user_exceptions != None:
                            for user_exception in user_exceptions:
                                if user_exception['user_e-mail'] == username:
                                    default_granularity = user_exception.get('default_entry_types_granularity')
                                    granularity_exceptions = user_exception.get('entry_types_exceptions')
                # If there is any restriction apply it to the max granularity to return.
                if granularity_exceptions != None:
                    for entry_type_id, entry_type_granularity in granularity_exceptions[0].items():
                        if entry_type_id == RequestAttributes.entry_type_id:
                            default_granularity = entry_type_granularity
                # If there is a default granularity, return it instantiating initially the datasets with their name and the default granularity.
                if default_granularity != None:
                    datasetInstance = SingleDatasetResponse(dataset=dataset, granularity=default_granularity)
                    datasets.append(datasetInstance)
            return datasets
        except Exception as e:
            raise NoPermissionsAvailable("Check if datasets_permissions.yml file is not empty of datasets or has any header missing.")

    async def close(self):
        pass