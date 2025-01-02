from beacon.connections.omopcdm.__init__ import client
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

def search_ontology(concept_id):
    records = basic_queries.sql_get_ontology(client, concept_id=concept_id)
    return records


def search_ontologies(dictValues):
    for person_id, listVariableValues in dictValues.items():    # For each id
        for dictVariableValue in listVariableValues:                        # For each object of the list   
            for variable, value in dictVariableValue.items():                                     
                # If id in variable, extract the label and OntologyId
                if "concept_id" in variable:
                    if value == 0:
                        dictVariableValue[variable] = {'id':"None:No matching concept", 'label':"No matching concept"}
                        continue
                    records = search_ontology(value)
                    if records:
                        label = records[0]
                        id = records[1]
                    else:
                        label = "No matching concept"
                        id = "None:No matching concept"
                    dictVariableValue[variable] = {'id':id, 'label':label}
    return dictValues