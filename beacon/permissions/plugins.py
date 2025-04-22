from beacon.request.classes import ErrorClass
import yaml

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
    
    async def get(self, username, requested_datasets=None):
        try:
            if username == 'public':
                with open("/beacon/permissions/datasets/public_datasets.yml", 'r') as pfile:
                    public_datasets = yaml.safe_load(pfile)
                pfile.close()
                list_public_datasets = public_datasets['public_datasets']
                datasets = []
                for pdataset in list_public_datasets:
                    datasets.append(pdataset)
                datasets = set(datasets)       
            else:
                with open("/beacon/permissions/datasets/registered_datasets.yml", 'r') as file:
                    registered_datasets = yaml.safe_load(file)
                file.close()
                with open("/beacon/permissions/datasets/public_datasets.yml", 'r') as pfile:
                    public_datasets = yaml.safe_load(pfile)
                with open("/beacon/permissions/datasets/controlled_datasets.yml", 'r') as cfile:
                    controlled_datasets = yaml.safe_load(cfile)
                pfile.close()
                list_registered_datasets = registered_datasets['registered_datasets']
                list_public_datasets = public_datasets['public_datasets']
                list_controlled_datasets = controlled_datasets[username]
                datasets = []
                for pdataset in list_public_datasets:
                    datasets.append(pdataset)
                for rdataset in list_registered_datasets:
                    datasets.append(rdataset)
                for cdataset in list_controlled_datasets:
                    datasets.append(cdataset)
                datasets = set(datasets)
                
            if requested_datasets:
                return set(requested_datasets).intersection(datasets)# pragma: no cover
            else:
                return datasets
        except Exception as e:# pragma: no cover
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise

    async def close(self):
        pass# pragma: no cover