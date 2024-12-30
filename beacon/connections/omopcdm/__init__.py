from beacon.connections.omopcdm import conf
import psycopg2
import os
from beacon.logs.logs import log_with_args, LOG


# db_url = os.getenv('POSTGRES_URL', default="postgresql://pgadmin:admin@localhost:5432/omopdb")
uri = "postgresql://{}:{}@{}:{}/{}".format(
    conf.database_user,
    conf.database_password,
    conf.database_host, # Ex: localhost
    conf.database_port, # Ex: 5432
    conf.database_name,
)
# LOG.debug(f"URI {uri}")

client = psycopg2.connect(uri)

# CDM_SCHEMA='cdm'
# VOCABULARIES_SCHEMA='vocabularies'
# query = "select * from cdm.person limit 10"
# cur = client.cursor()
# cur.execute(query)
# records = cur.fetchall()
# listOfList = [str(record[0]) for record in records]
# LOG.debug(f"list of lissssssttttttt {listOfList}")
