from dotenv import load_dotenv
import os
import glob

database_cluster = False
use_env_file = False # If true, create a conf.env file in this same folder with the same variables that appear below and set their values there.

if use_env_file == False:
    database_host = 'mongo' #'host.docker.internal'
    database_port = 27017
    database_user = 'root'
    database_password = 'example'
    database_name = 'beacon'
    database_auth_source = 'admin'
    database_certificate = ''
    database_cafile = ''
elif use_env_file == True:
    mongo_conf = "beacon/connections/mongo/conf.env"
    load_dotenv(mongo_conf, override=True)

    database_host = os.getenv('database_host')
    database_port = os.getenv('database_port')
    database_user = os.getenv('database_user')
    database_password = os.getenv('database_password')
    database_name = os.getenv('database_name')
    database_auth_source = os.getenv('database_auth_source')
    database_certificate = os.getenv('database_certificate')
    database_cafile = os.getenv('database_cafile')