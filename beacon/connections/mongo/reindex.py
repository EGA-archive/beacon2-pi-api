from pymongo.mongo_client import MongoClient
import conf
import os


if conf.database_cluster:
    uri = "mongodb+srv://{}:{}@{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
        conf.database_user,
        conf.database_password,
        conf.database_host
    )
else:
    uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
        conf.database_user,
        conf.database_password,
        conf.database_host,
        conf.database_port,
        conf.database_name,
        conf.database_auth_source
    )

if os.path.isfile(conf.database_certificate):
    uri += '&tls=true&tlsCertificateKeyFile={}'.format(conf.database_certificate)
    if os.path.isfile(conf.database_cafile):
        uri += '&tlsCAFile={}'.format(conf.database_cafile)

client = MongoClient(uri)
try:
    client.beacon.drop_collection("synonyms")
except Exception:
    client.beacon.create_collection(name="synonyms")
try:
    client.beacon.validate_collection("synonyms")
except Exception:
    db=client.beacon.create_collection(name="synonyms")
try:
    client.beacon.validate_collection("targets")
except Exception:
    db=client.beacon.create_collection(name="targets")
try:
    client.beacon.validate_collection("caseLevelData")
except Exception:
    db=client.beacon.create_collection(name="caseLevelData")
try:
    client.beacon.drop_collection("counts")
except Exception:
    client.beacon.create_collection(name="counts")
try:
    client.beacon.validate_collection("counts")
except Exception:
    db=client.beacon.create_collection(name="counts")
try:
    client.beacon.drop_collection("similarities")
except Exception:
    client.beacon.create_collection(name="similarities")
try:
    client.beacon.validate_collection("similarities")
except Exception:
    db=client.beacon.create_collection(name="similarities")
#client.beacon.analyses.create_index([("$**", "text")])
#client.beacon.biosamples.create_index([("$**", "text")])
#client.beacon.cohorts.create_index([("$**", "text")])
#client.beacon.datasets.create_index([("$**", "text")])
#client.beacon.genomicVariations.create_index([("$**", "text")])
#client.beacon.genomicVariations.create_index([("caseLevelData.biosampleId", 1)])
#client.beacon.genomicVariations.create_index([("variation.location.interval.end.value", -1), ("variation.location.interval.start.value", 1)])
#client.beacon.genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1)])
client.beacon.genomicVariations.create_index([("datasetId", 1)])
#client.beacon.genomicVariations.create_index([("variantInternalId", 1)])
#client.beacon.genomicVariations.create_index([("variation.location.interval.start.value", 1)])
#client.beacon.genomicVariations.create_index([("variation.location.interval.end.value", 1)])
client.beacon.genomicVariations.create_index([("variation.location.interval.start.value", 1)])
client.beacon.genomicVariations.create_index([("variation.location.interval.end.value", 1)])
client.beacon.genomicVariations.create_index([("identifiers.genomicHGVSId", 1)])
#client.beacon.genomicVariations.create_index([("datasetId", 1), ("variation.location.interval.start.value", 1), ("variation.referenceBases", 1), ("variation.alternateBases", 1)])
client.beacon.genomicVariations.create_index([("molecularAttributes.geneIds", 1), ("variation.variantType", 1)])
client.beacon.caseLevelData.create_index([("id", 1), ("datasetId", 1)])
client.beacon.caseLevelData.create_index([("datasetId", 1)])
#client.beacon.individuals.create_index([("$**", "text")])
#client.beacon.runs.create_index([("$**", "text")])
#collection_name = client.beacon.analyses
#print(collection_name.index_information())

