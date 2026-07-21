import asyncio

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from beacon.exceptions.exceptions import DatabaseIsDown


# Merge the function in the client script
async def ping_database(client):
    try:
        def _ping():
            with client.connect() as connection:
                connection.execute(text("SELECT 1"))

        await asyncio.to_thread(_ping)
        return {"ok": 1}

    except SQLAlchemyError as e:
        raise DatabaseIsDown(str(e))
    except Exception as e:
        raise DatabaseIsDown(str(e))