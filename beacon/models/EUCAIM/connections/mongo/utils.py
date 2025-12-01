from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import diseases, images, patients, tumors
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level
from beacon.exceptions.exceptions import InvalidRequest
import aiohttp.web as web
from beacon.models.EUCAIM.conf.entry_types import disease, imaging, patient, tumor, dataset

@log_with_args_mongo(level)
def get_non_collections_cross_query_attributes(self, entry_type, pre_entry_type):
    # For cross queries, save the attributes for the translation (linkage) between endpoints (idq to idq2) and the name of the collection for the initial endpoint queried (secondary_collection)
    mapping = {disease.endpoint_name: {imaging.endpoint_name: {"idq": "imageId",
                                                         "idq2": "patientId",
                                                         "secondary_collection": images},
                                        tumor.endpoint_name: {"idq": "diseaseId",
                                                         "idq2": "diseaseId",
                                                         "secondary_collection": tumors},
                                        patient.endpoint_name: {"idq": "patientId",
                                                        "idq2": "patientId",
                                                        "secondary_collection": patients}},
    imaging.endpoint_name: {disease.endpoint_name: {"idq": "diseaseId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": diseases},
                            tumor.endpoint_name: {"idq": "tumorId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": tumors},
                            patient.endpoint_name: {"idq": "patientId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": patients}},
    tumor.endpoint_name: {disease.endpoint_name: {"idq": "diseaseId",
                                                    "idq2": "diseaseId",
                                                    "secondary_collection": diseases},
                            imaging.endpoint_name: {"idq": "imageId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": images},
                            patient.endpoint_name: {"idq": "patientId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": patients}},
    patient.endpoint_name: {disease.endpoint_name: {"idq": "diseaseId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": diseases},
                        tumor.endpoint_name: {"idq": "tumorId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": tumors},
                        imaging.endpoint_name: {"idq": "imageId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": images}}}
    return mapping[entry_type][pre_entry_type]