import asyncio
from concurrent.futures import ThreadPoolExecutor
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from typing import Optional
from beacon.request.classes import RequestAttributes
from beacon.connections.beaconCLI.g_variants import get_variants

@log_with_args(level)
async def execute_function(self, entry_type: str, datasets: list, entry_id: Optional[str]):
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    datasets_docs={}
    datasets_count={}
    new_count=0
    function=get_variants

    loop = asyncio.get_running_loop()

    if datasets != [] and include != 'NONE':
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
            if dataset_count != -1:
                new_count+=dataset_count
                datasets_docs[dataset]=records
                datasets_count[dataset]=dataset_count
        
        count=new_count
    
    else:
        with ThreadPoolExecutor() as pool:
            done, pending = await asyncio.wait(fs=[loop.run_in_executor(pool, function, self, entry_id, dataset) for dataset in datasets],
            return_when=asyncio.ALL_COMPLETED
            )
        for task in done:
            entity_schema, count, dataset_count, records, dataset = task.result()
        datasets_docs["NONE"]=records
        if limit == 0 or new_count < limit:
            pass
        else:
            count = limit
        datasets_count["NONE"]=count
    return datasets_docs, datasets_count, count, entity_schema, include