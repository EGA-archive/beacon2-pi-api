from beacon.connections.mongo.__init__ import collections, imagestudies, patients
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf_override import config
import yaml

def import_collections_confile():
    with open("/beacon/models/EUCAIM/conf/entry_types/collections.yml", 'r') as pfile:
        collections_confile= yaml.safe_load(pfile)
    pfile.close()
    return collections_confile

def import_patients_confile():
    with open("/beacon/models/EUCAIM/conf/entry_types/patients.yml", 'r') as pfile:
        patients_confile= yaml.safe_load(pfile)
    pfile.close()
    return patients_confile


@log_with_args_mongo(config.level)
def get_non_collections_cross_query_attributes(self, entry_type, pre_entry_type):
    patients_confile=import_patients_confile()
    collections_confile=import_collections_confile()
    # For cross queries, save the attributes for the translation (linkage) between endpoints (idq to idq2) and the name of the collection for the initial endpoint queried (secondary_collection)
    mapping = {
    collections_confile["collections"]["endpoint_name"]: {
                    patients_confile["patients"]["endpoint_name"]: {"idq": "id",
                                                "idq2": "datasetId",
                                                "secondary_collection": patients}},
    patients_confile["patients"]["endpoint_name"]: {
                    collections_confile["collections"]["endpoint_name"]: {"idq": "datasetId",
                                                "idq2": "datasetId",
                                                "secondary_collection": collections}}}
    return mapping[entry_type][pre_entry_type]