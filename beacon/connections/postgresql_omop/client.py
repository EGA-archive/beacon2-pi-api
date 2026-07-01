import sqlalchemy
from sqlalchemy import create_engine, MetaData, URL
from beacon.connections.postgresql_omop import conf


def get_client(table_name = None):
    url_object = URL.create(
        "postgresql+psycopg2",
        username = conf.database_user,
        password = conf.database_password,
        host     = conf.database_host,
        port     = conf.database_port,
        database = conf.database_name,
    )

    client = create_engine(url_object, pool_pre_ping = True)

    if table_name is not None:
        if table_name not in ['specimen', 'cohort_definition', 'cohort', 'person', 'location', 'condition_occurrence', 'procedure_occurrence', 'drug_exposure', 'measurement', 'observation', 'observation_period', 'concept', 'concept_ancestor']:
            raise ValueError(f"Table '{table_name}' is not a valid table name.")
        
        __meta__ = MetaData()
        __meta__.reflect(bind = client)

        table = sqlalchemy.Table(table_name, __meta__, autoload_with = client)

        return table
    else:
        return client
