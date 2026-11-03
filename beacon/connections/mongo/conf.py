from dotenv import load_dotenv
import os

mongo_conf = "beacon/connections/mongo/conf.env"
load_dotenv(mongo_conf, override=True)

database_host = os.getenv('database_host', 'mongo')
database_port = os.getenv('database_port', str(27017))
database_user = os.getenv('database_user', 'root')
database_password = os.getenv('database_password', 'example')
database_name = os.getenv('database_name', 'beacon')
database_auth_source = os.getenv('database_auth_source', 'admin')
database_certificate = os.getenv('database_certificate', '')
database_cafile = os.getenv('database_cafile', '')
database_cluster = False

# Connection pool and timeout tuning for the shared MongoClient.
# These are passed straight to pymongo.MongoClient, so the names match pymongo's.
database_max_pool_size = int(os.getenv('database_max_pool_size', str(100)))
database_min_pool_size = int(os.getenv('database_min_pool_size', str(0)))
database_server_selection_timeout_ms = int(os.getenv('database_server_selection_timeout_ms', str(5000)))
database_connect_timeout_ms = int(os.getenv('database_connect_timeout_ms', str(5000)))
