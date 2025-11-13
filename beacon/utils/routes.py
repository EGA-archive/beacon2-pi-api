from beacon.logs.logs import log_with_args_initial, LOG
from beacon.conf.conf import level
from beacon.views.collection_entry_type import CollectionEntryTypeView
from beacon.views.configuration import ConfigurationView
from beacon.views.entry_types import EntryTypesEndpointView
from beacon.views.filtering_terms import FilteringTermsView
from beacon.views.info import InfoView
from beacon.views.map import MapView
from beacon.views.service_info import ServiceInfoView
from beacon.conf.conf import level, uri_subpath
import aiohttp.web as web
import os

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
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "routes" in subdirs:
            complete_module='beacon.models.'+folder+'.routes.routes'
            import importlib
            module = importlib.import_module(complete_module, package=None)
            app = module.extend_routes(app)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+'/'+subfolder)
                if "routes" in underdirs:
                    complete_module='beacon.models.'+folder+'.'+subfolder+'.routes.routes'
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    app = module.extend_routes(app)
    return app