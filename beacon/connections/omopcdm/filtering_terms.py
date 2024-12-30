from beacon.connections.omopcdm.__init__ import client
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams

import aiosql
from pathlib import Path
queries_file = Path(__file__).parent / "sql" / "filteringTerms.sql"
filteringTerms_queries = aiosql.from_path(queries_file, "psycopg2")

def get_filtering_terms_of_individual(entry_id: Optional[str], qparams: RequestParams):
    schema = DefaultSchemas.FILTERINGTERMS

    indFilters = [filteringTerms_queries.sql_filtering_terms_race_gender(client),
                    filteringTerms_queries.sql_filtering_terms_condition(client),
                    filteringTerms_queries.sql_filtering_terms_measurement(client),
                    filteringTerms_queries.sql_filtering_terms_procedure(client),
                    filteringTerms_queries.sql_filtering_terms_observation(client),
                    filteringTerms_queries.sql_filtering_terms_drug_exposure(client)]
    finalIndFilters = []
    for ind_filters in indFilters:
        for filters in ind_filters:
            if filters[0].endswith("OMOP generated"):
                continue
            dict_filter = {"id":filters[0],"label":filters[1],"scopes":["individual"],"type":"ontology"}
            finalIndFilters.append(dict_filter)
    return len(finalIndFilters), finalIndFilters



def get_filtering_terms_of_biosample(entry_id: Optional[str], qparams: RequestParams):
    schema = DefaultSchemas.FILTERINGTERMS
    bio_filters = filteringTerms_queries.sql_filtering_terms_biosample(client)
    l_bioFilters = []
    for filters in bio_filters:
        dict_filter = {"id":filters[0],"label":filters[1],"scopes":["biosample"],"type":"ontology"}
        l_bioFilters.append(dict_filter)
    return len(l_bioFilters), l_bioFilters


def get_filtering_terms(self, qparams: RequestParams):

    schema = DefaultSchemas.FILTERINGTERMS
    indCount, indDocs = get_filtering_terms_of_individual(None, None)
    bioCount, bioDocs = get_filtering_terms_of_biosample(None, None)

    return schema, indCount + bioCount, indDocs + bioDocs