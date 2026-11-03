import asyncio
import json
import os

import aio_pika

from beacon.connections.mongo.client import get_client


RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://audit_user:audit_password@rabbitmq:5672/",
)


async def main():
    client = get_client()

    db = client["beacon"]
    collection = db["events"]

    await asyncio.to_thread(client.admin.command, "ping")
    print("MongoDB connected", flush=True)

    rabbit = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await rabbit.channel()

    await channel.set_qos(prefetch_count=100)

    queue = await channel.declare_queue(
        "audit_queue",
        durable=True,
    )

    print("Audit consumer started", flush=True)

    async with queue.iterator() as messages:
        async for message in messages:
            print(
                f"Received message: {message.body!r}",
                flush=True,
            )

            try:
                event = json.loads(message.body)

                print(f"Inserting event: {event}", flush=True)

                result = await asyncio.to_thread(
                    collection.insert_one,
                    event,
                )

                print(
                    f"Inserted MongoDB document: {result.inserted_id}",
                    flush=True,
                )

                await message.ack()

            except Exception as exc:
                print(
                    f"Failed processing message: {exc!r}",
                    flush=True,
                )
                await message.nack(requeue=False)



if __name__ == "__main__":
    asyncio.run(main())
