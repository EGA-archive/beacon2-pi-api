from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams, RequestMeta, RequestQuery
from beacon.request.classes import Granularity, ErrorClass, RequestAttributes
from beacon.conf import conf
from typing import Optional
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.filtering_terms.resources import resources
from beacon.utils.handovers import list_of_handovers, list_of_handovers_per_dataset
import json
import math

@log_with_args(level)
def generate_endpoints(self, response_type, key_response):
    with open('beacon/response/templates/{}.json'.format(response_type), 'r') as template:
        response = json.load(template)

    if analysis.endpoint_name!='':
        response[key_response][analysis.id]=response[key_response]['analysis']
        response[key_response][analysis.id]["entryType"]=analysis.id
        response[key_response][analysis.id]["openAPIEndpointsDefinition"]=analysis.open_api_endpoints_definition
        response[key_response][analysis.id]["rootUrl"]=conf.complete_url+'/'+analysis.endpoint_name
        if analysis.singleEntryUrl == True:
            response[key_response][analysis.id]["singleEntryUrl"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}'
        else:
            del response[key_response][analysis.id]["singleEntryUrl"]
        if analysis.biosample_lookup == True:
            response[key_response][analysis.id]["endpoints"][biosample.id]=response[key_response][analysis.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][analysis.id]["endpoints"]["biosample"]
            response[key_response][analysis.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][analysis.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name
        if analysis.cohort_lookup == True:
            response[key_response][analysis.id]["endpoints"][cohort.id]=response[key_response][analysis.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][analysis.id]["endpoints"]["cohort"]
            response[key_response][analysis.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][analysis.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name
        if analysis.dataset_lookup == True:
            response[key_response][analysis.id]["endpoints"][dataset.id]=response[key_response][analysis.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][analysis.id]["endpoints"]["dataset"]
            response[key_response][analysis.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][analysis.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name
        if analysis.genomicVariant_lookup == True:
            response[key_response][analysis.id]["endpoints"][genomicVariant.id]=response[key_response][analysis.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][analysis.id]["endpoints"]["genomicVariant"]
            response[key_response][analysis.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][analysis.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if analysis.individual_lookup == True:
            response[key_response][analysis.id]["endpoints"][individual.id]=response[key_response][analysis.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][analysis.id]["endpoints"]["individual"]
            response[key_response][analysis.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][analysis.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name
        if analysis.run_lookup == True:
            response[key_response][analysis.id]["endpoints"][run.id]=response[key_response][analysis.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][analysis.id]["endpoints"]["run"]
            response[key_response][analysis.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][analysis.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name
    if biosample.endpoint_name!='':
        response[key_response][biosample.id]=response[key_response]['biosample']
        response[key_response][biosample.id]["entryType"]=biosample.id
        response[key_response][biosample.id]["openAPIEndpointsDefinition"]=biosample.open_api_endpoints_definition
        response[key_response][biosample.id]["rootUrl"]=conf.complete_url+'/'+biosample.endpoint_name
        if biosample.singleEntryUrl == True:
            response[key_response][biosample.id]["singleEntryUrl"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}'
        else:
            del response[key_response][biosample.id]["singleEntryUrl"]
        if biosample.analysis_lookup == True:
            response[key_response][biosample.id]["endpoints"][analysis.id]=response[key_response][biosample.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][biosample.id]["endpoints"]["analysis"]
            response[key_response][biosample.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][biosample.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name
        if biosample.cohort_lookup == True:
            response[key_response][biosample.id]["endpoints"][cohort.id]=response[key_response][biosample.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][biosample.id]["endpoints"]["cohort"]
            response[key_response][biosample.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][biosample.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name
        if biosample.dataset_lookup == True:
            response[key_response][biosample.id]["endpoints"][dataset.id]=response[key_response][biosample.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][biosample.id]["endpoints"]["dataset"]
            response[key_response][biosample.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][biosample.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name
        if biosample.genomicVariant_lookup == True:
            response[key_response][biosample.id]["endpoints"][genomicVariant.id]=response[key_response][biosample.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][biosample.id]["endpoints"]["genomicVariant"]
            response[key_response][biosample.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][biosample.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if biosample.individual_lookup == True:
            response[key_response][biosample.id]["endpoints"][individual.id]=response[key_response][biosample.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][biosample.id]["endpoints"]["individual"]
            response[key_response][biosample.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][biosample.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name
        if biosample.run_lookup == True:
            response[key_response][biosample.id]["endpoints"][run.id]=response[key_response][biosample.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][biosample.id]["endpoints"]["run"]
            response[key_response][biosample.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][biosample.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name
    if cohort.endpoint_name!='':
        response[key_response][cohort.id]=response[key_response]['cohort']
        response[key_response][cohort.id]["entryType"]=cohort.id
        response[key_response][cohort.id]["openAPIEndpointsDefinition"]=cohort.open_api_endpoints_definition
        response[key_response][cohort.id]["rootUrl"]=conf.complete_url+'/'+cohort.endpoint_name
        if cohort.singleEntryUrl == True:
            response[key_response][cohort.id]["singleEntryUrl"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}'
        else:
            del response[key_response][cohort.id]["singleEntryUrl"]
        if cohort.analysis_lookup == True:
            response[key_response][cohort.id]["endpoints"][analysis.id]=response[key_response][cohort.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][cohort.id]["endpoints"]["analysis"]
            response[key_response][cohort.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][cohort.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name
        if cohort.biosample_lookup == True:
            response[key_response][cohort.id]["endpoints"][biosample.id]=response[key_response][cohort.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][cohort.id]["endpoints"]["biosample"]
            response[key_response][cohort.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][cohort.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name
        if cohort.dataset_lookup == True:
            response[key_response][cohort.id]["endpoints"][dataset.id]=response[key_response][cohort.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][cohort.id]["endpoints"]["dataset"]
            response[key_response][cohort.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][cohort.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name
        if cohort.genomicVariant_lookup == True:
            response[key_response][cohort.id]["endpoints"][genomicVariant.id]=response[key_response][cohort.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][cohort.id]["endpoints"]["genomicVariant"]
            response[key_response][cohort.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][cohort.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if cohort.individual_lookup == True:
            response[key_response][cohort.id]["endpoints"][individual.id]=response[key_response][cohort.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][cohort.id]["endpoints"]["individual"]
            response[key_response][cohort.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][cohort.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name
        if cohort.run_lookup == True:
            response[key_response][cohort.id]["endpoints"][run.id]=response[key_response][cohort.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][cohort.id]["endpoints"]["run"]
            response[key_response][cohort.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][cohort.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name
    if dataset.endpoint_name!='':
        response[key_response][dataset.id]=response[key_response]['dataset']
        response[key_response][dataset.id]["entryType"]=dataset.id
        response[key_response][dataset.id]["openAPIEndpointsDefinition"]=dataset.open_api_endpoints_definition
        response[key_response][dataset.id]["rootUrl"]=conf.complete_url+'/'+dataset.endpoint_name
        if dataset.singleEntryUrl == True:
            response[key_response][dataset.id]["singleEntryUrl"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}'
        else:
            del response[key_response][dataset.id]["singleEntryUrl"]
        if dataset.analysis_lookup == True:
            response[key_response][dataset.id]["endpoints"][analysis.id]=response[key_response][dataset.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][dataset.id]["endpoints"]["analysis"]
            response[key_response][dataset.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][dataset.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name
        if dataset.biosample_lookup == True:
            response[key_response][dataset.id]["endpoints"][biosample.id]=response[key_response][dataset.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][dataset.id]["endpoints"]["biosample"]
            response[key_response][dataset.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][dataset.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name
        if dataset.cohort_lookup == True:
            response[key_response][dataset.id]["endpoints"][cohort.id]=response[key_response][dataset.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][dataset.id]["endpoints"]["dataset"]
            response[key_response][dataset.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][dataset.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name
        if dataset.genomicVariant_lookup == True:
            response[key_response][dataset.id]["endpoints"][genomicVariant.id]=response[key_response][dataset.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][dataset.id]["endpoints"]["genomicVariant"]
            response[key_response][dataset.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][dataset.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if dataset.individual_lookup == True:
            response[key_response][dataset.id]["endpoints"][individual.id]=response[key_response][dataset.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][dataset.id]["endpoints"]["individual"]
            response[key_response][dataset.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][dataset.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name
        if dataset.run_lookup == True:
            response[key_response][dataset.id]["endpoints"][run.id]=response[key_response][dataset.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][dataset.id]["endpoints"]["run"]
            response[key_response][dataset.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][dataset.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name
    if genomicVariant.endpoint_name!='':
        response[key_response][genomicVariant.id]=response[key_response]['genomicVariant']
        response[key_response][genomicVariant.id]["entryType"]=genomicVariant.id
        response[key_response][genomicVariant.id]["openAPIEndpointsDefinition"]=genomicVariant.open_api_endpoints_definition
        response[key_response][genomicVariant.id]["rootUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name
        if genomicVariant.singleEntryUrl == True:
            response[key_response][genomicVariant.id]["singleEntryUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}'
        else:
            del response[key_response][genomicVariant.id]["singleEntryUrl"]
        if genomicVariant.analysis_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][analysis.id]=response[key_response][genomicVariant.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][genomicVariant.id]["endpoints"]["analysis"]
            response[key_response][genomicVariant.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][genomicVariant.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name
        if genomicVariant.biosample_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][biosample.id]=response[key_response][genomicVariant.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][genomicVariant.id]["endpoints"]["biosample"]
            response[key_response][genomicVariant.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][genomicVariant.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name
        if genomicVariant.cohort_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][cohort.id]=response[key_response][genomicVariant.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][genomicVariant.id]["endpoints"]["genomicVariant"]
            response[key_response][genomicVariant.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][genomicVariant.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name
        if genomicVariant.dataset_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][dataset.id]=response[key_response][genomicVariant.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][genomicVariant.id]["endpoints"]["dataset"]
            response[key_response][genomicVariant.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][genomicVariant.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name
        if genomicVariant.individual_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][individual.id]=response[key_response][genomicVariant.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][genomicVariant.id]["endpoints"]["individual"]
            response[key_response][genomicVariant.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][genomicVariant.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name
        if genomicVariant.run_lookup == True:
            response[key_response][genomicVariant.id]["endpoints"][run.id]=response[key_response][genomicVariant.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][genomicVariant.id]["endpoints"]["run"]
            response[key_response][genomicVariant.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][genomicVariant.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name
    if individual.endpoint_name!='':
        response[key_response][individual.id]=response[key_response]['individual']
        response[key_response][individual.id]["entryType"]=individual.id
        response[key_response][individual.id]["openAPIEndpointsDefinition"]=individual.open_api_endpoints_definition
        response[key_response][individual.id]["rootUrl"]=conf.complete_url+'/'+individual.endpoint_name
        if individual.singleEntryUrl == True:
            response[key_response][individual.id]["singleEntryUrl"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}'
        else:
            del response[key_response][individual.id]["singleEntryUrl"]
        if individual.analysis_lookup == True:
            response[key_response][individual.id]["endpoints"][analysis.id]=response[key_response][individual.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][individual.id]["endpoints"]["analysis"]
            response[key_response][individual.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][individual.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name
        if individual.biosample_lookup == True:
            response[key_response][individual.id]["endpoints"][biosample.id]=response[key_response][individual.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][individual.id]["endpoints"]["biosample"]
            response[key_response][individual.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][individual.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name
        if individual.cohort_lookup == True:
            response[key_response][individual.id]["endpoints"][cohort.id]=response[key_response][individual.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][individual.id]["endpoints"]["individual"]
            response[key_response][individual.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][individual.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name
        if individual.dataset_lookup == True:
            response[key_response][individual.id]["endpoints"][dataset.id]=response[key_response][individual.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][individual.id]["endpoints"]["dataset"]
            response[key_response][individual.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][individual.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name
        if individual.genomicVariant_lookup == True:
            response[key_response][individual.id]["endpoints"][genomicVariant.id]=response[key_response][individual.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][individual.id]["endpoints"]["genomicVariant"]
            response[key_response][individual.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][individual.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if individual.run_lookup == True:
            response[key_response][individual.id]["endpoints"][run.id]=response[key_response][individual.id]["endpoints"]["run"]
            if run.id != 'run':
                del response[key_response][individual.id]["endpoints"]["run"]
            response[key_response][individual.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            response[key_response][individual.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name
    if run.endpoint_name!='':
        response[key_response][run.id]=response[key_response]['run']
        response[key_response][run.id]["entryType"]=run.id
        response[key_response][run.id]["openAPIEndpointsDefinition"]=run.open_api_endpoints_definition
        response[key_response][run.id]["rootUrl"]=conf.complete_url+'/'+run.endpoint_name
        if run.singleEntryUrl == True:
            response[key_response][run.id]["singleEntryUrl"]=conf.complete_url+'/'+run.endpoint_name+'/{id}'
        else:
            del response[key_response][run.id]["singleEntryUrl"]
        if run.analysis_lookup == True:
            response[key_response][run.id]["endpoints"][analysis.id]=response[key_response][run.id]["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del response[key_response][run.id]["endpoints"]["analysis"]
            response[key_response][run.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            response[key_response][run.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name
        if run.biosample_lookup == True:
            response[key_response][run.id]["endpoints"][biosample.id]=response[key_response][run.id]["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del response[key_response][run.id]["endpoints"]["biosample"]
            response[key_response][run.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            response[key_response][run.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name
        if run.cohort_lookup == True:
            response[key_response][run.id]["endpoints"][cohort.id]=response[key_response][run.id]["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del response[key_response][run.id]["endpoints"]["run"]
            response[key_response][run.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            response[key_response][run.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name
        if run.dataset_lookup == True:
            response[key_response][run.id]["endpoints"][dataset.id]=response[key_response][run.id]["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del response[key_response][run.id]["endpoints"]["dataset"]
            response[key_response][run.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            response[key_response][run.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name
        if run.genomicVariant_lookup == True:
            response[key_response][run.id]["endpoints"][genomicVariant.id]=response[key_response][run.id]["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del response[key_response][run.id]["endpoints"]["genomicVariant"]
            response[key_response][run.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            response[key_response][run.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if run.individual_lookup == True:
            response[key_response][run.id]["endpoints"][individual.id]=response[key_response][run.id]["endpoints"]["individual"]
            if individual.id != 'individual':
                del response[key_response][run.id]["endpoints"]["individual"]
            response[key_response][run.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            response[key_response][run.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name
    return response

@log_with_args(level)
def build_response(self, data, num_total_results, qparams):
    """"Fills the `response` part with the correct format in `results`"""
    limit = qparams.query.pagination.limit
    include = qparams.query.includeResultsetResponses
    if limit != 0 and limit < num_total_results:# pragma: no cover
        response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': limit,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }
    else:# pragma: no cover
        response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': num_total_results,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }

    return response

@log_with_args(level)
def build_response_summary(self, exists, num_total_results):
    try:
        if num_total_results is None:# pragma: no cover
            return {
                'exists': exists
            }
        else:
            return {
                'exists': exists,
                'numTotalResults': num_total_results
            }
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_response_summary_by_dataset(self, datasets, data, dict_counts, qparams):
    try:
        count=0
        non_counted=0
        granularity = qparams.query.requestedGranularity
        for dataset in datasets:
            if dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':
                if conf.imprecise_count !=0:
                    if dict_counts[dataset.dataset] < conf.imprecise_count:
                        count+=conf.imprecise_count
                elif conf.round_to_tens == True:
                    count+=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                elif conf.round_to_hundreds == True:
                    count+=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                else:
                    count +=dict_counts[dataset.dataset]
            else:
                non_counted+=dict_counts[dataset.dataset]
        if count == 0 and non_counted >0:
            return {
                'exists': True
            }
        elif count > 0:
            return {
                'exists': count > 0,
                'numTotalResults': count
            }
        else:
            return {
                'exists': False
            }
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_meta(self, qparams: RequestParams, entity_schema: Optional[DefaultSchemas], returned_granularity: Granularity):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedGranularity': returned_granularity,
            'receivedRequestSummary': qparams.summary(),
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception:
        try:
            meta = {
                'beaconId': conf.beacon_id,
                'apiVersion': conf.api_version,
                'returnedGranularity': returned_granularity,
                'receivedRequestSummary': qparams,
                'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
            }
            return meta
        except Exception as e:# pragma: no cover
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise

@log_with_args(level)
def build_info_meta(self, entity_schema: Optional[DefaultSchemas]):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception:# pragma: no cover
        try:
            meta = {
                'beaconId': conf.beacon_id,
                'apiVersion': conf.api_version,
                'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
            }
            return meta
        except Exception as e:
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise

@log_with_args(level)
def build_response_by_dataset(self, datasets, data, dict_counts, qparams):
    try:
        granularity = qparams.query.requestedGranularity
        list_of_responses=[]
        for dataset in datasets:
            if dataset.granularity == 'record' and RequestAttributes.allowed_granularity=='record' and granularity =='record':
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:# pragma: no cover
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0,
                            'resultsCount': dict_counts[dataset.dataset],
                            'results': data[dataset.dataset],
                            # 'info': None,
                            'resultsHandover': handover["handover"]  # build_results_handover
                            
                        }
                    else:
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0,
                            'resultsCount': dict_counts[dataset.dataset],
                            'results': data[dataset.dataset]
                        }
                if conf.imprecise_count !=0:
                    if dict_counts[dataset.dataset] < conf.imprecise_count:
                        response['resultsCount']=conf.imprecise_count
                        response['countAdjustedTo']=[conf.imprecise_count]
                        response['countPrecision']='imprecise'
                elif conf.round_to_tens == True:
                    response['resultsCount']=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                    response['countAdjustedTo']=['immediate ten']
                    response['countPrecision']='rounded'
                elif conf.round_to_hundreds == True:
                    response['resultsCount']=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                    response['countAdjustedTo']=['immediate hundred']
                    response['countPrecision']='rounded'
            elif dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:# pragma: no cover
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0,
                            'resultsCount': dict_counts[dataset.dataset],
                            # 'info': None,
                            'resultsHandover': handover["handover"]  # build_results_handover
                        }
                    else:
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0,
                            'resultsCount': dict_counts[dataset.dataset]
                        }
            else:
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:# pragma: no cover
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0,
                            # 'info': None,
                            'resultsHandover': handover["handover"]  # build_results_handover
                        }
                    else:
                        response = {
                            'id': dataset.dataset, # TODO: Set the name of the dataset/cohort
                            'setType': 'dataset', # TODO: Set the type of collection
                            'exists': dict_counts[dataset.dataset] > 0
                        }

            list_of_responses.append(response)

        return list_of_responses
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_record_response_by_dataset(self, datasets, data,
                                    dict_counts,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        if RequestAttributes.allowed_granularity == 'boolean':
            granul_returned = 'boolean'
        elif RequestAttributes.allowed_granularity in ['count', 'record'] and qparams.query.requestedGranularity == 'boolean':
            granul_returned = 'boolean'
        elif RequestAttributes.allowed_granularity == 'record' and qparams.query.requestedGranularity == 'record':
            granul_returned = 'record'
        else:
            granul_returned = 'count'
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, granul_returned),
            'responseSummary': build_response_summary_by_dataset(self, datasets, data, dict_counts, qparams),
            'response': {
                'resultSets': build_response_by_dataset(self, datasets, data, dict_counts, qparams)
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_boolean_response(self,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:# pragma: no cover
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.BOOLEAN),
            'responseSummary': build_response_summary(self, num_total_results > 0, None),
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_count_response(self, datasets, data,
                                    dict_counts,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, 'count'),
            'responseSummary': build_response_summary_by_dataset(self, datasets, data, dict_counts, qparams),
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_error_response(self, errorCode, errorMessage):
    try:

        beacon_response = {
            'meta': build_meta(self,         {
                "apiVersion": RequestMeta().apiVersion,
                "requestedSchemas": RequestMeta().requestedSchemas,
                "pagination": RequestQuery().pagination.dict(),
                "requestedGranularity": RequestQuery().requestedGranularity,
            }, None, Granularity.RECORD),
            'error': {
                'errorCode': str(errorCode),
                'errorMessage': str(errorMessage)
            }
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_collection_response(self, data, num_total_results, qparams: RequestParams, entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'info': build_extended_info(),
            'beaconHandovers': list_of_handovers,
            'response': {
                'collections': data
            }
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_info_response(self):
    try:
        beacon_response = {
            'meta': build_info_meta(self, None),
            'response': {
                'id': conf.beacon_id,
                'name': conf.beacon_name,
                'apiVersion': conf.api_version,
                'environment': conf.environment,
                'organization': {
                    'id': conf.org_id,
                    'name': conf.org_name,
                    'description': conf.org_description,
                    'address': conf.org_adress,
                    'welcomeUrl': conf.org_welcome_url,
                    'contactUrl': conf.org_contact_url,
                    'logoUrl': conf.org_logo_url,
                },
                'description': conf.description,
                'version': conf.version,
                'welcomeUrl': conf.welcome_url,
                'alternativeUrl': conf.alternative_url,
                'createDateTime': conf.create_datetime,
                'updateDateTime': conf.update_datetime
            }
        }
        return beacon_response
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_configuration(self):
    try:
        meta = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/sections/beaconInformationalResponseMeta.json',
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        with open('beacon/response/templates/configuration.json', 'r') as template:
            response = json.load(template)

        response['securityAttributes']['defaultGranularity']=conf.default_beacon_granularity
        response['securityAttributes']['securityLevels']=conf.security_levels
        response['maturityAttributes']['productionStatus']=conf.environment.upper()

        if analysis.endpoint_name != '':
            response['entryTypes'][analysis.id]==response['entryTypes']['analysis']
            if analysis.id != 'analysis':
                del response['entryTypes']['analysis']
            response['entryTypes'][analysis.id]["id"]=analysis.id
            response['entryTypes'][analysis.id]["name"]=analysis.name
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['id']=analysis.ontology_id
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['name']=analysis.ontology_name
            response['entryTypes'][analysis.id]['partOfSpecification']=analysis.specification
            response['entryTypes'][analysis.id]['description']=analysis.description
            response['entryTypes'][analysis.id]['defaultSchema']['id']=analysis.defaultSchema_id
            response['entryTypes'][analysis.id]['defaultSchema']['name']=analysis.defaultSchema_name
            response['entryTypes'][analysis.id]['defaultSchema']['referenceToSchemaDefinition']=analysis.defaultSchema_reference_to_schema_definition
            response['entryTypes'][analysis.id]['defaultSchema']['schemaVersion']=analysis.defaultSchema_schema_version
            response['entryTypes'][analysis.id]['additionallySupportedSchemas']=analysis.aditionally_supported_schemas
            response['entryTypes'][analysis.id]['nonFilteredQueriesAllowed']=analysis.allow_queries_without_filters
        else:
            del response['entryTypes']['analysis']
        if biosample.endpoint_name != '':
            response['entryTypes'][biosample.id]==response['entryTypes']['biosample']
            if biosample.id != 'biosample':
                del response['entryTypes']['biosample']
            response['entryTypes'][biosample.id]["id"]=biosample.id
            response['entryTypes'][biosample.id]["name"]=biosample.name
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['id']=biosample.ontology_id
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['name']=biosample.ontology_name
            response['entryTypes'][biosample.id]['partOfSpecification']=biosample.specification
            response['entryTypes'][biosample.id]['description']=biosample.description
            response['entryTypes'][biosample.id]['defaultSchema']['id']=biosample.defaultSchema_id
            response['entryTypes'][biosample.id]['defaultSchema']['name']=biosample.defaultSchema_name
            response['entryTypes'][biosample.id]['defaultSchema']['referenceToSchemaDefinition']=biosample.defaultSchema_reference_to_schema_definition
            response['entryTypes'][biosample.id]['defaultSchema']['schemaVersion']=biosample.defaultSchema_schema_version
            response['entryTypes'][biosample.id]['additionallySupportedSchemas']=biosample.aditionally_supported_schemas
            response['entryTypes'][biosample.id]['nonFilteredQueriesAllowed']=biosample.allow_queries_without_filters
        else:
            del response['entryTypes']['biosample']
        if cohort.endpoint_name!='':
            response['entryTypes'][cohort.id]==response['entryTypes']['cohort']
            if cohort.id != 'cohort':
                del response['entryTypes']['cohort']
            response['entryTypes'][cohort.id]["id"]=cohort.id
            response['entryTypes'][cohort.id]["name"]=cohort.name
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['id']=cohort.ontology_id
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['name']=cohort.ontology_name
            response['entryTypes'][cohort.id]['partOfSpecification']=cohort.specification
            response['entryTypes'][cohort.id]['description']=cohort.description
            response['entryTypes'][cohort.id]['defaultSchema']['id']=cohort.defaultSchema_id
            response['entryTypes'][cohort.id]['defaultSchema']['name']=cohort.defaultSchema_name
            response['entryTypes'][cohort.id]['defaultSchema']['referenceToSchemaDefinition']=cohort.defaultSchema_reference_to_schema_definition
            response['entryTypes'][cohort.id]['defaultSchema']['schemaVersion']=cohort.defaultSchema_schema_version
            response['entryTypes'][cohort.id]['additionallySupportedSchemas']=cohort.aditionally_supported_schemas
            response['entryTypes'][cohort.id]['nonFilteredQueriesAllowed']=cohort.allow_queries_without_filters
        else:
            del response['entryTypes']['cohort']
        if dataset.endpoint_name!='':
            response['entryTypes'][dataset.id]==response['entryTypes']['dataset']
            if dataset.id != 'dataset':
                del response['entryTypes']['dataset']
            response['entryTypes'][dataset.id]["id"]=dataset.id
            response['entryTypes'][dataset.id]["name"]=dataset.name
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['id']=dataset.ontology_id
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['name']=dataset.ontology_name
            response['entryTypes'][dataset.id]['partOfSpecification']=dataset.specification
            response['entryTypes'][dataset.id]['description']=dataset.description
            response['entryTypes'][dataset.id]['defaultSchema']['id']=dataset.defaultSchema_id
            response['entryTypes'][dataset.id]['defaultSchema']['name']=dataset.defaultSchema_name
            response['entryTypes'][dataset.id]['defaultSchema']['referenceToSchemaDefinition']=dataset.defaultSchema_reference_to_schema_definition
            response['entryTypes'][dataset.id]['defaultSchema']['schemaVersion']=dataset.defaultSchema_schema_version
            response['entryTypes'][dataset.id]['additionallySupportedSchemas']=dataset.aditionally_supported_schemas
            response['entryTypes'][dataset.id]['nonFilteredQueriesAllowed']=dataset.allow_queries_without_filters
        else:
            del response['entryTypes']['dataset']
        if genomicVariant.endpoint_name!='':
            response['entryTypes'][genomicVariant.id]==response['entryTypes']['genomicVariant']
            if genomicVariant.id != 'genomicVariant':
                del response['entryTypes']['genomicVariant']
            response['entryTypes'][genomicVariant.id]["id"]=genomicVariant.id
            response['entryTypes'][genomicVariant.id]["name"]=genomicVariant.name
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['id']=genomicVariant.ontology_id
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['name']=genomicVariant.ontology_name
            response['entryTypes'][genomicVariant.id]['partOfSpecification']=genomicVariant.specification
            response['entryTypes'][genomicVariant.id]['description']=genomicVariant.description
            response['entryTypes'][genomicVariant.id]['defaultSchema']['id']=genomicVariant.defaultSchema_id
            response['entryTypes'][genomicVariant.id]['defaultSchema']['name']=genomicVariant.defaultSchema_name
            response['entryTypes'][genomicVariant.id]['defaultSchema']['referenceToSchemaDefinition']=genomicVariant.defaultSchema_reference_to_schema_definition
            response['entryTypes'][genomicVariant.id]['defaultSchema']['schemaVersion']=genomicVariant.defaultSchema_schema_version
            response['entryTypes'][genomicVariant.id]['additionallySupportedSchemas']=genomicVariant.aditionally_supported_schemas
            response['entryTypes'][genomicVariant.id]['nonFilteredQueriesAllowed']=genomicVariant.allow_queries_without_filters
        else:
            del response['entryTypes']['genomicVariant']
        if individual.endpoint_name!='':
            response['entryTypes'][individual.id]==response['entryTypes']['individual']
            if individual.id != 'individual':
                del response['entryTypes']['individual']
            response['entryTypes'][individual.id]["id"]=individual.id
            response['entryTypes'][individual.id]["name"]=individual.name
            response['entryTypes'][individual.id]['ontologyTermForThisType']['id']=individual.ontology_id
            response['entryTypes'][individual.id]['ontologyTermForThisType']['name']=individual.ontology_name
            response['entryTypes'][individual.id]['partOfSpecification']=individual.specification
            response['entryTypes'][individual.id]['description']=individual.description
            response['entryTypes'][individual.id]['defaultSchema']['id']=individual.defaultSchema_id
            response['entryTypes'][individual.id]['defaultSchema']['name']=individual.defaultSchema_name
            response['entryTypes'][individual.id]['defaultSchema']['referenceToSchemaDefinition']=individual.defaultSchema_reference_to_schema_definition
            response['entryTypes'][individual.id]['defaultSchema']['schemaVersion']=individual.defaultSchema_schema_version
            response['entryTypes'][individual.id]['additionallySupportedSchemas']=individual.aditionally_supported_schemas
            response['entryTypes'][individual.id]['nonFilteredQueriesAllowed']=individual.allow_queries_without_filters
        else:
            del response['entryTypes']['individual']
        if run.endpoint_name!='':
            response['entryTypes'][run.id]==response['entryTypes']['run']
            if run.id != 'run':
                del response['entryTypes']['run']
            response['entryTypes'][run.id]["id"]=run.id
            response['entryTypes'][run.id]["name"]=run.name
            response['entryTypes'][run.id]['ontologyTermForThisType']['id']=run.ontology_id
            response['entryTypes'][run.id]['ontologyTermForThisType']['name']=run.ontology_name
            response['entryTypes'][run.id]['partOfSpecification']=run.specification
            response['entryTypes'][run.id]['description']=run.description
            response['entryTypes'][run.id]['defaultSchema']['id']=run.defaultSchema_id
            response['entryTypes'][run.id]['defaultSchema']['name']=run.defaultSchema_name
            response['entryTypes'][run.id]['defaultSchema']['referenceToSchemaDefinition']=run.defaultSchema_reference_to_schema_definition
            response['entryTypes'][run.id]['defaultSchema']['schemaVersion']=run.defaultSchema_schema_version
            response['entryTypes'][run.id]['additionallySupportedSchemas']=run.aditionally_supported_schemas
            response['entryTypes'][run.id]['nonFilteredQueriesAllowed']=run.allow_queries_without_filters
        else:
            del response['entryTypes']['run']
        if response['entryTypes'] == {}:
            ErrorClass.error_code=500
            ErrorClass.error_message='Please, provide an entry type in conf to be able to have a beacon instance with at least one endpoint to query.'
            raise

        configuration_json = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/beaconConfigurationResponse.json',
            'meta': meta,
            'response': response
        }

        return configuration_json
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_map(self):
    try:
        meta = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/sections/beaconInformationalResponseMeta.json',
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        response = generate_endpoints(self, 'map', 'endpointSets')

        beacon_map_json = {
            'meta': meta,
            'response': response
        }

        return beacon_map_json
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_entry_types(self):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        with open('beacon/response/templates/entry_types.json', 'r') as template:
            response = json.load(template)


        if analysis.endpoint_name != '':
            response['entryTypes'][analysis.id]==response['entryTypes']['analysis']
            if analysis.id != 'analysis':
                del response['entryTypes']['analysis']
            response['entryTypes'][analysis.id]["id"]=analysis.id
            response['entryTypes'][analysis.id]["name"]=analysis.name
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['id']=analysis.ontology_id
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['name']=analysis.ontology_name
            response['entryTypes'][analysis.id]['partOfSpecification']=analysis.specification
            response['entryTypes'][analysis.id]['description']=analysis.description
            response['entryTypes'][analysis.id]['defaultSchema']['id']=analysis.defaultSchema_id
            response['entryTypes'][analysis.id]['defaultSchema']['name']=analysis.defaultSchema_name
            response['entryTypes'][analysis.id]['defaultSchema']['referenceToSchemaDefinition']=analysis.defaultSchema_reference_to_schema_definition
            response['entryTypes'][analysis.id]['defaultSchema']['schemaVersion']=analysis.defaultSchema_schema_version
            response['entryTypes'][analysis.id]['additionallySupportedSchemas']=analysis.aditionally_supported_schemas
            response['entryTypes'][analysis.id]['nonFilteredQueriesAllowed']=analysis.allow_queries_without_filters
        else:
            del response['entryTypes']['analysis']
        if biosample.endpoint_name != '':
            response['entryTypes'][biosample.id]==response['entryTypes']['biosample']
            if biosample.id != 'biosample':
                del response['entryTypes']['biosample']
            response['entryTypes'][biosample.id]["id"]=biosample.id
            response['entryTypes'][biosample.id]["name"]=biosample.name
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['id']=biosample.ontology_id
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['name']=biosample.ontology_name
            response['entryTypes'][biosample.id]['partOfSpecification']=biosample.specification
            response['entryTypes'][biosample.id]['description']=biosample.description
            response['entryTypes'][biosample.id]['defaultSchema']['id']=biosample.defaultSchema_id
            response['entryTypes'][biosample.id]['defaultSchema']['name']=biosample.defaultSchema_name
            response['entryTypes'][biosample.id]['defaultSchema']['referenceToSchemaDefinition']=biosample.defaultSchema_reference_to_schema_definition
            response['entryTypes'][biosample.id]['defaultSchema']['schemaVersion']=biosample.defaultSchema_schema_version
            response['entryTypes'][biosample.id]['additionallySupportedSchemas']=biosample.aditionally_supported_schemas
            response['entryTypes'][biosample.id]['nonFilteredQueriesAllowed']=biosample.allow_queries_without_filters
        else:
            del response['entryTypes']['biosample']
        if cohort.endpoint_name!='':
            response['entryTypes'][cohort.id]==response['entryTypes']['cohort']
            if cohort.id != 'cohort':
                del response['entryTypes']['cohort']
            response['entryTypes'][cohort.id]["id"]=cohort.id
            response['entryTypes'][cohort.id]["name"]=cohort.name
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['id']=cohort.ontology_id
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['name']=cohort.ontology_name
            response['entryTypes'][cohort.id]['partOfSpecification']=cohort.specification
            response['entryTypes'][cohort.id]['description']=cohort.description
            response['entryTypes'][cohort.id]['defaultSchema']['id']=cohort.defaultSchema_id
            response['entryTypes'][cohort.id]['defaultSchema']['name']=cohort.defaultSchema_name
            response['entryTypes'][cohort.id]['defaultSchema']['referenceToSchemaDefinition']=cohort.defaultSchema_reference_to_schema_definition
            response['entryTypes'][cohort.id]['defaultSchema']['schemaVersion']=cohort.defaultSchema_schema_version
            response['entryTypes'][cohort.id]['additionallySupportedSchemas']=cohort.aditionally_supported_schemas
            response['entryTypes'][cohort.id]['nonFilteredQueriesAllowed']=cohort.allow_queries_without_filters
        else:
            del response['entryTypes']['cohort']
        if dataset.endpoint_name!='':
            response['entryTypes'][dataset.id]==response['entryTypes']['dataset']
            if dataset.id != 'dataset':
                del response['entryTypes']['dataset']
            response['entryTypes'][dataset.id]["id"]=dataset.id
            response['entryTypes'][dataset.id]["name"]=dataset.name
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['id']=dataset.ontology_id
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['name']=dataset.ontology_name
            response['entryTypes'][dataset.id]['partOfSpecification']=dataset.specification
            response['entryTypes'][dataset.id]['description']=dataset.description
            response['entryTypes'][dataset.id]['defaultSchema']['id']=dataset.defaultSchema_id
            response['entryTypes'][dataset.id]['defaultSchema']['name']=dataset.defaultSchema_name
            response['entryTypes'][dataset.id]['defaultSchema']['referenceToSchemaDefinition']=dataset.defaultSchema_reference_to_schema_definition
            response['entryTypes'][dataset.id]['defaultSchema']['schemaVersion']=dataset.defaultSchema_schema_version
            response['entryTypes'][dataset.id]['additionallySupportedSchemas']=dataset.aditionally_supported_schemas
            response['entryTypes'][dataset.id]['nonFilteredQueriesAllowed']=dataset.allow_queries_without_filters
        else:
            del response['entryTypes']['dataset']
        if genomicVariant.endpoint_name!='':
            response['entryTypes'][genomicVariant.id]==response['entryTypes']['genomicVariant']
            if genomicVariant.id != 'genomicVariant':
                del response['entryTypes']['genomicVariant']
            response['entryTypes'][genomicVariant.id]["id"]=genomicVariant.id
            response['entryTypes'][genomicVariant.id]["name"]=genomicVariant.name
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['id']=genomicVariant.ontology_id
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['name']=genomicVariant.ontology_name
            response['entryTypes'][genomicVariant.id]['partOfSpecification']=genomicVariant.specification
            response['entryTypes'][genomicVariant.id]['description']=genomicVariant.description
            response['entryTypes'][genomicVariant.id]['defaultSchema']['id']=genomicVariant.defaultSchema_id
            response['entryTypes'][genomicVariant.id]['defaultSchema']['name']=genomicVariant.defaultSchema_name
            response['entryTypes'][genomicVariant.id]['defaultSchema']['referenceToSchemaDefinition']=genomicVariant.defaultSchema_reference_to_schema_definition
            response['entryTypes'][genomicVariant.id]['defaultSchema']['schemaVersion']=genomicVariant.defaultSchema_schema_version
            response['entryTypes'][genomicVariant.id]['additionallySupportedSchemas']=genomicVariant.aditionally_supported_schemas
            response['entryTypes'][genomicVariant.id]['nonFilteredQueriesAllowed']=genomicVariant.allow_queries_without_filters
        else:
            del response['entryTypes']['genomicVariant']
        if individual.endpoint_name!='':
            response['entryTypes'][individual.id]==response['entryTypes']['individual']
            if individual.id != 'individual':
                del response['entryTypes']['individual']
            response['entryTypes'][individual.id]["id"]=individual.id
            response['entryTypes'][individual.id]["name"]=individual.name
            response['entryTypes'][individual.id]['ontologyTermForThisType']['id']=individual.ontology_id
            response['entryTypes'][individual.id]['ontologyTermForThisType']['name']=individual.ontology_name
            response['entryTypes'][individual.id]['partOfSpecification']=individual.specification
            response['entryTypes'][individual.id]['description']=individual.description
            response['entryTypes'][individual.id]['defaultSchema']['id']=individual.defaultSchema_id
            response['entryTypes'][individual.id]['defaultSchema']['name']=individual.defaultSchema_name
            response['entryTypes'][individual.id]['defaultSchema']['referenceToSchemaDefinition']=individual.defaultSchema_reference_to_schema_definition
            response['entryTypes'][individual.id]['defaultSchema']['schemaVersion']=individual.defaultSchema_schema_version
            response['entryTypes'][individual.id]['additionallySupportedSchemas']=individual.aditionally_supported_schemas
            response['entryTypes'][individual.id]['nonFilteredQueriesAllowed']=individual.allow_queries_without_filters
        else:
            del response['entryTypes']['individual']
        if run.endpoint_name!='':
            response['entryTypes'][run.id]==response['entryTypes']['run']
            if run.id != 'run':
                del response['entryTypes']['run']
            response['entryTypes'][run.id]["id"]=run.id
            response['entryTypes'][run.id]["name"]=run.name
            response['entryTypes'][run.id]['ontologyTermForThisType']['id']=run.ontology_id
            response['entryTypes'][run.id]['ontologyTermForThisType']['name']=run.ontology_name
            response['entryTypes'][run.id]['partOfSpecification']=run.specification
            response['entryTypes'][run.id]['description']=run.description
            response['entryTypes'][run.id]['defaultSchema']['id']=run.defaultSchema_id
            response['entryTypes'][run.id]['defaultSchema']['name']=run.defaultSchema_name
            response['entryTypes'][run.id]['defaultSchema']['referenceToSchemaDefinition']=run.defaultSchema_reference_to_schema_definition
            response['entryTypes'][run.id]['defaultSchema']['schemaVersion']=run.defaultSchema_schema_version
            response['entryTypes'][run.id]['additionallySupportedSchemas']=run.aditionally_supported_schemas
            response['entryTypes'][run.id]['nonFilteredQueriesAllowed']=run.allow_queries_without_filters
        else:
            del response['entryTypes']['run']
        if response['entryTypes'] == {}:
            ErrorClass.error_code=500
            ErrorClass.error_message='Please, provide an entry type in conf to be able to have a beacon instance with at least one endpoint to query.'
            raise

        entry_types_json = {
            'meta': meta,
            'response': response
        }

        return entry_types_json
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_beacon_service_info_response(self):
    try:
        beacon_response = {
            'id': conf.beacon_id,
            'name': conf.beacon_name,
            'type': {
                'group': conf.ga4gh_service_type_group,
                'artifact': conf.ga4gh_service_type_artifact,
                'version': conf.ga4gh_service_type_version
            },
            'description': conf.description,
            'organization': {
                'name': conf.org_name,
                'url': conf.org_welcome_url
            },
            'contactUrl': conf.org_contact_url,
            'documentationUrl': conf.documentation_url,
            'createdAt': conf.create_datetime,
            'updatedAt': conf.update_datetime,
            'environment': conf.environment,
            'version': conf.version,
        }
        return beacon_response
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_beacon_well_known_oauth_response(self):
    try:
        beacon_response = {
            'resource': conf.complete_url,
            'authorization_servers': conf.authorization_servers,
            'client_id': conf.client_id,
        }
        return beacon_response
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_filtering_terms_response(self, data,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'extendedInfo': build_extended_info(),
            'response': {
                'filteringTerms': data,
                'resources': resources
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise
