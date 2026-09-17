from beacon.logs.logs import log_with_args_initial
from beacon.views.collection import CollectionEntryTypeView
from beacon.views.non_collection import EntryTypeView 
from beacon.views.configuration import ConfigurationView
from beacon.views.entry_types import EntryTypesEndpointView
from beacon.views.filtering_terms import FilteringTermsView
from beacon.views.info import InfoView
from beacon.views.map import MapView
from beacon.views.service_info import ServiceInfoView
from beacon.views.health import HealthView
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.utils.modules import load_routes

@log_with_args_initial(config.level)
def append_routes(app):
    """Generating the routes to be added to the API"""
    
    # POST API framework routes to be added
    app.add_routes([web.post(config.uri_subpath, InfoView)])
    app.add_routes([web.post(config.uri_subpath+'/info', InfoView)])
    app.add_routes([web.post(config.uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.post(config.uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.post(config.uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.post(config.uri_subpath+'/map', MapView)])
    app.add_routes([web.post(config.uri_subpath+'/filtering_terms', FilteringTermsView)])

    # GET API framework routes to be added
    app.add_routes([web.get(config.uri_subpath, InfoView)])
    app.add_routes([web.get(config.uri_subpath+'/info', InfoView)])
    app.add_routes([web.get(config.uri_subpath+'/entry_types', EntryTypesEndpointView)])
    app.add_routes([web.get(config.uri_subpath+'/service-info', ServiceInfoView)])
    app.add_routes([web.get(config.uri_subpath+'/configuration', ConfigurationView)])
    app.add_routes([web.get(config.uri_subpath+'/map', MapView)])
    app.add_routes([web.get(config.uri_subpath+'/filtering_terms', FilteringTermsView)])
    
    # Health check route, only available by GET
    app.add_routes([web.get(config.uri_subpath+'/health', HealthView)])

    # Load the model specific classes that need to be routed dynamically
    routes_to_add = load_routes()

    # For each of the model classes, add the routes
    for url, response_type in routes_to_add.items():
        # First check if they are a collection or not response type of route
        if response_type == ['non_collection']:
            # Add both POST and GET routes for non collection entry types
            app.add_routes([web.get(config.uri_subpath+'/'+url, EntryTypeView)])
            app.add_routes([web.post(config.uri_subpath+'/'+url, EntryTypeView)])
        elif response_type == ['collection']:
            # Add both POST and GET routes for collection entry types
            app.add_routes([web.get(config.uri_subpath+'/'+url, CollectionEntryTypeView)])
            app.add_routes([web.post(config.uri_subpath+'/'+url, CollectionEntryTypeView)])
    return app