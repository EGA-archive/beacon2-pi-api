from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.entry_type_is_variant import cross_query_entry_type_is_genomicVariant_and_scope_is_not
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.scope_is_variant import cross_query_scope_is_genomicVariant_and_entry_type_is_not
from beacon.connections.mongo.filters.cross_queries.scope_is_not_entry_type import scope_is_not_entry_type
from beacon.connections.mongo.__init__ import genomicVariations, individuals, analyses, biosamples, runs, datasets
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_dataset_confile, import_analysis_confile, import_biosample_confile, import_cohort_confile, import_individual_confile, import_genomicVariant_confile, import_run_confile

@log_with_args(config.level)
def cross_query(self, query: dict, scope: str, request_parameters: dict, dataset: str):
    # Check for the different scopes and entry types to apply a different query syntax built.
    if scope == 'genomicVariation' and RequestAttributes.entry_type == genomicVariant_confile["endpoint_name"]:
        subquery={}
        subquery["$or"]=[]
        if request_parameters != {}:
            # If there are request parameters, get the ids of the query performed with the request parameters received
            listHGVS=[]
            queryHGVS={}
            HGVSIds = genomicVariations.find(request_parameters, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            for HGVSId in HGVSIds:
                justid=HGVSId["identifiers"]["genomicHGVSId"]
                listHGVS.append(justid)
            # Add the ids obtained in a dictionary
            queryHGVS["$in"]=listHGVS
            queryHGVSId={"datasetId": dataset, "identifiers.genomicHGVSId": queryHGVS}
            try:
                query["$and"] = []
                query["$and"].append(queryHGVSId)
            except Exception:
                pass
    else:
        # Import all the entry types configuration files
        biosample_confile=import_biosample_confile()
        analysis_confile=import_analysis_confile()
        run_confile=import_run_confile()
        genomicVariant_confile=import_genomicVariant_confile()
        individual_confile=import_individual_confile()
        cohort_confile=import_cohort_confile()
        dataset_confile=import_dataset_confile()
        # Initiate a list to get the final ids for the performed fist stage queries of the cross query
        def_list=[]             
        # Set the id to point at when performing the first stage queries (original_id) and the id for the second stage queries (final_id)  
        if scope == 'individual':
            mongo_collection=individuals
            original_id="id"
            final_id="individualId"
            if RequestAttributes.entry_type == genomicVariant_confile["endpoint_name"]:
                query=cross_query_entry_type_is_genomicVariant_and_scope_is_not(self,mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type in [run_confile["endpoint_name"],biosample_confile["endpoint_name"],analysis_confile["endpoint_name"]]:
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type == individual_confile["endpoint_name"]:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "individualId", query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type == biosample_confile["endpoint_name"]:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "id", query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type in [analysis_confile["endpoint_name"],run_confile["endpoint_name"]]:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "biosampleId", query, dataset)
        elif scope == 'run' and RequestAttributes.entry_type != run_confile["endpoint_name"]:
            mongo_collection=runs
            if RequestAttributes.entry_type == genomicVariant_confile["endpoint_name"]:
                original_id="biosampleId"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual_confile["endpoint_name"]:
                original_id="individualId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == analysis_confile["endpoint_name"]:
                original_id="biosampleId"
                final_id="biosampleId"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == biosample_confile["endpoint_name"]:
                original_id="biosampleId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type in [cohort_confile["endpoint_name"], dataset_confile["endpoint_name"]]:
                original_id="datasetId"
                final_id="datasetId"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'analysis' and RequestAttributes.entry_type != analysis_confile["endpoint_name"]:
            mongo_collection=analyses
            if RequestAttributes.entry_type == genomicVariant_confile["endpoint_name"]:
                original_id="biosampleId"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual_confile["endpoint_name"]:
                original_id="individualId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == run_confile["endpoint_name"]:
                original_id="biosampleId"
                final_id="biosampleId"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == biosample_confile["endpoint_name"]:
                original_id="biosampleId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type in [cohort_confile["endpoint_name"], dataset_confile["endpoint_name"]]:
                original_id="datasetId"
                final_id="datasetId"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'biosample' and RequestAttributes.entry_type != biosample_confile["endpoint_name"]:
            mongo_collection=biosamples
            if RequestAttributes.entry_type == genomicVariant_confile["endpoint_name"]:
                original_id="id"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual_confile["endpoint_name"]:
                original_id="individualId"
                final_id="id"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type in [analysis_confile["endpoint_name"], run_confile["endpoint_name"]]:
                original_id="id"
                final_id="biosampleId"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type in [cohort_confile["endpoint_name"], dataset_confile["endpoint_name"]]:
                original_id="datasetId"
                final_id="datasetId"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'dataset' and RequestAttributes.entry_type != dataset_confile["endpoint_name"]:
            query = scope_is_not_entry_type(self, "id", "datasetId", def_list, datasets, query, dataset)
        elif scope == 'cohort' and RequestAttributes.entry_type != cohort_confile["endpoint_name"]:
            query = scope_is_not_entry_type(self, "id", "datasetId", def_list, datasets, query, dataset)
    return query