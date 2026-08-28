from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from beacon.connections.postgresql_omop import conf

def get_client():
    url_object = URL.create(
        conf.database_driver,
        username = conf.database_user,
        password = conf.database_password,
        host     = conf.database_host,
        port     = conf.database_port,
        database = conf.database_name,
    )

    client = create_async_engine(url_object, pool_pre_ping = True)
    
    return client