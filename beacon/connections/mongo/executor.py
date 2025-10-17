import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args, level, LOG
from beacon.connections.mongo.__init__ import client
from beacon.request.classes import RequestAttributes
from beacon.exceptions.exceptions import NoPermissionsAvailable, DatabaseIsDown
from pymongo.errors import ConnectionFailure
from beacon.connections.mongo.mappers import get_function, get_collections_function

@log_with_args(level)
async def execute_function(self, datasets: list):
    include = RequestAttributes.qparams.query.includeResultsetResponses
    datasets_docs={}
    datasets_count={}
    new_count=0

    function = get_function(self)

    loop = asyncio.get_running_loop()

    if datasets != []:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, dataset.dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            count, dataset_count, records, dataset = task.result()
            if include == 'ALL':
                if dataset_count != -1:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
            elif include == 'MISS':
                if dataset_count == 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
            else:
                if dataset_count != -1 and dataset_count != 0:
                    new_count+=dataset_count
                    datasets_docs[dataset]=records
                    datasets_count[dataset]=dataset_count
                else:
                    datasets = [x for x in datasets if x.dataset != dataset] 
        count=new_count
    try:
        return datasets_docs, datasets_count, count, include, datasets
    except ConnectionFailure as e:
        client.close()
        raise DatabaseIsDown(str(e))
    except Exception:
        raise NoPermissionsAvailable("No datasets found. Check out the permissions or the datasets requested if a response was expected.")
    

@log_with_args(level)
async def execute_collection_function(self):
    try:
        function = get_collections_function(self)
        response_converted, count = function(self)
        return response_converted, count
    except ConnectionFailure as e:
        client.close()
        raise DatabaseIsDown(str(e))
