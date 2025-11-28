from beacon.request.classes import RequestAttributes
from beacon.logs.logs import log_with_args, LOG, level
from beacon.response.classes import MultipleDatasetsResponse

@log_with_args(level)
def gather_final_datasets_to_return(self, responseClass, finalMultiDatasetsClass):
    # Get the total count adding up the different datasets' counts for the responses and instantiate the dataset instance and the total counts in a wrapper class.
    finalMultiDatasetsClass.total_count+=responseClass.dataset_count
    finalMultiDatasetsClass.datasets_responses.append(responseClass)
    return finalMultiDatasetsClass

@log_with_args(level)
def include_resultSet_responses(self, multipleDatasetsClass):
    # Load the include resultSet response from the request attributes.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    # Start a multiple datasets class that is empty.
    finalMultiDatasetsClass = MultipleDatasetsResponse(total_count=0, datasets_responses=[])
    for dataset in multipleDatasetsClass.datasets_responses:
        if include == 'ALL':
            # In case the resultSets response is ALL, insert all the datasets found in the database in the multiple datasets class that was empty.
            if dataset.exists != None:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
        elif include == 'MISS':
            # In case the resultSets response is MISS, insert the datasets that have negative answer to the query in the multiple datasets class that was empty.
            if dataset.dataset_count == 0:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
        else:
            # In case the resultSets response is HIT, insert the datasets that have positive answer to the query in the multiple datasets class that was empty.
            if dataset.exists == True and dataset.dataset_count != 0:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
    return finalMultiDatasetsClass
