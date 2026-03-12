from pymongo.mongo_client import MongoClient
from beacon.connections.mongo import conf
from beacon.connections.mongo.ping import ping_database
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.exceptions.exceptions import DatabaseIsDown
import asyncio

async def get_client():
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
    await asyncio.wait_for(ping_database(client), timeout=1.0)
    return client

def create_budget():
    client=get_client()
    if config.query_budget_database == 'mongo':
        try:
            client[config.query_budget_db_name].validate_collection(config.query_budget_table)
        except Exception:
            try:
                db=client[config.query_budget_db_name].create_collection(name=config.query_budget_table)
            except Exception as e:
                pass


