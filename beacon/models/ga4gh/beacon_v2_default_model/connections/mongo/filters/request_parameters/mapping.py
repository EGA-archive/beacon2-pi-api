# Mapping of the name of the request parameter and the location inside the schema (mongoDB object)
VARIANTS_PROPERTY_MAP = {
    "start": "variation.location.interval.start.value",
    "end": "variation.location.interval.end.value",
    "assemblyId": "assemblyId",
    "referenceName": "identifiers.genomicHGVSId",
    "referenceBases": "variation.referenceBases",
    "alternateBases": "variation.alternateBases",
    "variantType": "variation.variantType",
    "variantMinLength": "variation.alternateBases",
    "variantMaxLength": "variation.alternateBases",
    "geneId": "molecularAttributes.geneIds",
    "genomicAlleleShortForm": "identifiers.genomicHGVSId",
    "aminoacidChange": "molecularAttributes.aminoacidChanges",
    "clinicalRelevance": "caseLevelData.clinicalInterpretations.clinicalRelevance",
    "mateName": "identifiers.genomicHGVSId",
    "requestProfileId": "requestProfileId"
}