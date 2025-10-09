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
from jinja2 import Template

@log_with_args(level)
def build_map(self, response):
    new_response=response
    # TODO: delete parts where the entry type without name shouldn't exist
    if analysis.endpoint_name!='' and analysis.enable_endpoint==True:
        new_response['response']['endpointSets'][analysis.id]=response['response']['endpointSets']['analysis']
        new_response['response']['endpointSets'][analysis.id]["entryType"]=analysis.id
        new_response['response']['endpointSets'][analysis.id]["openAPIEndpointsDefinition"]=analysis.open_api_endpoints_definition
        new_response['response']['endpointSets'][analysis.id]["rootUrl"]=conf.complete_url+'/'+analysis.endpoint_name
        if analysis.singleEntryUrl == True:
            new_response['response']['endpointSets'][analysis.id]["singleEntryUrl"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][analysis.id]["singleEntryUrl"]
        if analysis.biosample_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][biosample.id]=response['response']['endpointSets']['analysis']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name
        if analysis.cohort_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][cohort.id]=response['response']['endpointSets']['analysis']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["cohort"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name
        if analysis.dataset_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][dataset.id]=response['response']['endpointSets']['analysis']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name
        if analysis.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['analysis']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if analysis.individual_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][individual.id]=response['response']['endpointSets']['analysis']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name
        if analysis.run_lookup == True:
            new_response['response']['endpointSets'][analysis.id]["endpoints"][run.id]=response['response']['endpointSets']['analysis']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][analysis.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][analysis.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][analysis.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name
    if biosample.endpoint_name!='' and biosample.enable_endpoint==True:
        new_response['response']['endpointSets'][biosample.id]=response['response']['endpointSets']['biosample']
        new_response['response']['endpointSets'][biosample.id]["entryType"]=biosample.id
        new_response['response']['endpointSets'][biosample.id]["openAPIEndpointsDefinition"]=biosample.open_api_endpoints_definition
        new_response['response']['endpointSets'][biosample.id]["rootUrl"]=conf.complete_url+'/'+biosample.endpoint_name
        if biosample.singleEntryUrl == True:
            new_response['response']['endpointSets'][biosample.id]["singleEntryUrl"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][biosample.id]["singleEntryUrl"]
        if biosample.analysis_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][analysis.id]=response['response']['endpointSets']['biosample']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name
        if biosample.cohort_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][cohort.id]=response['response']['endpointSets']['biosample']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["cohort"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name
        if biosample.dataset_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][dataset.id]=response['response']['endpointSets']['biosample']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name
        if biosample.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['biosample']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if biosample.individual_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][individual.id]=response['response']['endpointSets']['biosample']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name
        if biosample.run_lookup == True:
            new_response['response']['endpointSets'][biosample.id]["endpoints"][run.id]=response['response']['endpointSets']['biosample']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][biosample.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][biosample.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][biosample.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name
    if cohort.endpoint_name!='' and cohort.enable_endpoint==True:
        new_response['response']['endpointSets'][cohort.id]=response['response']['endpointSets']['cohort']
        new_response['response']['endpointSets'][cohort.id]["entryType"]=cohort.id
        new_response['response']['endpointSets'][cohort.id]["openAPIEndpointsDefinition"]=cohort.open_api_endpoints_definition
        new_response['response']['endpointSets'][cohort.id]["rootUrl"]=conf.complete_url+'/'+cohort.endpoint_name
        if cohort.singleEntryUrl == True:
            new_response['response']['endpointSets'][cohort.id]["singleEntryUrl"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][cohort.id]["singleEntryUrl"]
        if cohort.analysis_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][analysis.id]=response['response']['endpointSets']['cohort']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name
        if cohort.biosample_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][biosample.id]=response['response']['endpointSets']['cohort']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name
        if cohort.dataset_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][dataset.id]=response['response']['endpointSets']['cohort']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name
        if cohort.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['cohort']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if cohort.individual_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][individual.id]=response['response']['endpointSets']['cohort']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name
        if cohort.run_lookup == True:
            new_response['response']['endpointSets'][cohort.id]["endpoints"][run.id]=response['response']['endpointSets']['cohort']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][cohort.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][cohort.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][cohort.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name
    if dataset.endpoint_name!='' and dataset.enable_endpoint==True:
        new_response['response']['endpointSets'][dataset.id]=response['response']['endpointSets']['dataset']
        new_response['response']['endpointSets'][dataset.id]["entryType"]=dataset.id
        new_response['response']['endpointSets'][dataset.id]["openAPIEndpointsDefinition"]=dataset.open_api_endpoints_definition
        new_response['response']['endpointSets'][dataset.id]["rootUrl"]=conf.complete_url+'/'+dataset.endpoint_name
        if dataset.singleEntryUrl == True:
            new_response['response']['endpointSets'][dataset.id]["singleEntryUrl"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][dataset.id]["singleEntryUrl"]
        if dataset.analysis_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][analysis.id]=response['response']['endpointSets']['dataset']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name
        if dataset.biosample_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][biosample.id]=response['response']['endpointSets']['dataset']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name
        if dataset.cohort_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][cohort.id]=response['response']['endpointSets']['dataset']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name
        if dataset.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['dataset']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if dataset.individual_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][individual.id]=response['response']['endpointSets']['dataset']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name
        if dataset.run_lookup == True:
            new_response['response']['endpointSets'][dataset.id]["endpoints"][run.id]=response['response']['endpointSets']['dataset']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][dataset.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][dataset.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][dataset.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name
    if genomicVariant.endpoint_name!='' and genomicVariant.enable_endpoint==True:
        new_response['response']['endpointSets'][genomicVariant.id]=response['response']['endpointSets']['genomicVariant']
        new_response['response']['endpointSets'][genomicVariant.id]["entryType"]=genomicVariant.id
        new_response['response']['endpointSets'][genomicVariant.id]["openAPIEndpointsDefinition"]=genomicVariant.open_api_endpoints_definition
        new_response['response']['endpointSets'][genomicVariant.id]["rootUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name
        if genomicVariant.singleEntryUrl == True:
            new_response['response']['endpointSets'][genomicVariant.id]["singleEntryUrl"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}'
        else:
            del new_response['response']['endpointSets'][genomicVariant.id]["singleEntryUrl"]
        if genomicVariant.analysis_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][analysis.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+analysis.endpoint_name
        if genomicVariant.biosample_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][biosample.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+biosample.endpoint_name
        if genomicVariant.cohort_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][cohort.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+cohort.endpoint_name
        if genomicVariant.dataset_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][dataset.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+dataset.endpoint_name
        if genomicVariant.individual_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][individual.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+individual.endpoint_name
        if genomicVariant.run_lookup == True:
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][run.id]=response['response']['endpointSets']['genomicVariant']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][genomicVariant.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][genomicVariant.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+genomicVariant.endpoint_name+'/{variantInternalId}/'+run.endpoint_name
    if individual.endpoint_name!='' and individual.enable_endpoint==True:
        new_response['response']['endpointSets'][individual.id]=response['response']['endpointSets']['individual']
        new_response['response']['endpointSets'][individual.id]["entryType"]=individual.id
        new_response['response']['endpointSets'][individual.id]["openAPIEndpointsDefinition"]=individual.open_api_endpoints_definition
        new_response['response']['endpointSets'][individual.id]["rootUrl"]=conf.complete_url+'/'+individual.endpoint_name
        if individual.singleEntryUrl == True:
            new_response['response']['endpointSets'][individual.id]["singleEntryUrl"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][individual.id]["singleEntryUrl"]
        if individual.analysis_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][analysis.id]=response['response']['endpointSets']['individual']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name
        if individual.biosample_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][biosample.id]=response['response']['endpointSets']['individual']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name
        if individual.cohort_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][cohort.id]=response['response']['endpointSets']['individual']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name
        if individual.dataset_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][dataset.id]=response['response']['endpointSets']['individual']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name
        if individual.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['individual']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if individual.run_lookup == True:
            new_response['response']['endpointSets'][individual.id]["endpoints"][run.id]=response['response']['endpointSets']['individual']["endpoints"]["run"]
            if run.id != 'run':
                del new_response['response']['endpointSets'][individual.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][individual.id]["endpoints"][run.id]["returnedEntryType"]=run.id
            new_response['response']['endpointSets'][individual.id]["endpoints"][run.id]["url"]=conf.complete_url+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name
    if run.endpoint_name!='' and run.enable_endpoint==True:
        new_response['response']['endpointSets'][run.id]=response['response']['endpointSets']['run']
        new_response['response']['endpointSets'][run.id]["entryType"]=run.id
        new_response['response']['endpointSets'][run.id]["openAPIEndpointsDefinition"]=run.open_api_endpoints_definition
        new_response['response']['endpointSets'][run.id]["rootUrl"]=conf.complete_url+'/'+run.endpoint_name
        if run.singleEntryUrl == True:
            new_response['response']['endpointSets'][run.id]["singleEntryUrl"]=conf.complete_url+'/'+run.endpoint_name+'/{id}'
        else:
            del new_response['response']['endpointSets'][run.id]["singleEntryUrl"]
        if run.analysis_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][analysis.id]=response['response']['endpointSets']['run']["endpoints"]["analysis"]
            if analysis.id != 'analysis':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["analysis"]
            new_response['response']['endpointSets'][run.id]["endpoints"][analysis.id]["returnedEntryType"]=analysis.id
            new_response['response']['endpointSets'][run.id]["endpoints"][analysis.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name
        if run.biosample_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][biosample.id]=response['response']['endpointSets']['run']["endpoints"]["biosample"]
            if biosample.id != 'biosample':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["biosample"]
            new_response['response']['endpointSets'][run.id]["endpoints"][biosample.id]["returnedEntryType"]=biosample.id
            new_response['response']['endpointSets'][run.id]["endpoints"][biosample.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name
        if run.cohort_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][cohort.id]=response['response']['endpointSets']['run']["endpoints"]["cohort"]
            if cohort.id != 'cohort':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["run"]
            new_response['response']['endpointSets'][run.id]["endpoints"][cohort.id]["returnedEntryType"]=cohort.id
            new_response['response']['endpointSets'][run.id]["endpoints"][cohort.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name
        if run.dataset_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][dataset.id]=response['response']['endpointSets']['run']["endpoints"]["dataset"]
            if dataset.id != 'dataset':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["dataset"]
            new_response['response']['endpointSets'][run.id]["endpoints"][dataset.id]["returnedEntryType"]=dataset.id
            new_response['response']['endpointSets'][run.id]["endpoints"][dataset.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name
        if run.genomicVariant_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][genomicVariant.id]=response['response']['endpointSets']['run']["endpoints"]["genomicVariant"]
            if genomicVariant.id != 'genomicVariant':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["genomicVariant"]
            new_response['response']['endpointSets'][run.id]["endpoints"][genomicVariant.id]["returnedEntryType"]=genomicVariant.id
            new_response['response']['endpointSets'][run.id]["endpoints"][genomicVariant.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name
        if run.individual_lookup == True:
            new_response['response']['endpointSets'][run.id]["endpoints"][individual.id]=response['response']['endpointSets']['run']["endpoints"]["individual"]
            if individual.id != 'individual':
                del new_response['response']['endpointSets'][run.id]["endpoints"]["individual"]
            new_response['response']['endpointSets'][run.id]["endpoints"][individual.id]["returnedEntryType"]=individual.id
            new_response['response']['endpointSets'][run.id]["endpoints"][individual.id]["url"]=conf.complete_url+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name
    return new_response

@log_with_args(level)
def build_response_summary(self, exists, num_total_results, response):
    try:
        if num_total_results is None:
            response['responseSummary']['exists']= exists
            return response
        else:
            response['responseSummary']['exists']= exists
            response['responseSummary']['numTotalResults']= num_total_results
            return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
def build_response_summary_by_dataset(self, datasets, dict_counts, response):
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
            response["responseSummary"]["exists"]=True
        elif count > 0:
            response["responseSummary"]["exists"]=count > 0
            response["responseSummary"]["numTotalResults"]=count
            return response
        else:
            RequestAttributes.returned_granularity = 'boolean'
            response["responseSummary"]["exists"]=False
            return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
def build_meta(self, entity_schema: Optional[DefaultSchemas], response: dict):
    try:
        response["meta"]["beaconId"]=conf.beacon_id
        response["meta"]["apiVersion"]=conf.api_version
        response["meta"]["returnedGranularity"]=RequestAttributes.returned_granularity
        response["meta"]["receivedRequestSummary"]=RequestAttributes.qparams.summary()
        response["meta"]["returnedSchemas"]=[entity_schema.value] if entity_schema is not None else []
        return response
    except Exception as e:
        response["meta"]["beaconId"]=conf.beacon_id
        response["meta"]["apiVersion"]=conf.api_version
        response["meta"]["returnedGranularity"]="boolean"
        response["meta"]["receivedRequestSummary"]={"apiVersion": "Request did not reach server",
                                        "requestedSchemas": [],
                                        "pagination": {},
                                        "requestedGranularity": "boolean"}
        response["meta"]["returnedSchemas"]=[entity_schema.value] if entity_schema is not None else []
        return response

@log_with_args(level)
def build_info_meta(self, entity_schema: Optional[DefaultSchemas], response: dict):
    try:
        response["meta"]["beaconId"]=conf.beacon_id
        response["meta"]["apiVersion"]=conf.api_version
        response["meta"]["returnedSchemas"]=[entity_schema.value] if entity_schema is not None else []
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
def build_response_by_dataset(self, datasets, data, dict_counts, response):
    try:
        resultSet={}
        granularity = RequestAttributes.qparams.query.requestedGranularity
        for dataset in datasets:
            if dataset.granularity == 'record' and RequestAttributes.allowed_granularity=='record' and granularity =='record':
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:
                        resultSet['id']=dataset.dataset
                        resultSet['setType']="dataset"
                        resultSet['exists']=dict_counts[dataset.dataset] > 0
                        resultSet['resultsCount']=dict_counts[dataset.dataset]
                        resultSet['results']=data[dataset.dataset]
                        resultSet['resultsHandover']=handover["handover"]
                        
                    else:
                        resultSet['id']=dataset.dataset
                        resultSet['setType']='dataset'
                        resultSet['exists']=dict_counts[dataset.dataset] > 0
                        resultSet['resultsCount']=dict_counts[dataset.dataset]
                        resultSet['results']=data[dataset.dataset]
                        
                if conf.imprecise_count !=0:
                    if dict_counts[dataset.dataset] < conf.imprecise_count:
                        resultSet['resultsCount']=conf.imprecise_count
                        resultSet["countAdjustedTo"]=[conf.imprecise_count]
                        resultSet["countPrecision"]='imprecise'
                        
                elif conf.round_to_tens == True:
                    resultSet['resultsCount']=math.ceil(dict_counts[dataset.dataset] / 10.0) * 10
                    resultSet["countAdjustedTo"]=['immediate ten']
                    resultSet["countPrecision"]='rounded'
                    
                elif conf.round_to_hundreds == True:
                    resultSet['resultsCount']=math.ceil(dict_counts[dataset.dataset] / 100.0) * 100
                    resultSet["countAdjustedTo"]=['immediate hundred']
                    resultSet["countPrecision"]='rounded'
                    
            elif dataset.granularity != 'boolean' and RequestAttributes.allowed_granularity != 'boolean' and granularity != 'boolean':
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:
                        resultSet['id']=dataset.dataset
                        resultSet['setType']="dataset"
                        resultSet['exists']=dict_counts[dataset.dataset] > 0
                        resultSet['resultsCount']=dict_counts[dataset.dataset]
                        resultSet['resultsHandover']=handover["handover"]
                        
                    else:
                        resultSet['id']=dataset.dataset
                        resultSet['setType']="dataset"
                        resultSet['exists']=dict_counts[dataset.dataset] > 0
                        resultSet['resultsCount']=dict_counts[dataset.dataset]
                        
            else:
                for handover in list_of_handovers_per_dataset:
                    if handover["dataset"]==dataset.dataset:
                        resultSet['id']=dataset.dataset
                        resultSet['setType']="dataset"
                        resultSet['exists']=dict_counts[dataset.dataset] > 0
                        resultSet['resultsHandover']=handover["handover"]
            with open('beacon/response/templates/{}/resultSets.json.jinja'.format("v2.2.0"), 'r') as template:
                template = json.dumps(json.load(template))
                template = template.replace('"{{exists|tojson}}"', '{{exists|tojson}}')
                template = template.replace('"{{resultsCount}}"', '{{resultsCount}}')
            template = Template(template)
            resultSet = template.render(resultSet)
            resultSet = json.loads(resultSet)
            resultSet["results"]=data[dataset.dataset]
            response["response"]["resultSets"].append(resultSet)


        return response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_error_response(self, errorCode, errorMessage):
    try:
        with open('beacon/response/templates/{}/error.json'.format("v2.2.0"), 'r') as template:
            response = json.load(template)
        response = build_meta(self, None, response)
        response['error']['errorCode']=str(errorCode)
        response['error']['errorMessage']=str(errorMessage)
        return response
    except Exception:
        raise

@log_with_args(level)
def build_configuration(self, response):
    try:
        response['response']['securityAttributes']['defaultGranularity']=conf.default_beacon_granularity
        response['response']['securityAttributes']['securityLevels']=conf.security_levels
        response['response']['maturityAttributes']['productionStatus']=conf.environment.upper()
        if analysis.endpoint_name != '' and analysis.enable_endpoint == True:
            response['response']['entryTypes'][analysis.id]==response['response']['entryTypes']['analysis']
            if analysis.id != 'analysis':
                del response['response']['entryTypes']['analysis']
            response['response']['entryTypes'][analysis.id]['id']=analysis.id
            response['response']['entryTypes'][analysis.id]["name"]=analysis.name
            response['response']['entryTypes'][analysis.id]['ontologyTermForThisType']['id']=analysis.ontology_id
            response['response']['entryTypes'][analysis.id]['ontologyTermForThisType']['name']=analysis.ontology_name
            response['response']['entryTypes'][analysis.id]['partOfSpecification']=analysis.specification
            response['response']['entryTypes'][analysis.id]['description']=analysis.description
            response['response']['entryTypes'][analysis.id]['defaultSchema']['id']=analysis.defaultSchema_id
            response['response']['entryTypes'][analysis.id]['defaultSchema']['name']=analysis.defaultSchema_name
            response['response']['entryTypes'][analysis.id]['defaultSchema']['referenceToSchemaDefinition']=analysis.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][analysis.id]['defaultSchema']['schemaVersion']=analysis.defaultSchema_schema_version
            response['response']['entryTypes'][analysis.id]['additionallySupportedSchemas']=analysis.aditionally_supported_schemas
            response['response']['entryTypes'][analysis.id]['nonFilteredQueriesAllowed']=analysis.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['analysis']
        if biosample.endpoint_name != '' and biosample.enable_endpoint == True:
            response['response']['entryTypes'][biosample.id]==response['response']['entryTypes']['biosample']
            if biosample.id != 'biosample':
                del response['response']['entryTypes']['biosample']
            response['response']['entryTypes'][biosample.id]['id']=biosample.id
            response['response']['entryTypes'][biosample.id]["name"]=biosample.name
            response['response']['entryTypes'][biosample.id]['ontologyTermForThisType']['id']=biosample.ontology_id
            response['response']['entryTypes'][biosample.id]['ontologyTermForThisType']['name']=biosample.ontology_name
            response['response']['entryTypes'][biosample.id]['partOfSpecification']=biosample.specification
            response['response']['entryTypes'][biosample.id]['description']=biosample.description
            response['response']['entryTypes'][biosample.id]['defaultSchema']['id']=biosample.defaultSchema_id
            response['response']['entryTypes'][biosample.id]['defaultSchema']['name']=biosample.defaultSchema_name
            response['response']['entryTypes'][biosample.id]['defaultSchema']['referenceToSchemaDefinition']=biosample.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][biosample.id]['defaultSchema']['schemaVersion']=biosample.defaultSchema_schema_version
            response['response']['entryTypes'][biosample.id]['additionallySupportedSchemas']=biosample.aditionally_supported_schemas
            response['response']['entryTypes'][biosample.id]['nonFilteredQueriesAllowed']=biosample.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['biosample']
        if cohort.endpoint_name!='' and cohort.enable_endpoint==True:
            response['response']['entryTypes'][cohort.id]==response['response']['entryTypes']['cohort']
            if cohort.id != 'cohort':
                del response['response']['entryTypes']['cohort']
            response['response']['entryTypes'][cohort.id]['id']=cohort.id
            response['response']['entryTypes'][cohort.id]["name"]=cohort.name
            response['response']['entryTypes'][cohort.id]['ontologyTermForThisType']['id']=cohort.ontology_id
            response['response']['entryTypes'][cohort.id]['ontologyTermForThisType']['name']=cohort.ontology_name
            response['response']['entryTypes'][cohort.id]['partOfSpecification']=cohort.specification
            response['response']['entryTypes'][cohort.id]['description']=cohort.description
            response['response']['entryTypes'][cohort.id]['defaultSchema']['id']=cohort.defaultSchema_id
            response['response']['entryTypes'][cohort.id]['defaultSchema']['name']=cohort.defaultSchema_name
            response['response']['entryTypes'][cohort.id]['defaultSchema']['referenceToSchemaDefinition']=cohort.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][cohort.id]['defaultSchema']['schemaVersion']=cohort.defaultSchema_schema_version
            response['response']['entryTypes'][cohort.id]['additionallySupportedSchemas']=cohort.aditionally_supported_schemas
            response['response']['entryTypes'][cohort.id]['nonFilteredQueriesAllowed']=cohort.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['cohort']
        if dataset.endpoint_name!='' and dataset.enable_endpoint==True:
            response['response']['entryTypes'][dataset.id]==response['response']['entryTypes']['dataset']
            if dataset.id != 'dataset':
                del response['response']['entryTypes']['dataset']
            response['response']['entryTypes'][dataset.id]['id']=dataset.id
            response['response']['entryTypes'][dataset.id]["name"]=dataset.name
            response['response']['entryTypes'][dataset.id]['ontologyTermForThisType']['id']=dataset.ontology_id
            response['response']['entryTypes'][dataset.id]['ontologyTermForThisType']['name']=dataset.ontology_name
            response['response']['entryTypes'][dataset.id]['partOfSpecification']=dataset.specification
            response['response']['entryTypes'][dataset.id]['description']=dataset.description
            response['response']['entryTypes'][dataset.id]['defaultSchema']['id']=dataset.defaultSchema_id
            response['response']['entryTypes'][dataset.id]['defaultSchema']['name']=dataset.defaultSchema_name
            response['response']['entryTypes'][dataset.id]['defaultSchema']['referenceToSchemaDefinition']=dataset.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][dataset.id]['defaultSchema']['schemaVersion']=dataset.defaultSchema_schema_version
            response['response']['entryTypes'][dataset.id]['additionallySupportedSchemas']=dataset.aditionally_supported_schemas
            response['response']['entryTypes'][dataset.id]['nonFilteredQueriesAllowed']=dataset.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['dataset']
        if genomicVariant.endpoint_name!='' and genomicVariant.enable_endpoint==True:
            response['response']['entryTypes'][genomicVariant.id]==response['response']['entryTypes']['genomicVariant']
            if genomicVariant.id != 'genomicVariant':
                del response['response']['entryTypes']['genomicVariant']
            response['response']['entryTypes'][genomicVariant.id]['id']=genomicVariant.id
            response['response']['entryTypes'][genomicVariant.id]["name"]=genomicVariant.name
            response['response']['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['id']=genomicVariant.ontology_id
            response['response']['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['name']=genomicVariant.ontology_name
            response['response']['entryTypes'][genomicVariant.id]['partOfSpecification']=genomicVariant.specification
            response['response']['entryTypes'][genomicVariant.id]['description']=genomicVariant.description
            response['response']['entryTypes'][genomicVariant.id]['defaultSchema']['id']=genomicVariant.defaultSchema_id
            response['response']['entryTypes'][genomicVariant.id]['defaultSchema']['name']=genomicVariant.defaultSchema_name
            response['response']['entryTypes'][genomicVariant.id]['defaultSchema']['referenceToSchemaDefinition']=genomicVariant.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][genomicVariant.id]['defaultSchema']['schemaVersion']=genomicVariant.defaultSchema_schema_version
            response['response']['entryTypes'][genomicVariant.id]['additionallySupportedSchemas']=genomicVariant.aditionally_supported_schemas
            response['response']['entryTypes'][genomicVariant.id]['nonFilteredQueriesAllowed']=genomicVariant.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['genomicVariant']
        if individual.endpoint_name!='' and individual.enable_endpoint==True:
            response['response']['entryTypes'][individual.id]==response['response']['entryTypes']['individual']
            if individual.id != 'individual':
                del response['response']['entryTypes']['individual']
            response['response']['entryTypes'][individual.id]['id']=individual.id
            response['response']['entryTypes'][individual.id]["name"]=individual.name
            response['response']['entryTypes'][individual.id]['ontologyTermForThisType']['id']=individual.ontology_id
            response['response']['entryTypes'][individual.id]['ontologyTermForThisType']['name']=individual.ontology_name
            response['response']['entryTypes'][individual.id]['partOfSpecification']=individual.specification
            response['response']['entryTypes'][individual.id]['description']=individual.description
            response['response']['entryTypes'][individual.id]['defaultSchema']['id']=individual.defaultSchema_id
            response['response']['entryTypes'][individual.id]['defaultSchema']['name']=individual.defaultSchema_name
            response['response']['entryTypes'][individual.id]['defaultSchema']['referenceToSchemaDefinition']=individual.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][individual.id]['defaultSchema']['schemaVersion']=individual.defaultSchema_schema_version
            response['response']['entryTypes'][individual.id]['additionallySupportedSchemas']=individual.aditionally_supported_schemas
            response['response']['entryTypes'][individual.id]['nonFilteredQueriesAllowed']=individual.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['individual']
        if run.endpoint_name!='' and run.enable_endpoint==True:
            response['response']['entryTypes'][run.id]==response['response']['entryTypes']['run']
            if run.id != 'run':
                del response['response']['entryTypes']['run']
            response['response']['entryTypes'][run.id]['id']=run.id
            response['response']['entryTypes'][run.id]["name"]=run.name
            response['response']['entryTypes'][run.id]['ontologyTermForThisType']['id']=run.ontology_id
            response['response']['entryTypes'][run.id]['ontologyTermForThisType']['name']=run.ontology_name
            response['response']['entryTypes'][run.id]['partOfSpecification']=run.specification
            response['response']['entryTypes'][run.id]['description']=run.description
            response['response']['entryTypes'][run.id]['defaultSchema']['id']=run.defaultSchema_id
            response['response']['entryTypes'][run.id]['defaultSchema']['name']=run.defaultSchema_name
            response['response']['entryTypes'][run.id]['defaultSchema']['referenceToSchemaDefinition']=run.defaultSchema_reference_to_schema_definition
            response['response']['entryTypes'][run.id]['defaultSchema']['schemaVersion']=run.defaultSchema_schema_version
            response['response']['entryTypes'][run.id]['additionallySupportedSchemas']=run.aditionally_supported_schemas
            response['response']['entryTypes'][run.id]['nonFilteredQueriesAllowed']=run.allow_queries_without_filters
        else:
            del response['response']['entryTypes']['run']
        if response['response']['entryTypes'] == {}:
            ErrorClass.error_code=500
            ErrorClass.error_message='Please, provide an entry type in conf to be able to have a beacon instance with at least one endpoint to query.'
            raise

        return response
    except Exception:
        self._error.handle_exception(e, None)
        raise
