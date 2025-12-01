from beacon.logs.logs import log_with_args_initial
from beacon.conf.conf import level
from beacon.conf.conf import level, uri_subpath
import aiohttp.web as web
from beacon.models.EUCAIM.conf.entry_types import imaging, disease, tumor, patient
from beacon.views.entry_type import EntryTypeView

@log_with_args_initial(level)
def extend_routes(app):
    if imaging.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name, EntryTypeView)])
        if imaging.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name+'/{id}', EntryTypeView)])
        if imaging.patient_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
        if imaging.disease_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
        if imaging.tumor_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+imaging.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
    if disease.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+disease.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+disease.endpoint_name, EntryTypeView)])
        if disease.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+disease.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+disease.endpoint_name+'/{id}', EntryTypeView)])
        if disease.patient_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
        if disease.imaging_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
        if disease.tumor_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+disease.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
    if tumor.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+tumor.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+tumor.endpoint_name, EntryTypeView)])
        if tumor.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+tumor.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+tumor.endpoint_name+'/{id}', EntryTypeView)])
        if tumor.patient_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+patient.endpoint_name, EntryTypeView)])
        if tumor.disease_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
        if tumor.imaging_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+tumor.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
    if patient.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+patient.endpoint_name, EntryTypeView)])
        app.add_routes([web.get(uri_subpath+'/'+patient.endpoint_name, EntryTypeView)])
        if patient.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+patient.endpoint_name+'/{id}', EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+patient.endpoint_name+'/{id}', EntryTypeView)])
        if patient.tumor_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+tumor.endpoint_name, EntryTypeView)])
        if patient.disease_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+disease.endpoint_name, EntryTypeView)])
        if patient.imaging_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
            app.add_routes([web.get(uri_subpath+'/'+patient.endpoint_name+'/{id}/'+imaging.endpoint_name, EntryTypeView)])
    return app