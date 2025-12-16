from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.apply_request_parameters import apply_request_parameters
from beacon.connections.mongo.filters.filters import apply_filters
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id
from beacon.connections.mongo.__init__ import genomicVariations, targets as targets_, caseLevelData, biosamples, runs, cohorts, analyses, datasets, individuals
from beacon.connections.mongo.utils import get_count, get_documents_for_cohorts
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import get_phenotypic_cross_query_attributes
from beacon.response.classes import SingleDatasetResponse
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_analysis_confile, import_biosample_confile, import_genomicVariant_confile, import_individual_confile, import_run_confile

@log_with_args(config.level)
def get_phenotypic_endpoint(self, dataset: SingleDatasetResponse):
    # Initialize the boolean parameter to know if the request parameters come from query string.
    parameters_as_filters=False
    # Handle the request parameters and create the first built of the query.
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, dataset.dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}: # If there are request parameters that come from query string, reprocess the request parameters 
        query, parameters_as_filters = apply_request_parameters(self, {}, dataset.dataset)
        query_parameters={}
    elif query_parameters != {'$and': []}: # Else, continue with the previous query build
        query=query_parameters
    elif query_parameters == {'$and': []}: # If the parameters didn't produce any query, restart the query dictionary. 
        query_parameters = {}
        query={}
     # Process the filters
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, query_parameters, dataset.dataset)
    if query == {} and query_parameters != {} and parameters_as_filters == False: # If the filters and the parameters didn't build any query, just return the dataset.
        return dataset
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_phenotypic_endpoint_with_id(self, dataset: SingleDatasetResponse):
    genomicVariant_confile=import_genomicVariant_confile()
    # If the entry type records to return are variants, apply request parameters checking if they come by query string or not. Otherwise, just process the parameters as usual.
    if RequestAttributes.entry_type == genomicVariant_confile["genomicVariant"]["endpoint_name"]:
        query = {"$and": [{"_id": RequestAttributes.entry_id}]}
        query_parameters, parameters_as_filters = apply_request_parameters(self, query, dataset.dataset)
        if parameters_as_filters == True:
            query, parameters_as_filters = apply_request_parameters(self, {}, dataset.dataset)
            query_parameters={}
        else:
            query=query_parameters
    else:
        query, parameters_as_filters = apply_request_parameters(self, {}, dataset.dataset)
    # Process filters
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # If the entry type records are not variants, include the id queried in the query.
    if RequestAttributes.entry_type != genomicVariant_confile["genomicVariant"]["endpoint_name"]:
        query = query_id(self, query, RequestAttributes.entry_id)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_variants_of_phenotypic_endpoint(self, dataset: SingleDatasetResponse):
    analysis_confile=import_analysis_confile()
    run_confile=import_run_confile()
    # Check which is the queried initial entry type of the cross query and process and get the ids to convert to the final entry type response.
    LOG.warning(RequestAttributes.pre_entry_type)
    if RequestAttributes.pre_entry_type == analysis_confile["analysis"]["endpoint_name"] or RequestAttributes.pre_entry_type == run_confile["run"]["endpoint_name"]:
        query = {"$and": [{"id": RequestAttributes.entry_id}]}
        LOG.warning(query)
        query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
        if RequestAttributes.pre_entry_type == analysis_confile["analysis"]["endpoint_name"]:
            initial_ids = analyses \
                .find_one(query, {"biosampleId": 1, "_id": 0})
        else:
            initial_ids = runs \
                .find_one(query, {"biosampleId": 1, "_id": 0})  
        LOG.warning(dataset) 
        LOG.warning(initial_ids)
        try:
            RequestAttributes.entry_id = initial_ids["biosampleId"]
        except Exception:
            return dataset
    try:
        # Retrieve the ids per dataset.
        targets = targets_ \
            .find({"datasetId": dataset.dataset}, {"biosampleIds": 1, "_id": 0})
        position=0
        bioids=targets[0]["biosampleIds"]
    except Exception:
        return dataset
    # Map the ids and check which is the position fo the id found in the array of ids.
    for bioid in bioids:
        if bioid == RequestAttributes.entry_id:
            break
        position+=1
    if position == len(bioids):
        return dataset
    position=str(position)
    # Query the caseLevelData to get the variants that are related to these ids.
    query_cl={"$or": [{ position: "10", "datasetId": dataset.dataset},{ position: "11", "datasetId": dataset.dataset}, { position: "01", "datasetId": dataset.dataset}, { position: "y", "datasetId": dataset.dataset}]}
    string_of_ids = caseLevelData \
        .find(query_cl, {"id": 1, "_id": 0}).limit(RequestAttributes.qparams.query.pagination.limit).skip(RequestAttributes.qparams.query.pagination.skip)
    HGVSIds=list(string_of_ids)
    # Build the query using the identifiers.genomicHGVSId
    query={}
    queryHGVS={}
    listHGVS=[]
    for HGVSId in HGVSIds:
        justid=HGVSId["id"]
        listHGVS.append(justid)
    queryHGVS["$in"]=listHGVS
    query["identifiers.genomicHGVSId"]=queryHGVS
    # Apply request parameters
    query, parameters_as_filters = apply_request_parameters(self, query, dataset.dataset)
    # Process filters
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_phenotypic_endpoint_of_variants(self, dataset: SingleDatasetResponse):
    # Add the variantInternalId of the variant to the query constructor.
    query = {"$and": [{"_id": RequestAttributes.entry_id}]}
    # Handle the request parameters and create the first built of the query.
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, dataset.dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}: # If there are request parameters that come from query string, reprocess the request parameters
        query, parameters_as_filters = apply_request_parameters(self, query, dataset.dataset)
        query_parameters={}
    elif query_parameters != {'$and': []}: # Else, continue with the previous query build
        query=query_parameters
    elif query_parameters == {'$and': []}: # If the parameters didn't produce any query, restart the query dictionary.
        query_parameters = {}
        query={}
    # Execute the query to get all the identifiers.genomicHGVSIds
    HGVSIds = genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    # Build the new query to targets, that will relate the variants to the other entry type by relating the identifiers.genomicHGVSId to the list of ids using caseLevelData.
    HGVSIds=list(HGVSIds)
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset.dataset != HGVSDataset:
        dataset.dataset_count=0
        dataset.exists=False
        dataset.exists=False
        dataset.docs=[]
        return dataset
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": HGVSDataset, "id": HGVSId}
    string_of_ids = caseLevelData \
        .find(queryHGVSId)
    try:
        targets = targets_ \
            .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
        targets=list(targets)
        list_of_targets=targets[0]["biosampleIds"]
        list_of_positions_strings= string_of_ids[0]
    except Exception:
        dataset.dataset_count=0
        dataset.exists=False
        dataset.docs=[]
        return dataset
    # Initialize the biosampleIds array obtained from variants.
    biosampleIds=[]
    biosampleIds_restricted=[]
    filters=RequestAttributes.qparams.query.filters
    new_filters=[]
    if filters != []: # If there are filters, check if there are zygosity filters.
        for filter in filters:
            if filter['id']=='GENO:0000458': # If there is any filter of homozygosity, collect only those ids.
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                RequestAttributes.qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:0000136': # If there is any filter of heterozygosity, collect only those ids.
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01' and value != 'y':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                RequestAttributes.qparams.query.filters.remove(filter)
            else: # Otherwise, collect all the ids.
                new_filters.append(filter)
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else: # Otherwise, collect all the ids.
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    # Check if there are any ids that need to be removed because of the zygosity.
    if biosampleIds_restricted != [] and biosampleIds != []:
        for biosampleId in biosampleIds:
            if biosampleId not in biosampleIds_restricted:
                biosampleIds.remove(biosampleId)
    elif biosampleIds_restricted != [] and biosampleIds == []:
        biosampleIds = biosampleIds_restricted
    individual_confile=import_individual_confile()
    biosample_confile=import_biosample_confile()
    # Build the query translating the biosampleIds to individualIds in case the entry type needed is individuals.
    if RequestAttributes.entry_type != individual_confile["individual"]["endpoint_name"]:
        finalids=biosampleIds
        try:
            finalids=[]
            if RequestAttributes.entry_type == biosample_confile["biosample"]["endpoint_name"]:
                idq = 'id'
            else:
                idq = 'biosampleId'
            for bioid in biosampleIds:
                finalids.append({idq: bioid})
        except Exception:
            finalids=[]
        superfinalquery = {"$and": [{"$or": finalids}]}
    else:
        try:
            finalquery={}
            finalquery["$or"]=[]
            for finalid in biosampleIds:
                query = {"id": finalid}
                finalquery["$or"].append(query)
            individual_id = biosamples \
                .find(finalquery, {"individualId": 1, "_id": 0})
            try:
                finalids=[]
                for indid in individual_id:
                    finalids.append(indid["individualId"])
            except Exception:
                finalids=[]
            if finalids==[]:
                finalids=biosampleIds
        except Exception:
            finalids=biosampleIds
        finalquery={}
        finalquery["$or"]=[]
        for finalid in finalids:
            query = {"id": finalid}
            finalquery["$or"].append(query)
        superfinalquery={}
        superfinalquery["$and"]=[finalquery]
    # Process filters
    query = apply_filters(self, superfinalquery, new_filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_variants_of_dataset(self, dataset: SingleDatasetResponse):
    # Initialize the query syntax.
    query_count={}
    query_count["$or"]=[]
    # If the entry_id belongs to any dataset, build the query, otherwise, dataset is not found.
    if dataset.dataset == RequestAttributes.entry_id:
        queryid={}
        queryid["datasetId"]=dataset
        query_count["$or"].append(queryid)
    else:
        dataset.dataset_count=0
        dataset.exists=False
        return dataset
    # Process filters
    query = apply_filters(self, query_count, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_phenotypic_endpoint_of_dataset(self, dataset: SingleDatasetResponse):
    # Process filters
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Add the dataset id requested in the query syntax.
    query = query_id(self, query, RequestAttributes.entry_id)
    # If the entry_id belongs to any dataset, build the query, otherwise, dataset is not found.
    dict_in={}
    if dataset.dataset == RequestAttributes.entry_id:
        dict_in['datasetId']=RequestAttributes.entry_id
    else:
        dataset.dataset_count=0
        dataset.exists=False
        return dataset
    # Process filters
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_phenotypic_endpoint_of_cohort(self, dataset: SingleDatasetResponse):
    # Make an initial query to translate the datasetId into cohort id.
    dataset_found = cohorts \
        .find({"id": RequestAttributes.entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    # If the entry_id belongs to any dataset, build the query, otherwise, dataset is not found.
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset.dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        dataset.dataset_count=0
        dataset.exists=False
        return dataset
    # Process filters
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    limit = RequestAttributes.qparams.query.pagination.limit
    include = RequestAttributes.qparams.query.includeResultsetResponses
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_variants_of_cohort(self, dataset: SingleDatasetResponse):
    # Save the include, limit and skip parameters so they are used later.
    limit = RequestAttributes.qparams.query.pagination.limit
    include = RequestAttributes.qparams.query.includeResultsetResponses
    skip = RequestAttributes.qparams.query.pagination.skip
    # Make an initial query to translate the datasetId into cohort id.
    dataset_found = cohorts \
        .find({"id": RequestAttributes.entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    # If the entry_id belongs to any dataset, build the query, otherwise, dataset is not found.
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset.dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        dataset.dataset_count=0
        dataset.exists=False
        return dataset
    # Process filters
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Get the datasets ids found in the cohorts, otherwise, dataset for the cohort is not found.
    query_count={}
    query_count["$or"]=[]
    docs = get_documents_for_cohorts(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    for doc in docs:
        if doc["datasetId"] == dataset.dataset:
            RequestAttributes.entry_id = dataset.dataset
    if dataset.dataset == RequestAttributes.entry_id:
        queryid={}
        queryid["datasetId"]=dataset.dataset
        query_count["$or"].append(queryid)
    else:
        dataset.dataset_count=0
        dataset.exists=False
        return dataset
    # Process filters.
    query = apply_filters(self, query_count, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(config.level)
def get_phenotypic_cross_query(self, dataset: SingleDatasetResponse):
    # Get the translation of ids for the entry types lookup for the cross query.
    mapping = get_phenotypic_cross_query_attributes(self, RequestAttributes.entry_type, RequestAttributes.pre_entry_type)
    # Get the ids found for the initial entry type query.
    items_found = mapping["secondary_collection"] \
    .find({"id": RequestAttributes.entry_id, "datasetId": dataset.dataset}, {mapping["idq2"]: 1, "_id": 0})
    # Translate the ids.
    list_of_itemsfound=[]
    for itemfound in items_found:
        list_of_itemsfound.append(itemfound[mapping["idq2"]])
    query = {mapping["idq"]: {"$in": list_of_itemsfound}}
    # Process filters.
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass
