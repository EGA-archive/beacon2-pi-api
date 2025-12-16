from beacon.connections.mongo.__init__ import biosamples
from beacon.conf.conf_override import config
from beacon.logs.logs import log_with_args, LOG
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.get_biosampleIds import get_biosampleIds
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.get_total_query import get_total_query
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_analysis_confile, import_biosample_confile, import_individual_confile, import_run_confile


@log_with_args(config.level)
def request_parameters(self, total_query, request_parameters, dataset): 
    # Import all the configuration files for the entry types
    individual_confile=import_individual_confile()
    analysis_confile=import_analysis_confile()
    biosample_confile=import_biosample_confile()
    run_confile=import_run_confile()
    # Check wich is the entry type to know how to do the id translation for the request parameters (if any)
    if RequestAttributes.entry_type == individual_confile["individual"]["endpoint_name"]:
        biosampleIds=get_biosampleIds(self, request_parameters, dataset)
        try:
            # Build the query to get the individual ids from biosamples
            finalquery={}
            finalquery["$or"]=[]
            for finalid in biosampleIds:
                query = {"id": finalid}
                finalquery["$or"].append(query)
            individual_id = biosamples \
                .find(finalquery, {"individualId": 1, "_id": 0})
            # Just keep the individual ids
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
        # Build the query with the ids obtained previously
        finalquery={}
        finalquery["$or"]=[]
        for finalid in finalids:
            query = {"id": finalid}
            finalquery["$or"].append(query)
        try:
            total_query["$and"].append(finalquery)
        except Exception:
            total_query["$and"]=[]
            total_query["$and"].append(finalquery)
    elif RequestAttributes.entry_type == biosample_confile["biosample"]["endpoint_name"]:
        # Get the biosampleIds obtained from the request parameters query and build the query with these ids as id because is against biosamples.
        biosampleIds=get_biosampleIds(self, request_parameters, dataset)
        total_query=get_total_query(self, biosampleIds, total_query, "id")
    elif RequestAttributes.entry_type == analysis_confile["analysis"]["endpoint_name"] or RequestAttributes.entry_type == run_confile["run"]["endpoint_name"]:
        # Get the biosampleIds obtained from the request parameters query and build the query with these ids as id because is against analyses/runs.
        biosampleIds=get_biosampleIds(self, request_parameters, dataset)
        total_query=get_total_query(self, biosampleIds, total_query, "biosampleId")
    else:
        # As the query is pointing to variants, just build the query with the request parameters received
        try:
            total_query["$and"].append(request_parameters)
        except Exception:
            total_query["$and"]=[]
            total_query["$and"].append(request_parameters)
    return total_query