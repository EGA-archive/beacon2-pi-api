from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
import aiohttp.web as web
from bson import json_util
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import InvalidData
from beacon.exceptions.exceptions import DatabaseIsDown
from beacon.utils.modules import check_database_connections
from aiohttp_cors import CorsViewMixin
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
import asyncio

class HealthView(web.View, CorsViewMixin):
    def __init__(self, request: Request):
        # Initialize dhe endpoint with some of the attributes that will need to be collected later on
        self._request = request
        RequestAttributes.ip = None
        RequestAttributes.headers=None
        self.LOG=self.request.app['logger']
        self._id=None
        self._id = generate_txid(self)

    async def get(self):
        #try:
        # Decompound/validate the request and store the attributes needed in the class RequestAttributes
        # Call the handler function for the view assigned to the queried endpoint
        return await self.handler()
    
    @log_with_args(config.level)
    async def handler(self):
        try:
            state=self._request.app['state']
            if state not in ['Shutting down', 'Draining']:
                self._request.app['state'] = 'Running - healthy'
                await check_database_connections(LOG=self.LOG)
                response_obj = {"state": self._request.app['state']}
            else:
                response_obj = {"state": self._request.app['state'], "number_of_requests_pending": len(self._request.app['pending_requests'])}
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except DatabaseIsDown as e:
            self._request.app['state']='Running - degraded'
            response_obj = {"state": self._request.app['state'], "error": "{} database is down".format(e)}
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')