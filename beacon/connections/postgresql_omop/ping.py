from sqlalchemy import exc
from beacon.exceptions.exceptions import DatabaseIsDown

async def ping_databse(client):
    try:
        with client.connect() as connection:
            await connection.execute("SELECT 1")
            return "connection successful"
    except exc.TimeoutError as e:
        raise DatabaseIsDown(f"Timeout error: {str(e)}")
    except exc.SQLAlchemyError as e:
        raise DatabaseIsDown(f"Database is down: {str(e)}")
    except Exception as e:
        raise DatabaseIsDown(f"An unexpected error occurred: {str(e)}")

