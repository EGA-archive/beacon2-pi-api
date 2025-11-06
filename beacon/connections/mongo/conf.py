from dotenv import load_dotenv
import os

mongo_conf = "beacon/connections/mongo/conf.env"
load_dotenv(mongo_conf, override=True)

database_host = ''.join(envar for envar in os.getenv('database_host', 'mongo') if envar.isalnum())
database_port = ''.join(envar for envar in os.getenv('database_port', str(27017)) if envar.isalnum())
database_user = ''.join(envar for envar in os.getenv('database_user', 'root') if envar.isalnum())
database_password = ''.join(envar for envar in os.getenv('database_password', 'example') if envar.isalnum())
database_name = ''.join(envar for envar in os.getenv('database_name', 'beacon') if envar.isalnum())
database_auth_source = ''.join(envar for envar in os.getenv('database_auth_source', 'admin') if envar.isalnum())
database_certificate = ''.join(envar for envar in os.getenv('database_certificate', '') if envar.isalnum())
database_cafile = ''.join(envar for envar in os.getenv('database_cafile', '') if envar.isalnum())
database_cluster = False