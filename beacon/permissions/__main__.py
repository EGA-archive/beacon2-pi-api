
from typing import Optional
from aiohttp import web
from .plugins import DummyPermissions as PermissionsProxy
from beacon.logs.logs import LOG
from beacon.auth.__main__ import authentication
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from beacon.budget.__main__ import check_budget
from beacon.conf import dataset
import yaml
from beacon.request.classes import RequestAttributes, ErrorClass

source=dataset.database
complete_module='beacon.connections.'+source+'.datasets'
import importlib
module = importlib.import_module(complete_module, package=None)

@log_with_args(level)
async def authorization(self):
    try:
        auth = RequestAttributes.headers.get('Authorization')
        if not auth or not auth.lower().startswith('bearer '):
            raise web.HTTPUnauthorized()
        list_visa_datasets=[]
        access_token = auth[7:].strip() # 7 = len('Bearer ')
        user, list_visa_datasets = await authentication(self, access_token)
        if user is None:
            user = 'public'# pragma: no cover
        elif user == 'public':
            username = 'public'# pragma: no cover
        else:
            username = user.get('preferred_username')

    except Exception as e:
        list_visa_datasets = []
        username = 'public'
        return username, list_visa_datasets
    return username, list_visa_datasets

@log_with_args(level)
async def get_datasets_list(self, qparams, authorized_datasets):
    try:
        specific_datasets_unauthorized = []
        search_and_authorized_datasets = []
        try:
            specific_datasets = qparams.query.requestParameters['datasets']
        except Exception as e:
            specific_datasets = []
        # Get response
        if specific_datasets != []:
            for element in authorized_datasets:# pragma: no cover
                if element in specific_datasets:
                    search_and_authorized_datasets.append(element)
            for elemento in specific_datasets:# pragma: no cover
                if elemento not in search_and_authorized_datasets:
                    specific_datasets_unauthorized.append(elemento)
            beacon_datasets = module.get_list_of_datasets(self)# pragma: no cover
            response_datasets = [ r['id'] for r in beacon_datasets if r['id'] in search_and_authorized_datasets]# pragma: no cover

        else:
            beacon_datasets = module.get_list_of_datasets(self)
            specific_datasets = [ r['id'] for r in beacon_datasets if r['id'] not in authorized_datasets]
            response_datasets = [ r['id'] for r in beacon_datasets if r['id'] in authorized_datasets]
            specific_datasets_unauthorized.append(specific_datasets)
    except Exception:# pragma: no cover
        raise
    return response_datasets

def query_permissions(func):
    @log_with_args(level)
    async def permission(self, qparams):
        try:
            time_now=None
            username = 'public'
            try:
                requested_datasets = qparams.query.requestParameters["datasets"]
            except Exception:
                requested_datasets = []
            if qparams.query.testMode == True:
                with open("/beacon/permissions/datasets/test_datasets.yml", 'r') as pfile:
                    test_datasets = yaml.safe_load(pfile)
                pfile.close()
                authorized_datasets= test_datasets['test_datasets']
                for requested_dataset in requested_datasets:
                    if requested_dataset not in authorized_datasets:
                        ErrorClass.error_code=400
                        ErrorClass.error_message='requested dataset: {} not a test dataset'.format(requested_dataset)
                        raise web.HTTPBadRequest
            else:
                username, list_visa_datasets = await authorization(self)
                datasets = await PermissionsProxy.get_permissions(self, username=username, requested_datasets=requested_datasets)
                time_now = check_budget(self, RequestAttributes.ip, username)
                authorized_datasets=list(datasets)
                for visa_dataset in list_visa_datasets:
                    authorized_datasets.append(visa_dataset)# pragma: no cover
            response_datasets= await get_datasets_list(self, qparams, authorized_datasets)
            return await func(self, qparams, response_datasets, username, time_now)
        except Exception:# pragma: no cover
            raise
    return permission

