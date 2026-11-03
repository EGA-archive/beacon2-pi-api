#### Input and Output files config parameters ####
csv_folder = './csv/examples/'
output_docs_folder='./output_docs/'
entry_type='all'

#### VCF Conversion config parameters ####
only_process_reads_with_allele_frequency=True
populations_by_allele_counts=True # Variable to choose if allele frequencies are to be read by single allele or by the whole genotype of the individual, if True the populations.json fields of Homozygous, Heterozygous and Hemizygous counts will be alleleCount, if False, genotype.
datasetId='test'
case_level_data=False
num_rows=150000000
verbosity=False # This variable, if True, will make the program run slower but give logs about all the skipped variants and the reason why.
scan_and_delete_variants_before_processing=False# If True, all the existing variants in the database will be deleted before starting the VCF processing.

### Update record ###
record_type='genomicVariation' # One between analysis, biosample, cohort, dataset, genomicVariation, individual or run
collection_name='genomicVariations'

### MongoDB parameters ###
# Use `database_uri` for a full MongoDB connection string, including
# `mongodb+srv://...` cluster URIs. Leave it empty to keep the legacy
# host/port/user/password fields below.
database_uri = ''
database_host = 'mongo'
database_port = 27017
database_user = 'root'
database_password = 'example'
database_name = 'beacon'
database_auth_source = 'admin'