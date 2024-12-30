from beacon.connections.omopcdm import conf
import psycopg2
import os
from beacon.logs.logs import log_with_args, LOG


uri = "postgresql://{}:{}@{}:{}/{}".format(
    conf.database_user,
    conf.database_password,
    conf.database_host, # Ex: localhost
    conf.database_port, # Ex: 5432
    conf.database_name,
)

client = psycopg2.connect(uri)