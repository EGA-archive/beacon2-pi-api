from pymongo.mongo_client import MongoClient
from beacon.connections.mongo import conf
from beacon.conf.conf_override import config
import threading
from pymongo import MongoClient
from beacon.connections.mongo import conf
import threading

_CLIENTS = {}
_CLIENTS_LOCK = threading.Lock()


def get_client():
    if conf.database_cluster:
        uri = (
            f"mongodb+srv://{conf.database_host}/"
            "?tls=true&authMechanism=SCRAM-SHA-256"
            "&retrywrites=false&maxIdleTimeMS=120000"
        )
    else:
        uri = (
            f"mongodb://{conf.database_host}:"
            f"{conf.database_port}/{conf.database_name}"
            f"?authSource={conf.database_auth_source}"
        )

    if conf.database_certificate and conf.database_cafile:
        uri += (
            f"&tls=true"
            f"&tlsCertificateKeyFile={conf.database_certificate}"
            f"&tlsCAFile={conf.database_cafile}"
        )

    # Include effective client settings in the cache key.
    key = (
        uri,
        conf.database_user,
        conf.database_max_pool_size,
        conf.database_min_pool_size,
        conf.database_server_selection_timeout_ms,
        conf.database_connect_timeout_ms,
    )

    with _CLIENTS_LOCK:
        client = _CLIENTS.get(key)

        if client is None:
            client = MongoClient(
                uri,
                username=conf.database_user,
                password=conf.database_password,
                maxPoolSize=conf.database_max_pool_size,
                minPoolSize=conf.database_min_pool_size,
                serverSelectionTimeoutMS=(
                    conf.database_server_selection_timeout_ms
                ),
                connectTimeoutMS=conf.database_connect_timeout_ms,
                waitQueueTimeoutMS=5000,
            )
            _CLIENTS[key] = client

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


