import asyncio
from beacon.exceptions.exceptions import DatabaseIsDown

async def ping_database(client):
    try:
        return await asyncio.to_thread(client.admin.command, "ping")
    except TimeoutError as e:
        raise DatabaseIsDown(str(e))
    except Exception as e:
        raise DatabaseIsDown(str(e))