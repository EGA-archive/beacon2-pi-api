from dotenv import load_dotenv
import os

mongo_conf = "beacon/connections/mongo/conf.env"
load_dotenv(mongo_conf, override=True)

database_host = os.getenv('database_host', 'mongo')
database_port = os.getenv('database_port', 27017)
database_user = os.getenv('database_user', 'root')
database_password = os.getenv('database_password', 'example')
database_name = os.getenv('database_name', 'beacon')
database_auth_source = os.getenv('database_auth_source', 'admin')
database_certificate = os.getenv('database_certificate', '')
database_cafile = os.getenv('database_cafile', '')
database_cluster = False