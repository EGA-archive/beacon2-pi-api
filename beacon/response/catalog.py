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
import sys

@log_with_args(level)
def generate_endpoints(self, response_type, key_response):
    with open('beacon/response/templates/{}.json'.format(response_type), 'r') as template:
        response = json.load(template)
    new_response={}
    new_response[key_response]={}
    # TODO: delete parts where the entry type without name shouldn't exist
    if analysis.endpoint_name!='' and analysis.enable_endpoint==True:
        new_response[key_response][analysis.id]=response[key_response]['analysis']
        new_response[key_response][analysis.id]["entryType"]=analysis.id
        new_response[key_response][analysis.id]["openAPIEndpointsDefinition"]=analysis.open_api_endpoints_definition
        new_response[key_response][analysis.id]["rootUrl"]=conf.complete_url+'/'+analysis.endpoint_name
        if analysis.singleEntryUrl == True:
            new_response[key_response][analysis.id]["singleEntryUrl"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}'
        else:
            del new_response[key_response][analysis.id]["singleEntryUrl"]
        if analysis.biosample_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][biosample.id]=response[key_response]['analysis']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][analysis.id]["endpoints"]["biosample"]
            new_response[key_response][analysis.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][analysis.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name
        if analysis.cohort_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][cohort.id]=response[key_response]['analysis']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][analysis.id]["endpoints"]["cohort"]
            new_response[key_response][analysis.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][analysis.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name
        if analysis.dataset_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][dataset.id]=response[key_response]['analysis']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][analysis.id]["endpoints"]["dataset"]
            new_response[key_response][analysis.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][analysis.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name
        if analysis.genomicVariant_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][genomicVariant.id]=response[key_response]['analysis']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][analysis.id]["endpoints"]["genomicVariant"]
            new_response[key_response][analysis.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][analysis.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if analysis.individual_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][individual.id]=response[key_response]['analysis']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][analysis.id]["endpoints"]["individual"]
            new_response[key_response][analysis.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][analysis.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name
        if analysis.run_lookup == True:
            new_response[key_response][analysis.id]["endpoints"][run.id]=response[key_response]['analysis']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][analysis.id]["endpoints"]["run"]
            new_response[key_response][analysis.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][analysis.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name
    if biosample.endpoint_name!='' and biosample.enable_endpoint==True:
        new_response[key_response][biosample.id]=response[key_response]['biosample']
        new_response[key_response][biosample.id]["entryType"]=biosample.id
        new_response[key_response][biosample.id]["openAPIEndpointsDefinition"]=biosample.open_api_endpoints_definition
        new_response[key_response][biosample.id]["rootUrl"]=conf.complete_url+'/'+biosample.endpoint_name
        if biosample.singleEntryUrl == True:
            new_response[key_response][biosample.id]["singleEntryUrl"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}'
        else:
            del new_response[key_response][biosample.id]["singleEntryUrl"]
        if biosample.analysis_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][analysis.id]=response[key_response]['biosample']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][biosample.id]["endpoints"]["analysis"]
            new_response[key_response][biosample.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][biosample.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name
        if biosample.cohort_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][cohort.id]=response[key_response]['biosample']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][biosample.id]["endpoints"]["cohort"]
            new_response[key_response][biosample.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][biosample.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name
        if biosample.dataset_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][dataset.id]=response[key_response]['biosample']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][biosample.id]["endpoints"]["dataset"]
            new_response[key_response][biosample.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][biosample.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name
        if biosample.genomicVariant_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][genomicVariant.id]=response[key_response]['biosample']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][biosample.id]["endpoints"]["genomicVariant"]
            new_response[key_response][biosample.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][biosample.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if biosample.individual_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][individual.id]=response[key_response]['biosample']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][biosample.id]["endpoints"]["individual"]
            new_response[key_response][biosample.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][biosample.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name
        if biosample.run_lookup == True:
            new_response[key_response][biosample.id]["endpoints"][run.id]=response[key_response]['biosample']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][biosample.id]["endpoints"]["run"]
            new_response[key_response][biosample.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][biosample.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name
    if cohort.endpoint_name!='' and cohort.enable_endpoint==True:
        new_response[key_response][cohort.id]=response[key_response]['cohort']
        new_response[key_response][cohort.id]["entryType"]=cohort.id
        new_response[key_response][cohort.id]["openAPIEndpointsDefinition"]=cohort.open_api_endpoints_definition
        new_response[key_response][cohort.id]["rootUrl"]=conf.complete_url+'/'+cohort.endpoint_name
        if cohort.singleEntryUrl == True:
            new_response[key_response][cohort.id]["singleEntryUrl"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}'
        else:
            del new_response[key_response][cohort.id]["singleEntryUrl"]
        if cohort.analysis_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][analysis.id]=response[key_response]['cohort']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][cohort.id]["endpoints"]["analysis"]
            new_response[key_response][cohort.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][cohort.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name
        if cohort.biosample_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][biosample.id]=response[key_response]['cohort']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][cohort.id]["endpoints"]["biosample"]
            new_response[key_response][cohort.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][cohort.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name
        if cohort.dataset_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][dataset.id]=response[key_response]['cohort']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][cohort.id]["endpoints"]["dataset"]
            new_response[key_response][cohort.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][cohort.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name
        if cohort.genomicVariant_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][genomicVariant.id]=response[key_response]['cohort']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][cohort.id]["endpoints"]["genomicVariant"]
            new_response[key_response][cohort.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][cohort.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if cohort.individual_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][individual.id]=response[key_response]['cohort']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][cohort.id]["endpoints"]["individual"]
            new_response[key_response][cohort.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][cohort.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name
        if cohort.run_lookup == True:
            new_response[key_response][cohort.id]["endpoints"][run.id]=response[key_response]['cohort']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][cohort.id]["endpoints"]["run"]
            new_response[key_response][cohort.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][cohort.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name
    if dataset.endpoint_name!='' and dataset.enable_endpoint==True:
        new_response[key_response][dataset.id]=response[key_response]['dataset']
        new_response[key_response][dataset.id]["entryType"]=dataset.id
        new_response[key_response][dataset.id]["openAPIEndpointsDefinition"]=dataset.open_api_endpoints_definition
        new_response[key_response][dataset.id]["rootUrl"]=conf.complete_url+'/'+dataset.endpoint_name
        if dataset.singleEntryUrl == True:
            new_response[key_response][dataset.id]["singleEntryUrl"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}'
        else:
            del new_response[key_response][dataset.id]["singleEntryUrl"]
        if dataset.analysis_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][analysis.id]=response[key_response]['dataset']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][dataset.id]["endpoints"]["analysis"]
            new_response[key_response][dataset.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][dataset.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name
        if dataset.biosample_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][biosample.id]=response[key_response]['dataset']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][dataset.id]["endpoints"]["biosample"]
            new_response[key_response][dataset.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][dataset.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name
        if dataset.cohort_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][cohort.id]=response[key_response]['dataset']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][dataset.id]["endpoints"]["dataset"]
            new_response[key_response][dataset.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][dataset.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name
        if dataset.genomicVariant_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][genomicVariant.id]=response[key_response]['dataset']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][dataset.id]["endpoints"]["genomicVariant"]
            new_response[key_response][dataset.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][dataset.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if dataset.individual_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][individual.id]=response[key_response]['dataset']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][dataset.id]["endpoints"]["individual"]
            new_response[key_response][dataset.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][dataset.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name
        if dataset.run_lookup == True:
            new_response[key_response][dataset.id]["endpoints"][run.id]=response[key_response]['dataset']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][dataset.id]["endpoints"]["run"]
            new_response[key_response][dataset.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][dataset.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name
    if genomicVariant.endpoint_name!='' and genomicVariant.enable_endpoint==True:
        new_response[key_response][genomicVariant.id]=response[key_response]['genomicVariant']
        new_response[key_response][genomicVariant.id]["entryType"]=genomicVariant.id
        new_response[key_response][genomicVariant.id]["openAPIEndpointsDefinition"]=genomicVariant.open_api_endpoints_definition
        new_response[key_response][genomicVariant.id]["rootUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name
        if genomicVariant.singleEntryUrl == True:
            new_response[key_response][genomicVariant.id]["singleEntryUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}'
        else:
            del new_response[key_response][genomicVariant.id]["singleEntryUrl"]
        if genomicVariant.analysis_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][analysis.id]=response[key_response]['genomicVariant']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][genomicVariant.id]["endpoints"]["analysis"]
            new_response[key_response][genomicVariant.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][genomicVariant.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+analysis.endpoint_name
        if genomicVariant.biosample_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][biosample.id]=response[key_response]['genomicVariant']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][genomicVariant.id]["endpoints"]["biosample"]
            new_response[key_response][genomicVariant.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][genomicVariant.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+biosample.endpoint_name
        if genomicVariant.cohort_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][cohort.id]=response[key_response]['genomicVariant']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][genomicVariant.id]["endpoints"]["genomicVariant"]
            new_response[key_response][genomicVariant.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][genomicVariant.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+cohort.endpoint_name
        if genomicVariant.dataset_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][dataset.id]=response[key_response]['genomicVariant']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][genomicVariant.id]["endpoints"]["dataset"]
            new_response[key_response][genomicVariant.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][genomicVariant.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+dataset.endpoint_name
        if genomicVariant.individual_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][individual.id]=response[key_response]['genomicVariant']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][genomicVariant.id]["endpoints"]["individual"]
            new_response[key_response][genomicVariant.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][genomicVariant.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+individual.endpoint_name
        if genomicVariant.run_lookup == True:
            new_response[key_response][genomicVariant.id]["endpoints"][run.id]=response[key_response]['genomicVariant']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][genomicVariant.id]["endpoints"]["run"]
            new_response[key_response][genomicVariant.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][genomicVariant.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+run.endpoint_name
    if individual.endpoint_name!='' and individual.enable_endpoint==True:
        new_response[key_response][individual.id]=response[key_response]['individual']
        new_response[key_response][individual.id]["entryType"]=individual.id
        new_response[key_response][individual.id]["openAPIEndpointsDefinition"]=individual.open_api_endpoints_definition
        new_response[key_response][individual.id]["rootUrl"]=conf.complete_url+'/'+individual.endpoint_name
        if individual.singleEntryUrl == True:
            new_response[key_response][individual.id]["singleEntryUrl"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}'
        else:
            del new_response[key_response][individual.id]["singleEntryUrl"]
        if individual.analysis_lookup == True:
            new_response[key_response][individual.id]["endpoints"][analysis.id]=response[key_response]['individual']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][individual.id]["endpoints"]["analysis"]
            new_response[key_response][individual.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][individual.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name
        if individual.biosample_lookup == True:
            new_response[key_response][individual.id]["endpoints"][biosample.id]=response[key_response]['individual']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][individual.id]["endpoints"]["biosample"]
            new_response[key_response][individual.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][individual.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name
        if individual.cohort_lookup == True:
            new_response[key_response][individual.id]["endpoints"][cohort.id]=response[key_response]['individual']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][individual.id]["endpoints"]["individual"]
            new_response[key_response][individual.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][individual.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name
        if individual.dataset_lookup == True:
            new_response[key_response][individual.id]["endpoints"][dataset.id]=response[key_response]['individual']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][individual.id]["endpoints"]["dataset"]
            new_response[key_response][individual.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][individual.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name
        if individual.genomicVariant_lookup == True:
            new_response[key_response][individual.id]["endpoints"][genomicVariant.id]=response[key_response]['individual']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][individual.id]["endpoints"]["genomicVariant"]
            new_response[key_response][individual.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][individual.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if individual.run_lookup == True:
            new_response[key_response][individual.id]["endpoints"][run.id]=response[key_response]['individual']["endpoints"]["run"]
            if run.id != 'run':
                del new_response[key_response][individual.id]["endpoints"]["run"]
            new_response[key_response][individual.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response[key_response][individual.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name
    if run.endpoint_name!='' and run.enable_endpoint==True:
        new_response[key_response][run.id]=response[key_response]['run']
        new_response[key_response][run.id]["entryType"]=run.id
        new_response[key_response][run.id]["openAPIEndpointsDefinition"]=run.open_api_endpoints_definition
        new_response[key_response][run.id]["rootUrl"]=conf.complete_url+'/'+run.endpoint_name
        if run.singleEntryUrl == True:
            new_response[key_response][run.id]["singleEntryUrl"]=conf.complete_url+'/'+run.endpoint_name+'/{id}'
        else:
            del new_response[key_response][run.id]["singleEntryUrl"]
        if run.analysis_lookup == True:
            new_response[key_response][run.id]["endpoints"][analysis.id]=response[key_response]['run']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response[key_response][run.id]["endpoints"]["analysis"]
            new_response[key_response][run.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response[key_response][run.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name
        if run.biosample_lookup == True:
            new_response[key_response][run.id]["endpoints"][biosample.id]=response[key_response]['run']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response[key_response][run.id]["endpoints"]["biosample"]
            new_response[key_response][run.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response[key_response][run.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name
        if run.cohort_lookup == True:
            new_response[key_response][run.id]["endpoints"][cohort.id]=response[key_response]['run']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response[key_response][run.id]["endpoints"]["run"]
            new_response[key_response][run.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response[key_response][run.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name
        if run.dataset_lookup == True:
            new_response[key_response][run.id]["endpoints"][dataset.id]=response[key_response]['run']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response[key_response][run.id]["endpoints"]["dataset"]
            new_response[key_response][run.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response[key_response][run.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name
        if run.genomicVariant_lookup == True:
            new_response[key_response][run.id]["endpoints"][genomicVariant.id]=response[key_response]['run']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response[key_response][run.id]["endpoints"]["genomicVariant"]
            new_response[key_response][run.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response[key_response][run.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if run.individual_lookup == True:
            new_response[key_response][run.id]["endpoints"][individual.id]=response[key_response]['run']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response[key_response][run.id]["endpoints"]["individual"]
            new_response[key_response][run.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response[key_response][run.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name
    return new_response

@log_with_args(level)
def build_response(self, data, num_total_results):
    """"Fills the `response` part with the correct format in `results`"""
    limit = RequestAttributes.qparams.query.pagination.limit
    include = RequestAttributes.qparams.query.includeResultsetResponses
    if limit != 0 and limit < num_total_results:
        response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': limit,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }
    else:
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
        if num_total_results is None:
            return {
                'exists': exists
            }
        else:
            return {
                'exists': exists,
                'numTotalResults': num_total_results
            }
    except Exception as e:
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_response_summary_by_dataset(self, datasets, data, dict_counts):
    try:
        count=0
        non_counted=0
        granularity = RequestAttributes.qparams.query.requestedGranularity
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
            RequestAttributes.returned_granularity = 'boolean'
            return {
                'exists': True
            }
        elif count > 0:
            return {
                'exists': count > 0,
                'numTotalResults': count
            }
        else:
            RequestAttributes.returned_granularity = 'boolean'
            return {
                'exists': False
            }
    except Exception as e:
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_meta(self, entity_schema: Optional[DefaultSchemas]):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedGranularity': RequestAttributes.returned_granularity,
            'receivedRequestSummary': RequestAttributes.qparams.summary(),
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception as e:
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
    except Exception:
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
def build_response_by_dataset(self, datasets, data, dict_counts):
    try:
        granularity = RequestAttributes.qparams.query.requestedGranularity
        list_of_responses=[]
        for dataset in datasets:
            if dataset.granularity == 'record' and RequestAttributes.allowed_granularity=='record' and granularity =='record':
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:
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
                    if handover["dataset"]==dataset.dataset:
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
                    if handover["dataset"]==dataset.dataset:
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
    except Exception:
        raise

@log_with_args(level)
def build_beacon_record_response_by_dataset(self, datasets, data,
                                    dict_counts,
                                    entity_schema: DefaultSchemas):
    try:
        responseSummary = build_response_summary_by_dataset(self, datasets, data, dict_counts)
        resultSets = build_response_by_dataset(self, datasets, data, dict_counts) # setting variables before meta, in case meta changes
        beacon_response = {
            'meta': build_meta(self, entity_schema),
            'responseSummary': responseSummary,
            'response': {
                'resultSets': resultSets,
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_boolean_response(self,
                                    num_total_results,
                                    entity_schema: DefaultSchemas):
    try:
        responseSummary = build_response_summary(self, num_total_results > 0, None)
        beacon_response = {
            'meta': build_meta(self, entity_schema),
            'responseSummary': responseSummary,
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_count_response(self, datasets, data,
                                    dict_counts,
                                    num_total_results,
                                    entity_schema: DefaultSchemas):
    try:
        responseSummary = build_response_summary_by_dataset(self, datasets, data, dict_counts)
        beacon_response = {
            'meta': build_meta(self, entity_schema),
            'responseSummary': responseSummary,
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_error_response(self, errorCode, errorMessage):
    try:

        beacon_response = {
            'meta': build_meta(self, None),
            'error': {
                'errorCode': str(errorCode),
                'errorMessage': str(errorMessage)
            }
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_collection_response(self, data, num_total_results: RequestParams, entity_schema: DefaultSchemas):
    try:
        responseSummary = build_response_summary(self, num_total_results > 0, num_total_results)
        beacon_response = {
            'meta': build_meta(self, entity_schema),
            'responseSummary': responseSummary,
            # TODO: 'info': build_extended_info(),
            'beaconHandovers': list_of_handovers,
            'response': {
                'collections': data
            }
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_info_response(self):
    # TODO: reproduir el mateix procediment que per la resta amb templates.
    try:
        with open('beacon/response/templates/{}.json'.format("info"), 'r') as template:
            response = json.load(template)
        beacon_response={}
        beacon_response['meta']=build_info_meta(self, None)
        response['id']=conf.beacon_id
        response['name']=conf.beacon_name
        response['apiVersion']=conf.api_version
        response['environment']=conf.environment
        response['organization']['id']=conf.org_id
        response['organization']['name']=conf.org_name
        response['organization']['description']=conf.org_description
        response['organization']['address']=conf.org_adress
        response['organization']['welcomeUrl']=conf.org_welcome_url
        response['organization']['contactUrl']=conf.org_contact_url
        response['organization']['logoUrl']=conf.org_logo_url
        response['description']=conf.description
        response['version']=conf.version
        response['welcomeUrl']=conf.welcome_url
        response['alternativeUrl']=conf.alternative_url
        response['createDateTime']=conf.create_datetime
        response['updateDateTime']=conf.update_datetime
        beacon_response['response']=response
        return beacon_response
    except Exception as ex:
        #template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #message = template.format(type(ex).__name__, ex.args)
        ErrorClass.error_code=500
        ErrorClass.error_message=str(ex)
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

        if analysis.endpoint_name != '' and analysis.enable_endpoint==True:
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
        if biosample.endpoint_name != '' and biosample.enable_endpoint==True:
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
        if cohort.endpoint_name!='' and cohort.enable_endpoint==True:
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
        if dataset.endpoint_name!='' and dataset.enable_endpoint==True:
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
        if genomicVariant.endpoint_name!='' and genomicVariant.enable_endpoint==True:
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
        if individual.endpoint_name!='' and individual.enable_endpoint==True:
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
        if run.endpoint_name!='' and run.enable_endpoint==True:
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
    except Exception:
        raise

@log_with_args(level)
def build_map(self):
    # TODO: comprovar que s'eliminin els entry types que no tenen nom a configuration
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
    except Exception as e:
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


        if analysis.endpoint_name != '' and analysis.enable_endpoint == True:
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
        if biosample.endpoint_name != '' and biosample.enable_endpoint == True:
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
        if cohort.endpoint_name!='' and cohort.enable_endpoint==True:
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
        if dataset.endpoint_name!='' and dataset.enable_endpoint==True:
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
        if genomicVariant.endpoint_name!='' and genomicVariant.enable_endpoint==True:
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
        if individual.endpoint_name!='' and individual.enable_endpoint==True:
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
        if run.endpoint_name!='' and run.enable_endpoint==True:
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
    except Exception as e:
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_beacon_service_info_response(self):
    try:
        with open('beacon/response/templates/{}.json'.format("service-info"), 'r') as template:
            beacon_response = json.load(template)
        beacon_response['id']=conf.beacon_id
        beacon_response['name']=conf.beacon_name
        beacon_response['type']['group']=conf.ga4gh_service_type_group
        beacon_response['type']['artifact']=conf.ga4gh_service_type_artifact
        beacon_response['type']['version']=conf.ga4gh_service_type_version
        beacon_response['description']=conf.description
        beacon_response['organization']['name']=conf.org_name
        beacon_response['organization']['url']=conf.org_welcome_url
        beacon_response['contactUrl']=conf.org_contact_url
        beacon_response['documentationUrl']=conf.documentation_url
        beacon_response['createdAt']=conf.create_datetime
        beacon_response['updatedAt']=conf.update_datetime
        beacon_response['environment']=conf.environment
        beacon_response['version']=conf.version
        return beacon_response
    except Exception as e:
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_filtering_terms_response(self, data,
                                    num_total_results,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, entity_schema),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'extendedInfo': build_extended_info(),
            'response': {
                'filteringTerms': data,
                'resources': resources
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:
        raise
