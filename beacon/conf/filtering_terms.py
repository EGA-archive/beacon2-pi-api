# Add all the filters allowed to be used in case the ontology pair for it doesn't exist (direct alphanumeric terms inserted, not from the ontology terms)
database='mongo'
alphanumeric_terms_runs = ['libraryStrategy']
alphanumeric_terms_analyses = ['variantCaller']
alphanumeric_terms_g_variants = ['molecularAttributes.geneIds', 'molecularAttributes.aminoacidChanges']
alphanumeric_terms_individuals = ['diseases.ageOfOnset.iso8601duration','phenotypicFeatures.onset.iso8601duration', 'exposures.ageAtExposure.iso8601duration', 'treatments.ageAtOnset.iso8601duration']
alphanumeric_terms_biosamples = ['diseases.ageOfOnset.iso8601duration','phenotypicFeatures.onset.iso8601duration', 'exposures.ageAtExposure.iso8601duration', 'treatments.ageAtOnset.iso8601duration']
alphanumeric_terms_datasets = []
alphanumeric_terms_cohorts = []

alphanumeric_terms = ['imageStudy.disease.tumorMetadata.PSA']