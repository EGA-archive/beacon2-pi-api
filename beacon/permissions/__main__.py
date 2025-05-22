
from typing import Optional
from aiohttp import web
from aiohttp.web import FileField
from aiohttp.web_request import Request
from .plugins import DummyPermissions as PermissionsProxy
from beacon.logs.logs import LOG
from beacon.auth.__main__ import authentication
from beacon.logs.logs import log_with_args, log_with_args_mongo
from beacon.conf.conf import level
from beacon.budget.__main__ import check_budget
from beacon.conf import dataset

source=dataset.database
complete_module='beacon.connections.'+source+'.datasets'
import importlib
module = importlib.import_module(complete_module, package=None)

@log_with_args(level)
async def authorization(self, request, headers):
    try:
        auth = headers.get('Authorization')
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
async def get_datasets_list(self, qparams, request: Request, authorized_datasets):
    try:
        specific_datasets_unauthorized = []
        search_and_authorized_datasets = []
        try:
            specific_datasets = qparams.query.request_parameters['datasets']
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

def dataset_permissions(func):
    @log_with_args(level)
    async def permission(self, post_data, request: Request, qparams, entry_type, entry_id, ip, headers):
        try:
            if post_data is not None:
                v = post_data.get('datasets')
            else:
                v = None
            if v is None:
                requested_datasets = []
            elif isinstance(v, list):# pragma: no cover
                requested_datasets = v
            elif isinstance(v, FileField):# pragma: no cover
                requested_datasets = []
            else:# pragma: no cover
                requested_datasets = v.split(sep=',')
            
            username, list_visa_datasets = await authorization(self, request, headers)
                
            datasets = await PermissionsProxy.get_permissions(self, username=username, requested_datasets=requested_datasets)
            dict_returned={}
            dict_returned['username']=username
            time_now = check_budget(self, ip, username)
            authorized_datasets=list(datasets)
            for visa_dataset in list_visa_datasets:
                authorized_datasets.append(visa_dataset)# pragma: no cover
            response_datasets= await get_datasets_list(self, qparams, request, authorized_datasets)
            return await func(self, post_data, request, qparams, entry_type, entry_id, response_datasets, ip, headers, username, time_now)
        except Exception:# pragma: no cover
            raise
    return permission

