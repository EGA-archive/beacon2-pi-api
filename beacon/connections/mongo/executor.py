import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args, level, LOG
from beacon.connections.mongo.__init__ import client
from beacon.exceptions.exceptions import NoPermissionsAvailable, DatabaseIsDown
from pymongo.errors import ConnectionFailure
from beacon.connections.mongo.mappers import get_function, get_collections_function
from beacon.response.classes import MultipleDatasetsResponse

@log_with_args(level)
async def execute_function(self, datasets: list):
    list_of_responses=[]
    function = get_function(self)
    loop = asyncio.get_running_loop()
    if datasets != []:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            responseClass= task.result()
            list_of_responses.append(responseClass)
    try:
        return MultipleDatasetsResponse(datasets_responses=list_of_responses, datasets=datasets)
    except ConnectionFailure as e:
        #client.close() # No és el mateix que no trobi la base de dades que estigui malament la connexió.
        raise DatabaseIsDown(str(e))
    except Exception:
        raise NoPermissionsAvailable("No datasets found. Check out the permissions or the datasets requested if a response was expected.")
    
@log_with_args(level)
async def execute_collection_function(self):
    try:
        function = get_collections_function(self)
        collectionsResponseClass = function(self)
        return collectionsResponseClass
    except ConnectionFailure as e:
        #client.close()
        raise DatabaseIsDown(str(e))
