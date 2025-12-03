from beacon.connections.mongo.__init__ import diseases, images, patients, tumors
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level
import yaml

def import_dataset_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/disease.yml", 'r') as pfile:
        dataset_confile= yaml.safe_load(pfile)
    pfile.close()
    return dataset_confile

def import_disease_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/disease.yml", 'r') as pfile:
        disease_confile= yaml.safe_load(pfile)
    pfile.close()
    return disease_confile

def import_imaging_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/imaging.yml", 'r') as pfile:
        imaging_confile= yaml.safe_load(pfile)
    pfile.close()
    return imaging_confile

def import_patient_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/patient.yml", 'r') as pfile:
        patient_confile= yaml.safe_load(pfile)
    pfile.close()
    return patient_confile

def import_tumor_confile():
    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/tumor.yml", 'r') as pfile:
        tumor_confile= yaml.safe_load(pfile)
    pfile.close()
    return tumor_confile

@log_with_args_mongo(level)
def get_non_collections_cross_query_attributes(self, entry_type, pre_entry_type):
    disease_confile=import_disease_confile()
    imaging_confile=import_imaging_confile()
    patient_confile=import_imaging_confile()
    tumor_confile=import_tumor_confile()
    # For cross queries, save the attributes for the translation (linkage) between endpoints (idq to idq2) and the name of the collection for the initial endpoint queried (secondary_collection)
    mapping = {disease_confile["disease"]["endpoint_name"]: {imaging_confile["imaging"]["endpoint_name"]: {"idq": "imageId",
                                                         "idq2": "patientId",
                                                         "secondary_collection": images},
                                        tumor_confile["tumor"]["endpoint_name"]: {"idq": "diseaseId",
                                                         "idq2": "diseaseId",
                                                         "secondary_collection": tumors},
                                        patient_confile["patient"]["endpoint_name"]: {"idq": "patientId",
                                                        "idq2": "patientId",
                                                        "secondary_collection": patients}},
    imaging_confile["imaging"]["endpoint_name"]: {disease_confile["disease"]["endpoint_name"]: {"idq": "diseaseId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": diseases},
                            tumor_confile["tumor"]["endpoint_name"]: {"idq": "tumorId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": tumors},
                            patient_confile["patient"]["endpoint_name"]: {"idq": "patientId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": patients}},
    tumor_confile["tumor"]["endpoint_name"]: {disease_confile["disease"]["endpoint_name"]: {"idq": "diseaseId",
                                                    "idq2": "diseaseId",
                                                    "secondary_collection": diseases},
                            imaging_confile["imaging"]["endpoint_name"]: {"idq": "imageId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": images},
                            patient_confile["patient"]["endpoint_name"]: {"idq": "patientId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": patients}},
    patient_confile["patient"]["endpoint_name"]: {disease_confile["disease"]["endpoint_name"]: {"idq": "diseaseId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": diseases},
                        tumor_confile["tumor"]["endpoint_name"]: {"idq": "tumorId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": tumors},
                        imaging_confile["imaging"]["endpoint_name"]: {"idq": "imageId",
                                                    "idq2": "patientId",
                                                    "secondary_collection": images}}}
    return mapping[entry_type][pre_entry_type]