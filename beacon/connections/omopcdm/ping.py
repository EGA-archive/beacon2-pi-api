from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure 
import conf
import os
from beacon.logs.logs import LOG


if conf.database_cluster:
    uri = "mongodb+srv://{}:{}@{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
        conf.database_user,
        conf.database_password,
        conf.database_host
    )
else:
    uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
        conf.database_user,
        conf.database_password,
        conf.database_host,
        conf.database_port,
        conf.database_name,
        conf.database_auth_source
    )

if os.path.isfile(conf.database_certificate):
    uri += '&tls=true&tlsCertificateKeyFile={}'.format(conf.database_certificate)
    if os.path.isfile(conf.database_cafile):
        uri += '&tlsCAFile={}'.format(conf.database_cafile)

client = MongoClient(uri, serverSelectionTimeoutMS=30000)
try:
    client.admin.command('ping')
except ConnectionFailure as err:
    LOG.debug(f"Database error encountered: {err}")