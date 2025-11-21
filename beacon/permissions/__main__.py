
from typing import Optional
from aiohttp import web
from .plugins import DummyPermissions as PermissionsProxy
from beacon.logs.logs import LOG
from beacon.auth.__main__ import authentication
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level, default_beacon_granularity
from beacon.budget.__main__ import check_budget
from beacon.utils.modules import get_all_modules_datasets
from beacon.response.classes import SingleDatasetResponse
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import InvalidRequest, NoPermissionsAvailable

@log_with_args(level)
async def authorization(self):
    try:
        auth = RequestAttributes.headers.get('Authorization')
        if not auth or not auth.lower().startswith('bearer '):
            raise NoPermissionsAvailable('request received did not add a token or token did not start with bearer')
        list_visa_datasets=[]
        access_token = auth[7:].strip() # 7 = len('Bearer ')
        user, list_visa_datasets = await authentication(self, access_token)
        if user is None:
            user = 'public'
        elif user == 'public':
            username = 'public'
        else:
            username = user.get('email')
    except Exception as e:
        list_visa_datasets = []
        username = 'public'
        return username, list_visa_datasets
    return username, list_visa_datasets

@log_with_args(level)
async def get_datasets_list(self, authorized_datasets):
    try:
        specific_datasets = RequestAttributes.qparams.query.requestParameters['datasets']
    except Exception as e:
        specific_datasets = []
    list_of_datasets_confs = get_all_modules_datasets()
    beacon_datasets=[]
    for dataset_conf in list_of_datasets_confs:
        try:
            datasets = dataset_conf.get_list_of_datasets(self)
        except Exception:
            continue
        for dataset in datasets:
            beacon_datasets.append(dataset)
    # Get response
    if specific_datasets != []:
        response_datasets =  [element for element in authorized_datasets if element.dataset in [r['id'] for r in beacon_datasets] and element.dataset in specific_datasets]
    else:
        response_datasets =  [element for element in authorized_datasets if element.dataset in [r['id'] for r in beacon_datasets]]
    return response_datasets

def query_permissions(func):
    @log_with_args(level)
    async def permission(self):
        time_now=None
        username = 'public'
        try:
            requested_datasets = RequestAttributes.qparams.query.requestParameters["datasets"]
        except Exception:
            requested_datasets = []
        username, list_visa_datasets = await authorization(self)
        datasets_permissions = await PermissionsProxy.get_permissions(self, username=username, requested_datasets=requested_datasets, testMode=RequestAttributes.qparams.query.testMode)
        time_now = check_budget(self, username)
        for visa_dataset in list_visa_datasets:
            datasets_permissions.append(SingleDatasetResponse(dataset=visa_dataset, granularity=default_beacon_granularity))
        response_datasets= await get_datasets_list(self, datasets_permissions)
        return await func(self, response_datasets, username, time_now)
    return permission

