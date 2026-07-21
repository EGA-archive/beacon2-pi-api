import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import NoPermissionsAvailable, DatabaseIsDown
from pymongo.errors import ConnectionFailure
from beacon.response.classes import MultipleDatasetsResponse
from beacon.request.classes import RequestAttributes
from beacon.utils.modules import get_all_modules_connections_script

@log_with_args(config.level)
async def execute_function(self, datasets: list):
    self.LOG.warning('at the executor')
    # Initiate the list where the different dataset classes are returned populated from the queries
    list_of_responses=[]
    # Get the function that will be the one to use for the query performed
    list_of_non_collection_modules = get_all_modules_connections_script("non_collections", "sqlalchemy_postgresql")
    self.LOG.warning(list_of_non_collection_modules)
    for non_collection_module in list_of_non_collection_modules:
        try:
            function = getattr(non_collection_module, RequestAttributes.function)
            self.LOG.warning(function)
        except Exception:
            continue
    # Get the current process where the app is being run
    loop = asyncio.get_running_loop()
    self.LOG.warning(datasets)
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
        #client.close() # It's not the same that it doesn't found the database than the connection is wrong
        raise DatabaseIsDown(str(e))
    except Exception:
        raise NoPermissionsAvailable("No datasets found. Check out the permissions or the datasets requested if a response was expected.")

