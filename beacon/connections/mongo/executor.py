import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args, level, LOG
from beacon.connections.mongo.__init__ import client
from beacon.exceptions.exceptions import NoPermissionsAvailable, DatabaseIsDown
from pymongo.errors import ConnectionFailure
from beacon.response.classes import MultipleDatasetsResponse
from beacon.request.classes import RequestAttributes
from beacon.utils.modules import get_all_modules_mongo_connections_script

@log_with_args(level)
async def execute_function(self, datasets: list):
    # Initiate the list where the different dataset classes are returned populated from the queries
    list_of_responses=[]
    # Get the function that will be the one to use for the query performed
    list_of_non_collection_modules = get_all_modules_mongo_connections_script("non_collections")
    for non_collection_module in list_of_non_collection_modules:
        try:
            function = getattr(non_collection_module, RequestAttributes.function)
        except Exception:
            continue
    # Get the current process where the app is being run
    loop = asyncio.get_running_loop()
    if datasets != []:
        # If there is more than one datasets to query, start a thread for each of the datasets and execute the previously chosen function in parallel and asynchronously
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        # When each of the queries finishes, append the dataset instance class populated in a list
        for task in done:
            responseClass= task.result()
            list_of_responses.append(responseClass)
    # When all the queries per dataset finish, return the array of datasets in a wrapper class of the single dataset instances
    try:
        return MultipleDatasetsResponse(datasets_responses=list_of_responses)
    except ConnectionFailure as e:
        #client.close() # No és el mateix que no trobi la base de dades que estigui malament la connexió.
        raise DatabaseIsDown(str(e))
    except Exception:
        raise NoPermissionsAvailable("No datasets found. Check out the permissions or the datasets requested if a response was expected.")
    
@log_with_args(level)
async def execute_collection_function(self):
    try:
        # Get the function that will be the one to use for the query performed
        list_of_collection_modules = get_all_modules_mongo_connections_script("collections")
        for collection_module in list_of_collection_modules:
            try:
                function = getattr(collection_module, RequestAttributes.function)
            except Exception:
                continue
        # Perform the query and return the class to return for the chosen collection
        collectionsResponseClass = function(self)
        return collectionsResponseClass
    except ConnectionFailure as e:
        #client.close()
        raise DatabaseIsDown(str(e))
