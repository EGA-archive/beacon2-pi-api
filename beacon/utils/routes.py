from beacon.logs.logs import log_with_args_initial
from beacon.conf.conf import level
from beacon.views.model.collection_entry_type import CollectionEntryTypeView
from beacon.views.framework.configuration import ConfigurationView
from beacon.views.framework.entry_types import EntryTypesEndpointView
from beacon.views.framework.filtering_terms import FilteringTermsView
from beacon.views.framework.info import InfoView
from beacon.views.framework.map import MapView
from beacon.views.model.entry_type import EntryTypeView
from beacon.views.framework.service_info import ServiceInfoView
from beacon.conf.conf import level, uri_subpath
import aiohttp.web as web
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run

@log_with_args_initial(level)
def append_routes(app):
    app.add_routes([web.post(uri_subpath, InfoView)])
    app.add_routes([web.post(uri_subpath+'/info', InfoView)])
    app.add_routes([web.post(uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.post(uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.post(uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.post(uri_subpath+'/map', MapView)])
    app.add_routes([web.post(uri_subpath+'/filtering_terms', FilteringTermsView)])
    app.add_routes([web.get(uri_subpath, InfoView)])
    app.add_routes([web.get(uri_subpath+'/info', InfoView)])
    app.add_routes([web.get(uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.get(uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.get(uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.get(uri_subpath+'/map', MapView)])
    app.add_routes([web.get(uri_subpath+'/filtering_terms', FilteringTermsView)])
    if dataset.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name, CollectionEntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if dataset.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}', CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}', CollectionEntryTypeView)])
        if dataset.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if dataset.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if dataset.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if dataset.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if dataset.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
        if dataset.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if cohort.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name, CollectionEntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if cohort.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}', CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}', CollectionEntryTypeView)])
        if cohort.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if cohort.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if cohort.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if cohort.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if cohort.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
        if cohort.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if analysis.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name, EntryTypeView)])
        if analysis.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}', EntryTypeView)])
        if analysis.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if analysis.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if analysis.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if analysis.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if analysis.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
        if analysis.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if biosample.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name, EntryTypeView)])
        if biosample.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}', EntryTypeView)])
        if biosample.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if biosample.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if biosample.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if biosample.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if biosample.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
        if biosample.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if genomicVariant.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name, EntryTypeView)])
        if genomicVariant.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', EntryTypeView)])
        if genomicVariant.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if genomicVariant.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if genomicVariant.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if genomicVariant.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if genomicVariant.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
        if genomicVariant.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if individual.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name, EntryTypeView)])
        if individual.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}', EntryTypeView)])
        if individual.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if individual.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if individual.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if individual.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if individual.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if individual.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, EntryTypeView)])
    if run.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name, EntryTypeView)])
        if run.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}', EntryTypeView)])
        if run.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionEntryTypeView)])
        if run.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, EntryTypeView)])
        if run.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionEntryTypeView)])
        if run.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, EntryTypeView)])
        if run.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, EntryTypeView)])
        if run.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, EntryTypeView)])
    return app