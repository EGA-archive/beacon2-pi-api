from pymongo.mongo_client import MongoClient
from beacon.connections.mongo import conf
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.exceptions.exceptions import DatabaseIsDown
from beacon.connections.mongo.client import get_client

try:
    client=get_client()
except Exception as e:
    raise DatabaseIsDown(str(e))

# Mongo dbname
dbname = conf.database_name

# Collection clients initialized
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

if config.query_budget_database == 'mongo':
    try:
        client[config.query_budget_db_name].validate_collection(config.query_budget_table)
    except Exception:
        try:
            db=client[config.query_budget_db_name].create_collection(name=config.query_budget_table)
        except Exception as e:
            pass
