from pymongo.mongo_client import MongoClient
import conf
from beacon.connections.mongo.__init__ import client, dbname, filtering_terms, targets
import sys
import os


current = os.path.dirname(os.path.realpath(__file__))


parent = os.path.dirname(current)


sys.path.append(parent)

try:
    client[dbname].drop_collection("synonyms")
except Exception:
    client[dbname].create_collection(name="synonyms")
try:
    client[dbname].validate_collection("synonyms")
except Exception:
    db=client[dbname].create_collection(name="synonyms")
try:
    client[dbname].validate_collection("targets")
except Exception:
    db=client[dbname].create_collection(name="targets")
try:
    client[dbname].validate_collection("caseLevelData")
except Exception:
    db=client[dbname].create_collection(name="caseLevelData")
try:
    client[dbname].drop_collection("counts")
except Exception:
    client[dbname].create_collection(name="counts")
try:
    client[dbname].validate_collection("counts")
except Exception:
    db=client[dbname].create_collection(name="counts")
try:
    client[dbname].drop_collection("similarities")
except Exception:
    client[dbname].create_collection(name="similarities")
try:
    client[dbname].validate_collection("similarities")
except Exception:
    db=client[dbname].create_collection(name="similarities")
#client[dbname].analyses.create_index([("$**", "text")])
#client[dbname].biosamples.create_index([("$**", "text")])
#client[dbname].cohorts.create_index([("$**", "text")])
#client[dbname].datasets.create_index([("$**", "text")])
#client[dbname].genomicVariations.create_index([("$**", "text")])
#client[dbname].genomicVariations.create_index([("caseLevelData.biosampleId", 1)])
client[dbname].genomicVariations.create_index([("variation.location.interval.start.value", 1),("variation.location.interval.end.value", 1)])
client[dbname].genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1)])
client[dbname].genomicVariations.create_index([("datasetId", 1)])
#client[dbname].genomicVariations.create_index([("variantInternalId", 1)])
#client[dbname].genomicVariations.create_index([("variation.location.interval.start.value", 1)])
#client[dbname].genomicVariations.create_index([("variation.location.interval.end.value", 1)])
client[dbname].genomicVariations.create_index([("identifiers.genomicHGVSId", 1)])
#client[dbname].genomicVariations.create_index([("datasetId", 1), ("variation.location.interval.start.value", 1), ("variation.referenceBases", 1), ("variation.alternateBases", 1)])
client[dbname].genomicVariations.create_index([("molecularAttributes.geneIds", 1), ("variation.variantType", 1)])
client[dbname].caseLevelData.create_index([("id", 1), ("datasetId", 1)])
client[dbname].caseLevelData.create_index([("datasetId", 1)])
#client[dbname].individuals.create_index([("$**", "text")])
#client[dbname].runs.create_index([("$**", "text")])
#collection_name = client[dbname].analyses
#print(collection_name.index_information())

