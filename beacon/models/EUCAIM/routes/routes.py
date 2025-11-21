from beacon.logs.logs import log_with_args_initial
from beacon.conf.conf import level
from beacon.conf.conf import level, uri_subpath
import aiohttp.web as web
from beacon.models.EUCAIM.conf.entry_types import imaging
from beacon.views.entry_type import EntryTypeView

@log_with_args_initial(level)
def extend_routes(app):
    if imaging.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name, EntryTypeView)])
        if imaging.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name+'/{id}', EntryTypeView)])
    return app