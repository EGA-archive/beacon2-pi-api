from beacon.logs.logs import log_with_args_initial
from beacon.conf.conf import level
from beacon.views.collection import CollectionView
from beacon.views.configuration import ConfigurationView
from beacon.views.entry_types import EntryTypesView
from beacon.views.filtering_terms import FilteringTermsView
from beacon.views.info import InfoView
from beacon.views.map import MapView
from beacon.views.phenogeno import PhenoGenoView
from beacon.views.service_info import ServiceInfoView
from beacon.conf.conf import level, uri_subpath
import aiohttp.web as web
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run

@log_with_args_initial(level)
def append_routes(app):
    app.add_routes([web.post(uri_subpath, InfoView)])
    app.add_routes([web.post(uri_subpath+'/info', InfoView)])
    app.add_routes([web.post(uri_subpath+'/entry_types', EntryTypesView)])
    app.add_routes([web.post(uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.post(uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.post(uri_subpath+'/map', MapView)])
    app.add_routes([web.post(uri_subpath+'/filtering_terms', FilteringTermsView)])
    app.add_routes([web.get(uri_subpath, InfoView)])
    app.add_routes([web.get(uri_subpath+'/info', InfoView)])
    app.add_routes([web.get(uri_subpath+'/entry_types', EntryTypesView)])
    app.add_routes([web.get(uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.get(uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.get(uri_subpath+'/map', MapView)])
    app.add_routes([web.get(uri_subpath+'/filtering_terms', FilteringTermsView)])
    if dataset.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name, CollectionView)])
        app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name, CollectionView)])
        if dataset.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}', CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}', CollectionView)])
        if dataset.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if dataset.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if dataset.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if dataset.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if dataset.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
        if dataset.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if cohort.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name, CollectionView)])
        app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name, CollectionView)])
        if cohort.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}', CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}', CollectionView)])
        if cohort.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if cohort.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if cohort.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if cohort.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if cohort.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
        if cohort.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if analysis.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name, PhenoGenoView)])
        app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name, PhenoGenoView)])
        if analysis.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}', PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}', PhenoGenoView)])
        if analysis.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if analysis.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if analysis.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if analysis.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if analysis.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
        if analysis.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if biosample.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name, PhenoGenoView)])
        app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name, PhenoGenoView)])
        if biosample.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}', PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}', PhenoGenoView)])
        if biosample.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if biosample.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if biosample.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if biosample.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if biosample.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
        if biosample.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if genomicVariant.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name, PhenoGenoView)])
        app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if genomicVariant.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', PhenoGenoView)])
        if genomicVariant.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if genomicVariant.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if genomicVariant.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if genomicVariant.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if genomicVariant.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
        if genomicVariant.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if individual.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name, PhenoGenoView)])
        app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name, PhenoGenoView)])
        if individual.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}', PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}', PhenoGenoView)])
        if individual.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if individual.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if individual.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if individual.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if individual.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if individual.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGenoView)])
    if run.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name, PhenoGenoView)])
        app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name, PhenoGenoView)])
        if run.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}', PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}', PhenoGenoView)])
        if run.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, CollectionView)])
        if run.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGenoView)])
        if run.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, CollectionView)])
        if run.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGenoView)])
        if run.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGenoView)])
        if run.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGenoView)])
    return app