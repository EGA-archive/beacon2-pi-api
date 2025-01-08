from beacon.connections.omopcdm.__init__ import client
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import itertools
import aiosql
from pathlib import Path

queries_file = Path(__file__).parent / "sql" / "basic_queries.sql"
basic_queries = aiosql.from_path(queries_file, "psycopg2")

# Function to know if generator is empty
def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first, itertools.chain([first], iterable)

# Query executor
def queryExecutor(query):
    cur = client.cursor()
    cur.execute(query)
    records = cur.fetchall()
    return records

# Check if a materialised view exists in the given the R/W permissions
def materialised_view_exists():

    query = """
        SELECT count(*)
        FROM pg_matviews
        WHERE matviewname = 'search_ontologies_view';
    """
    result = queryExecutor(query)
    return result[0][0] > 0

def search_ontology(concept_id, matView):
    if matView:
        records = basic_queries.sql_get_ontology_view(client, concept_id=concept_id)
    else:
        records = basic_queries.sql_get_ontology(client, concept_id=concept_id)
    return records

@log_with_args(level)
def search_ontologies(self, dictValues, matView):
    for person_id, listVariableValues in dictValues.items():    # For each id
        for dictVariableValue in listVariableValues:                        # For each object of the list   
            for variable, value in dictVariableValue.items():                                     
                # If id in variable, extract the label and OntologyId
                if "concept_id" in variable:
                    if value == 0:
                        dictVariableValue[variable] = {'id':"None:No matching concept", 'label':"No matching concept"}
                        continue
                    records = search_ontology(value, matView)
                    if records:
                        label = records[0]
                        id = records[1]
                    else:
                        label = "No matching concept"
                        id = "None:No matching concept"
                    dictVariableValue[variable] = {'id':id, 'label':label}
    return dictValues