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
        # Call the handler function for the view assigned to the queried endpoint
        return await self.handler()
    
    @log_with_args(config.level)
    async def handler(self):
        try:
            # Get the value for the state at the moment of the health check
            state=self._request.app['state']
            # Process the states that are not a shutdown or an await for requests to finish (draining)
            if state not in ['Shutting down', 'Draining']:
                # Assign initially the state healthy in the running case
                self._request.app['state'] = 'Running - healthy'
                # Check that the database connections are alive
                await check_database_connections(LOG=self.LOG)
                # Create the JSON object that will be returned in response
                response_obj = {"state": self._request.app['state']}
            # Process the states that are a shutdown or an await for a requests to finish (draining)
            else:
                # Create the JSON object that will be returned in response adding the information for the number of the requests that are still running prior to state change
                response_obj = {"state": self._request.app['state'], "number_of_requests_pending": len(self._request.app['pending_requests'])}
            # Give a HTTP response with json data application and a 200 status, and the object created during the function execution
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        # Catch the exceptions where the database connections are not working
        except DatabaseIsDown as e:
            # Set the state for the app as degraded in the running case
            self._request.app['state']='Running - degraded'
            # Create the JSON object that will be returned in response adding the info reason why a database is down
            response_obj = {"state": self._request.app['state'], "error": "{} database is down".format(e)}
            # Give a HTTP response with json data application and a 200 status, and the object created during the function execution
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')