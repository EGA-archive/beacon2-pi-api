import yaml
from beacon.logs.logs import LOG
from beacon.exceptions.exceptions import NoPermissionsAvailable
from beacon.response.classes import SingleDatasetResponse
from beacon.permissions.utils import return_found_granularity_in_exceptions, return_granularity_and_exceptions


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
    async def initialize(self):
        pass
    
    async def get_permissions(self, username, requested_datasets=None, testMode=False):
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
                default_granularity, granularity_exceptions = return_granularity_and_exceptions(self, security_level_dict, username, default_granularity, granularity_exceptions)
                # If there is any restriction apply it to the max granularity to return.
                if granularity_exceptions != None:
                    default_granularity=return_found_granularity_in_exceptions(self, granularity_exceptions, default_granularity)
                # If there is a default granularity, return it instantiating initially the datasets with their name and the default granularity.
                if default_granularity != None:
                    datasetInstance = SingleDatasetResponse(dataset=dataset, granularity=default_granularity)
                    datasets.append(datasetInstance)
            return datasets
        except Exception as e:
            raise NoPermissionsAvailable("Check if datasets_permissions.yml file is not empty of datasets or has any header missing.")

    async def close(self):
        pass