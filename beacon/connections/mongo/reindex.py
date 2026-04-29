from beacon.connections.mongo.client import get_client

def reindex_database():
    client=get_client()
    genomicVariations=client['beacon'].genomicVariations
    caseLevelData=client['beacon'].caseLevelData
    try:
        client['beacon'].validate_collection("synonyms")
    except Exception:
        db=client['beacon'].create_collection(name="synonyms")
    try:
        client['beacon'].validate_collection("targets")
    except Exception:
        db=client['beacon'].create_collection(name="targets")
    try:
        client['beacon'].validate_collection("caseLevelData")
    except Exception:
        db=client['beacon'].create_collection(name="caseLevelData")
    try:
        client['beacon'].drop_collection("counts")
        client['beacon'].create_collection(name="counts")
    except Exception:
        client['beacon'].create_collection(name="counts")
    try:
        client['beacon'].validate_collection("similarities")
    except Exception:
        db=client['beacon'].create_collection(name="similarities")

    genomicVariations.create_index([("variation.location.interval.start.value", 1),("variation.location.interval.end.value", 1)]) # for range queries
    genomicVariations.create_index([("length", 1)]) # for range queries
    genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1)]) # for sequence queries
    genomicVariations.create_index([("datasetId", 1)]) # splits all the docs into datasets faster
    genomicVariations.create_index([("variation.location.interval.end.value", 1)])
    genomicVariations.create_index([("identifiers.genomicHGVSId", 1)])
    genomicVariations.create_index([("molecularAttributes.geneIds", 1), ("variation.variantType", 1)])
    caseLevelData.create_index([("id", 1), ("datasetId", 1)])
    caseLevelData.create_index([("datasetId", 1)])

if __name__ == '__main__':
    reindex_database()