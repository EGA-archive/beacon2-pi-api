
import asyncio
from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import (
    NoPermissionsAvailable,
    DatabaseIsDown,
)
from pymongo.errors import ConnectionFailure
from beacon.response.classes import MultipleDatasetsResponse
from beacon.utils.modules import get_all_modules_connections_script

@log_with_args(config.level)
async def execute_function(self, datasets: list):
    # Resolve the requested function from the enabled model modules.
    modules = get_all_modules_connections_script(
        "non_collections", "mongo"
    )

    function = None
    for module in modules:
        candidate = getattr(
            module,
            self.request_attributes.function,
            None,
        )
        if callable(candidate):
            function = candidate
            break

    if function is None:
        raise RuntimeError(
            "Non-collection function not found: "
            f"{self.request_attributes.function}"
        )

    # Reuse the application-wide thread pool.
    loop = asyncio.get_running_loop()
    pool = self.request.app["db_pool"]

    if datasets:

        tasks = []
        for dataset in datasets:

            task = loop.run_in_executor(
                pool,
                function,
                self,
                dataset,
            )

            tasks.append(task)

        # Wait for all dataset operations to finish.
        try:
            responses = await asyncio.gather(*tasks)
        except ConnectionFailure as exc:
            raise DatabaseIsDown(str(exc)) from exc


        list_of_responses = [
            result
            for result in responses
        ]

    else:
        list_of_responses = []

    # Preserve the existing response format.
    try:
        return MultipleDatasetsResponse(
            datasets_responses=list_of_responses
        )
    except ConnectionFailure as exc:
        raise DatabaseIsDown(str(exc)) from exc
    except Exception as exc:
        raise NoPermissionsAvailable(
            "No datasets found. Check the permissions or "
            "the requested datasets if a response was expected."
        ) from exc
    
@log_with_args(config.level)
async def execute_collection_function(self):
    try:
        modules = get_all_modules_connections_script(
            "collections", "mongo"
        )

        function = None
        for module in modules:
            candidate = getattr(
                module, self.request_attributes.function, None
            )
            if callable(candidate):
                function = candidate
                break

        if function is None:
            raise RuntimeError(
                "Collection function not found: "
                f"{self.request_attributes.function}"
            )

        loop = asyncio.get_running_loop()
        pool = self.request.app["db_pool"]

        try:
            return await loop.run_in_executor(
                pool, function, self
            )
        except ConnectionFailure as exc:
            raise DatabaseIsDown(str(exc)) from exc

    except ConnectionFailure as exc:
        raise DatabaseIsDown(str(exc)) from exc
