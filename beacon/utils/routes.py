from beacon.logs.logs import log_with_args_initial, LOG
from beacon.views.collection import CollectionEntryTypeView
from beacon.views.non_collection import EntryTypeView 
from beacon.views.configuration import ConfigurationView
from beacon.views.entry_types import EntryTypesEndpointView
from beacon.views.filtering_terms import FilteringTermsView
from beacon.views.info import InfoView
from beacon.views.map import MapView
from beacon.views.service_info import ServiceInfoView
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.utils.modules import load_routes

@log_with_args_initial(config.level)
def append_routes(app):
    app.add_routes([web.post(config.uri_subpath, InfoView)])
    app.add_routes([web.post(config.uri_subpath+'/info', InfoView)])
    app.add_routes([web.post(config.uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.post(config.uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.post(config.uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.post(config.uri_subpath+'/map', MapView)])
    app.add_routes([web.post(config.uri_subpath+'/filtering_terms', FilteringTermsView)])
    app.add_routes([web.get(config.uri_subpath, InfoView)])
    app.add_routes([web.get(config.uri_subpath+'/info', InfoView)])
    app.add_routes([web.get(config.uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.get(config.uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.get(config.uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.get(config.uri_subpath+'/map', MapView)])
    app.add_routes([web.get(config.uri_subpath+'/filtering_terms', FilteringTermsView)])
    routes_to_add = load_routes()
    for url, response_type in routes_to_add.items():
        if response_type == ['non_collection']:
            app.add_routes([web.get(config.uri_subpath+'/'+url, EntryTypeView)])
            app.add_routes([web.post(config.uri_subpath+'/'+url, EntryTypeView)])
        elif response_type == ['collection']:
            app.add_routes([web.get(config.uri_subpath+'/'+url, CollectionEntryTypeView)])
            app.add_routes([web.post(config.uri_subpath+'/'+url, CollectionEntryTypeView)])
    return app