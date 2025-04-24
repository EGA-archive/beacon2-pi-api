from beacon.request.classes import ErrorClass
import yaml
from beacon.logs.logs import LOG, log_with_args_initial, level

class Permissions():
    """Base class, just to agree on the interface."""
    def __init__(self, *args, **kwargs):
        pass# pragma: no cover

    async def initialize(self):
        raise NotImplementedError('Overload this function in a subclass')# pragma: no cover

    async def get(self, username, requested_datasets=None):
        """Return an iterable for the granted datasets for the given username and within a requested list of datasets."""
        raise NotImplementedError('Overload this function in a subclass')# pragma: no cover

    async def close(self):
        raise NotImplementedError('Overload this function in a subclass')# pragma: no cover



class DummyPermissions(Permissions):
    """
    Dummy permissions plugin
    
    We hard-code the dataset permissions.
    """

    async def initialize(self):
        pass# pragma: no cover
    
    @log_with_args_initial(level)
    async def get_permissions(self, username, requested_datasets=None):
        if username == 'public':
            try:
                with open("/beacon/permissions/datasets/public_datasets.yml", 'r') as pfile:
                    public_datasets = yaml.safe_load(pfile)
                pfile.close()
                list_public_datasets = public_datasets['public_datasets']
                datasets = []
                for pdataset in list_public_datasets:
                    datasets.append(pdataset)
                datasets = set(datasets)       
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="Check if public_datasets.yml file is not empty of datasets or has the public_datasets header."
                raise
        else:
            with open("/beacon/permissions/datasets/registered_datasets.yml", 'r') as file:
                registered_datasets = yaml.safe_load(file)
            file.close()
            with open("/beacon/permissions/datasets/public_datasets.yml", 'r') as pfile:
                public_datasets = yaml.safe_load(pfile)
            with open("/beacon/permissions/datasets/controlled_datasets.yml", 'r') as cfile:
                controlled_datasets = yaml.safe_load(cfile)
            pfile.close()
            try:
                list_registered_datasets = registered_datasets['registered_datasets']
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="registered_datasets.yml file is wrong. Check if registered_datasets header is in there."
                raise
            try:
                list_public_datasets = public_datasets['public_datasets']
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="public_datasets.yml file is wrong. Check if public_datasets header is in there."
                raise
            try:
                list_controlled_datasets = controlled_datasets[username]
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="Username could not be found in controlled_datasets.yml file."
                raise
            datasets = []
            try:
                for pdataset in list_public_datasets:
                    datasets.append(pdataset)
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="public_datasets.yml file is empty of datasets"
                raise
            try:
                for rdataset in list_registered_datasets:
                    datasets.append(rdataset)
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="registered_datasets.yml file is empty of datasets"
                raise
            try:
                for cdataset in list_controlled_datasets:
                    datasets.append(cdataset)
            except Exception:
                ErrorClass.error_code=500
                ErrorClass.error_message="controlled_datasets.yml file is empty of datasets"
                raise
            datasets = set(datasets)
        
        if requested_datasets:
            return set(requested_datasets).intersection(datasets)# pragma: no cover
        else:
            return datasets

    async def close(self):
        pass# pragma: no cover