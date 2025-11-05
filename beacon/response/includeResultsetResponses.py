from beacon.request.classes import RequestAttributes
from beacon.logs.logs import log_with_args, LOG, level
from beacon.response.classes import MultipleDatasetsResponse

@log_with_args(level)
def gather_final_datasets_to_return(self, responseClass, finalMultiDatasetsClass):
    finalMultiDatasetsClass.total_count+=responseClass.dataset_count
    finalMultiDatasetsClass.datasets_responses.append(responseClass)
    return finalMultiDatasetsClass

@log_with_args(level)
def include_resultSet_responses(self, multipleDatasetsClass):
    include = RequestAttributes.qparams.query.includeResultsetResponses
    finalMultiDatasetsClass = MultipleDatasetsResponse(total_count=0, datasets_responses=[])
    for dataset in multipleDatasetsClass.datasets_responses:
        if include == 'ALL':
            if dataset.dataset_count != -1:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
        elif include == 'MISS':
            if dataset.dataset_count == 0:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
        else:
            if dataset.dataset_count != -1 and dataset.dataset_count != 0:
                finalMultiDatasetsClass=gather_final_datasets_to_return(self, dataset, finalMultiDatasetsClass)
    return finalMultiDatasetsClass
