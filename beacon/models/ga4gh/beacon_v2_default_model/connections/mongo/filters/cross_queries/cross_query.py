from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.entry_type_is_variant import cross_query_entry_type_is_genomicVariant_and_scope_is_not
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.scope_is_variant import cross_query_scope_is_genomicVariant_and_entry_type_is_not
from beacon.connections.mongo.filters.cross_queries.scope_is_not_entry_type import scope_is_not_entry_type
from beacon.connections.mongo.__init__ import genomicVariations, individuals, analyses, biosamples, runs
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.request.classes import RequestAttributes

@log_with_args(level)
def cross_query(self, query: dict, scope: str, request_parameters: dict, dataset: str):
    if scope == 'genomicVariation' and RequestAttributes.entry_type == genomicVariant.endpoint_name:
        subquery={}
        subquery["$or"]=[]
        if request_parameters != {}:
            listHGVS=[]
            queryHGVS={}
            HGVSIds = genomicVariations.find(request_parameters, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            for HGVSId in HGVSIds:
                justid=HGVSId["identifiers"]["genomicHGVSId"]
                listHGVS.append(justid)
            queryHGVS["$in"]=listHGVS
            queryHGVSId={"datasetId": dataset, "identifiers.genomicHGVSId": queryHGVS}
            try:
                query["$and"] = []
                query["$and"].append(queryHGVSId)
            except Exception:
                pass
    else:
        def_list=[]                
        if scope == 'individual':
            mongo_collection=individuals
            original_id="id"
            final_id="individualId"
            if RequestAttributes.entry_type == genomicVariant.endpoint_name:
                query=cross_query_entry_type_is_genomicVariant_and_scope_is_not(self,mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type in [run.endpoint_name,biosample.endpoint_name,analysis.endpoint_name]:
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type == individual.endpoint_name:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "individualId", query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type == biosample.endpoint_name:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "id", query, dataset)
        elif scope == 'genomicVariation' and RequestAttributes.entry_type in [analysis.endpoint_name,run.endpoint_name]:
            query = cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, "biosampleId", query, dataset)
        elif scope == 'run' and RequestAttributes.entry_type != run.endpoint_name:
            mongo_collection=runs
            if RequestAttributes.entry_type == genomicVariant.endpoint_name:
                original_id="biosampleId"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual.endpoint_name:
                original_id="individualId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == analysis.endpoint_name:
                original_id="biosampleId"
                final_id="biosampleId"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == biosample.endpoint_name:
                original_id="biosampleId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'analysis' and RequestAttributes.entry_type != analysis.endpoint_name:
            mongo_collection=analyses
            if RequestAttributes.entry_type == genomicVariant.endpoint_name:
                original_id="biosampleId"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual.endpoint_name:
                original_id="individualId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == run.endpoint_name:
                original_id="biosampleId"
                final_id="biosampleId"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type == biosample.endpoint_name:
                original_id="biosampleId"
                final_id="id"
                query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
        elif scope == 'biosample' and RequestAttributes.entry_type != biosample.endpoint_name:
            mongo_collection=biosamples
            if RequestAttributes.entry_type == genomicVariant.endpoint_name:
                original_id="id"
                query = cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset)
            elif RequestAttributes.entry_type == individual.endpoint_name:
                original_id="individualId"
                final_id="id"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
            elif RequestAttributes.entry_type in [analysis.endpoint_name, run.endpoint_name]:
                original_id="id"
                final_id="biosampleId"
                query = scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
    return query