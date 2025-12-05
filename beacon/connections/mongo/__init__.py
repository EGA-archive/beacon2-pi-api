from pymongo.mongo_client import MongoClient
from beacon.connections.mongo import conf
from beacon.conf.conf import query_budget_database, query_budget_db_name, query_budget_table
import aiohttp.web as web
from beacon.exceptions.exceptions import DatabaseIsDown

try:
    if conf.database_cluster:
        uri = "mongodb+srv://{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
            conf.database_host
        )
    else:
        uri = "mongodb://{}:{}/{}?authSource={}".format(
            conf.database_host,
            conf.database_port,
            conf.database_name,
            conf.database_auth_source
        )

    if conf.database_certificate != '' and conf.database_cafile != '':
        uri += '&tls=true&tlsCertificateKeyFile={}&tlsCAFile={}'.format(conf.database_certificate, conf.database_cafile)

    client = MongoClient(uri, username=conf.database_user, password=conf.database_password)
except Exception as e:
    raise DatabaseIsDown(str(e))

# Mongo dbname
dbname='beacon'

# Collections clients
analyses=client[dbname].analyses
biosamples=client[dbname].biosamples
cohorts=client[dbname].cohorts
datasets=client[dbname].datasets
genomicVariations=client[dbname].genomicVariations
individuals=client[dbname].individuals
runs=client[dbname].runs

collections=client[dbname].collections
imagestudies=client[dbname].imagestudies
patients=client[dbname].patients

filtering_terms=client[dbname].filtering_terms
caseLevelData=client[dbname].caseLevelData
targets=client[dbname].targets
synonyms=client[dbname].synonyms
similarities=client[dbname].similarities
counts=client[dbname].counts

if query_budget_database == 'mongo':
    try:
        client[query_budget_db_name].validate_collection(query_budget_table)
    except Exception:
        try:
            db=client[query_budget_db_name].create_collection(name=query_budget_table)
        except Exception as e:
            pass
