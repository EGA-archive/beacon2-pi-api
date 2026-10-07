from beacon.connections.mongo.client import get_client

def reindex_database():
    client = get_client()
    db = client['beacon']
    genomicVariations = db.genomicVariations
    caseLevelData = db.caseLevelData
    # Existence check: fast, no lock, works with readWrite.
    existing = set(db.list_collection_names())
    for name in ("synonyms", "targets", "caseLevelData", "similarities"):
        if name not in existing:
            db.create_collection(name=name)

    # Reset cached counts; drop_collection is a no-op if it doesn't exist.
    # Let permission and other database errors propagate.
    db.drop_collection("counts")
    db.create_collection(name="counts")

    genomicVariations.create_index([("variation.location.interval.start.value", 1),("variation.location.interval.end.value", 1)]) # index needed for range queries
    genomicVariations.create_index([("length", 1)]) # index needed for range queries
    genomicVariations.create_index([("variation.alternateBases", 1),("variation.referenceBases", 1),("variation.location.interval.start.value", 1), ("variation.location.interval.end.value", 1)]) # index needed for sequence type queries
    genomicVariations.create_index([("datasetId", 1)]) # splits all the docs into datasets faster
    genomicVariations.create_index([("variation.location.interval.end.value", 1)]) # index needed for bracket queries
    genomicVariations.create_index([("identifiers.genomicHGVSId", 1)])
    genomicVariations.create_index([("molecularAttributes.geneIds", 1), ("variation.variantType", 1)])
    genomicVariations.create_index([("frequencyInPopulations.frequencies.alleleFrequency", 1)])
    caseLevelData.create_index([("id", 1), ("datasetId", 1)])
    caseLevelData.create_index([("datasetId", 1)])

if __name__ == '__main__':
    reindex_database()