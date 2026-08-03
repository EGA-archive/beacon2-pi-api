from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from beacon.connections.sqlalchemy_postgresql import conf

def get_client() -> Engine:
    connection_string = (
        "postgresql+psycopg2://"
        "{}:{}@{}:{}/{}".format(conf.database_user, conf.database_password, conf.database_host, conf.database_port, conf.database_name)
    )

    return create_engine(
        connection_string,
        pool_pre_ping=True,
        echo=False,
    )