#### Input and Output files config parameters ####
csv_folder = './csv/examples/test/'
output_docs_folder='./output_docs/'
entry_type='all'

#### VCF Conversion config parameters ####
only_process_reads_with_allele_frequency=True
populations_by_allele_counts=True # Variable to choose if allele frequencies are to be read by single allele or by the whole genotype of the individual, if True the populations.json fields of Homozygous, Heterozygous and Hemizygous counts will be alleleCount, if False, genotype.
reference_genome='GRCh37' # Choose one between NCBI36, GRCh37, GRCh38
datasetId='test'
case_level_data=False
num_rows=15000000
verbosity=False # This variable, if True, will make the program run slower but give logs about all the skipped variants and the reason why.

### Update record ###
record_type='genomicVariation' # One between analysis, biosample, cohort, dataset, genomicVariation, individual or run
collection_name='genomicVariations'

### MongoDB parameters ###
database_host = 'mongo'
database_port = 27017
database_user = 'root'
database_password = 'example'
database_name = 'beacon'
database_auth_source = 'admin'