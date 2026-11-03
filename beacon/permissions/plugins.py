import yaml
from beacon.exceptions.exceptions import NoPermissionsAvailable
from beacon.response.classes import SingleDatasetResponse
from beacon.permissions.utils import return_found_granularity_in_exceptions, return_granularity_and_exceptions


class Permissions():
    """Base class, just to agree on the interface."""
    def __init__(self, *args, **kwargs):
        pass

    async def initialize(self):
        raise NotImplementedError('Overload this function in a subclass')

    async def get(self, user_id, requested_datasets=None):
        """Return an iterable for the granted datasets for the given user_id and within a requested list of datasets."""
        raise NotImplementedError('Overload this function in a subclass')

    async def close(self):
        raise NotImplementedError('Overload this function in a subclass')



class DummyPermissions(Permissions):
    async def initialize(self):
        pass
    
    async def get_permissions(self, user_id, requested_datasets=None, testMode=False, entry_type_id=None, visa_datasets=None):
        # Initialize the list of datasets that will be returned depending on the permissions.
        datasets = []
        try:
            # Open the permissions config file and save it in a dictionary.
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                datasets_permissions = yaml.safe_load(pfile)
            pfile.close()
            if visa_datasets!=None:
                for visa_dataset in visa_datasets:
                    if visa_dataset in datasets_permissions:
                        continue
                    else:
                        datasets_permissions[visa_dataset]={"controlled": {"default_entry_types_granularity": "boolean", "user-list": [{"user_id": user_id}]}}
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
            definitive_granularity_per_dataset={}
            # Iterate through the datasets permissions.
            for dataset, security_level_dict in datasets_permissions.items():
                if requested_datasets != None and requested_datasets != []:
                    if dataset not in requested_datasets:
                        continue
                if testMode == True:
                    # In case testMode is active, get rid of the datasets that are not meant for testMode.
                    if dataset not in test_datasets:
                        continue
                if dataset not in definitive_granularity_per_dataset:
                    definitive_granularity_per_dataset[dataset]={}
                # Initialize the default granularity and granularity restrictions to return.
                default_granularity = None
                granularity_exceptions = None
                # Get the default granularity and any granularity restriction to return for the dataset and user (in case there is authentication).
                default_granularity, granularity_exceptions = return_granularity_and_exceptions(self, security_level_dict, user_id, default_granularity, granularity_exceptions)
                # If there is any restriction apply it to the max granularity to return.
                if granularity_exceptions != None:
                    default_granularity=return_found_granularity_in_exceptions(self, granularity_exceptions, default_granularity, entry_type_id)
                if default_granularity != None:
                    if definitive_granularity_per_dataset[dataset] != {}:
                        if next(iter(security_level_dict)) == 'registered':
                            if 'controlled' not in definitive_granularity_per_dataset[dataset]:
                                definitive_granularity_per_dataset[dataset]['registered']=default_granularity
                            if 'public' in definitive_granularity_per_dataset:
                                definitive_granularity_per_dataset[dataset].pop('public')
                        elif next(iter(security_level_dict)) == 'public':
                            if 'controlled' not in definitive_granularity_per_dataset[dataset] and 'registered' not in definitive_granularity_per_dataset[dataset]:
                                definitive_granularity_per_dataset[dataset]['public']=default_granularity
                        elif next(iter(security_level_dict)) == 'controlled':
                            if 'public' in definitive_granularity_per_dataset[dataset]:
                                definitive_granularity_per_dataset[dataset].pop('public')
                            if 'registered' in definitive_granularity_per_dataset[dataset]:
                                definitive_granularity_per_dataset[dataset].pop('registered')
                    else:
                        definitive_granularity_per_dataset[dataset][next(iter(security_level_dict), None)]=default_granularity
                # If there is a default granularity, return it instantiating initially the datasets with their name and the default granularity.
            definitive_datasets_granularity = {
                dataset_id: next(iter(security_level.values()))
                for dataset_id, security_level in definitive_granularity_per_dataset.items()
                if security_level
            }
            for dataset, granularity in definitive_datasets_granularity.items():
                datasetInstance = SingleDatasetResponse(dataset=dataset, granularity=granularity)
                datasets.append(datasetInstance)
            return datasets
        except Exception as e:
            raise NoPermissionsAvailable("Check if datasets_permissions.yml file is not empty of datasets or has any header missing.")

    async def close(self):
        pass