database='mongo'
alphanumeric_terms_runs = ['libraryStrategy']
alphanumeric_terms_analyses = ['variantCaller']
alphanumeric_terms_g_variants = ['molecularAttributes.geneIds', 'molecularAttributes.aminoacidChanges']
alphanumeric_terms_individuals = ['diseases.ageOfOnset.iso8601duration','phenotypicFeatures.onset.iso8601duration', 'exposures.ageAtExposure.iso8601duration', 'treatments.ageAtOnset.iso8601duration']
alphanumeric_terms_biosamples = ['diseases.ageOfOnset.iso8601duration','phenotypicFeatures.onset.iso8601duration', 'exposures.ageAtExposure.iso8601duration', 'treatments.ageAtOnset.iso8601duration']
alphanumeric_terms_datasets = []
alphanumeric_terms_cohorts = []

alphanumeric_terms = alphanumeric_terms_runs + alphanumeric_terms_analyses + alphanumeric_terms_g_variants + alphanumeric_terms_individuals + alphanumeric_terms_biosamples + alphanumeric_terms_datasets +alphanumeric_terms_cohorts