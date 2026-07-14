from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_client() -> Engine:
    connection_string = (
        "postgresql+psycopg2://"
        "postgres:your_secure_password@localhost:5432/beacon"
    )

    return create_engine(
        connection_string,
        pool_pre_ping=True,
        echo=False,
    )