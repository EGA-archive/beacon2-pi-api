from pymongo.mongo_client import MongoClient
from beacon.connections.mongo import conf
from beacon.connections.mongo.ping import ping_database
from beacon.conf.conf_override import config
import aiohttp.web as web
from beacon.exceptions.exceptions import DatabaseIsDown
import asyncio
import threading

# A MongoClient is thread-safe and maintains its own connection pool, so a single
# instance can be shared by every caller. Building one per call costs a TCP
# connect, a SCRAM handshake and a topology discovery on every request, so the
# clients are memoised here by connection URI. They are created lazily (never at
# import time) so that a pre-forking server would get a client per worker.
_CLIENTS = {}
_CLIENTS_LOCK = threading.Lock()

def get_client():
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

    # Return the already built client for this URI, if there is one.
    client = _CLIENTS.get(uri)
    if client is not None:
        return client

    with _CLIENTS_LOCK:
        # Another thread may have built it while this one waited for the lock.
        client = _CLIENTS.get(uri)
        if client is None:
            client = MongoClient(
                uri,
                username=conf.database_user,
                password=conf.database_password,
                maxPoolSize=conf.database_max_pool_size,
                minPoolSize=conf.database_min_pool_size,
                serverSelectionTimeoutMS=conf.database_server_selection_timeout_ms,
                connectTimeoutMS=conf.database_connect_timeout_ms,
            )
            _CLIENTS[uri] = client

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


