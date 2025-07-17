from beacon.connections.mongo.__init__ import client, dbname, genomicVariations, caseLevelData, individuals, analyses, biosamples, cohorts, datasets, runs, targets

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

genomicVariations.create_index([("length", 1), ("variation.location.interval.start.value", 1),("variation.location.interval.end.value", 1)]) # for range queries
#genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1)]) # for sequence queries
genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1), ("datasetId", 1)], unique=True) # for sequence queries
genomicVariations.create_index([("datasetId", 1)]) # splits all the docs into datasets faster
genomicVariations.create_index([("variantInternalId", 1)]) # enables the g_variants/{id}/endpoint query to do it faster
genomicVariations.create_index([("identifiers.genomicHGVSId", 1)])
genomicVariations.create_index([("molecularAttributes.geneIds", 1), ("variation.variantType", 1)])
caseLevelData.create_index([("id", 1), ("datasetId", 1)], unique=True)
caseLevelData.create_index([("datasetId", 1)])
individuals.create_index([("id", 1), ("datasetId", 1)], unique=True)
biosamples.create_index([("id", 1), ("datasetId", 1)], unique=True)
analyses.create_index([("id", 1), ("datasetId", 1)], unique=True)
cohorts.create_index([("id", 1), ("datasetId", 1)], unique=True)
runs.create_index([("id", 1), ("datasetId", 1)], unique=True)
datasets.create_index([("id", 1), ("datasetId", 1)], unique=True)
targets.create_index([("datasetId", 1)], unique=True)