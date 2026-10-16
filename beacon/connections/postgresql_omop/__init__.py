from beacon.connections.postgresql_omop.client import get_client
import sqlalchemy
from sqlalchemy import MetaData, Table
import logging

LOG = logging.getLogger(__name__)

client = get_client()
meta   = MetaData()

def get_table(name, schema=None):
    key = f"{schema}.{name}" if schema else name
    return meta.tables[key]

async def initialize():
    async with client.begin() as conn:
        LOG.info("CONNECTED")
        
        def load(sync_conn):
            LOG.info("REFLECTING")
            for table in (
                "specimen",
                "cohort_definition",
                "cohort",
                "person",
                "location",
                "condition_occurrence",
                "procedure_occurrence",
                "drug_exposure",
                "measurement",
                "observation",
                "observation_period",
            ):
                Table(
                    table,
                    meta,
                    autoload_with=sync_conn,
                    schema="cdm",
                )
            for table in (
                "concept",
                "concept_ancestor",
            ):
                Table(
                    table,
                    meta,
                    autoload_with=sync_conn,
                    schema="vocabularies",
                )

        await conn.run_sync(load)